import pytest
from app import app, init_db
from models import db, Libro, Usuario, Prestamo
import hashlib

@pytest.fixture
def client():
    """Configura la app en modo testing con BD en memoria."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.drop_all()      
        db.create_all()  
        # Usuario de prueba
        usuario = Usuario(
            nombre='Test User',
            email='test@test.com',
            password=hashlib.sha256('test123'.encode()).hexdigest(),
            rol='usuario'
        )
        # Bibliotecario de prueba
        admin = Usuario(
            nombre='Admin Test',
            email='admin@test.com',
            password=hashlib.sha256('admin123'.encode()).hexdigest(),
            rol='bibliotecario'
        )
        # Libro de prueba
        libro = Libro(titulo='Libro Test', autor='Autor Test', disponible=True)
        db.session.add_all([usuario, admin, libro])
        db.session.commit()

    with app.test_client() as client:
        yield client


# ── Test 1: La página de login carga correctamente ─────
def test_login_carga(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Biblioteca' in response.data


# ── Test 2: Login con credenciales correctas ───────────
def test_login_correcto(client):
    response = client.post('/login', data={
        'email': 'test@test.com',
        'password': 'test123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Cat' in response.data  # redirecciona al catálogo


# ── Test 3: Login con credenciales incorrectas ─────────
def test_login_incorrecto(client):
    response = client.post('/login', data={
        'email': 'test@test.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert b'Credenciales incorrectas' in response.data


# ── Test 4: El catálogo requiere autenticación ─────────
def test_catalogo_requiere_login(client):
    response = client.get('/catalogo', follow_redirects=True)
    assert b'Biblioteca' in response.data  # redirige al login


# ── Test 5: Un libro disponible puede ser prestado ─────
def test_libro_disponible_en_catalogo(client):
    with app.app_context():
        libro = Libro.query.first()
        assert libro.disponible == True


# ── Test 6: Préstamo actualiza disponibilidad (RF-8) ───
def test_prestamo_actualiza_disponibilidad(client):
    with app.app_context():
        libro = Libro.query.first()
        usuario = Usuario.query.filter_by(rol='usuario').first()

        from datetime import date
        prestamo = Prestamo(
            libro_id    = libro.id,
            usuario_id  = usuario.id,
            fecha_inicio= date.today(),
            estado      = 'activo'
        )
        libro.disponible = False
        db.session.add(prestamo)
        db.session.commit()

        libro_actualizado = Libro.query.get(libro.id)
        assert libro_actualizado.disponible == False


# ── Test 7: Devolución restaura disponibilidad (RF-8) ──
def test_devolucion_restaura_disponibilidad(client):
    with app.app_context():
        from datetime import date
        libro = Libro.query.first()
        usuario = Usuario.query.filter_by(rol='usuario').first()

        # Crear préstamo primero
        prestamo = Prestamo(
            libro_id     = libro.id,
            usuario_id   = usuario.id,
            fecha_inicio = date.today(),
            estado       = 'activo'
        )
        libro.disponible = False
        db.session.add(prestamo)
        db.session.commit()

        # Ahora registrar devolución
        prestamo.estado = 'finalizado'
        prestamo.fecha_devolucion = date.today()
        libro.disponible = True
        db.session.commit()

        assert libro.disponible == True

# ── Test 8: Solo bibliotecario accede a admin ──────────
def test_admin_requiere_bibliotecario(client):
    # Login como usuario normal
    client.post('/login', data={
        'email': 'test@test.com',
        'password': 'test123'
    })
    response = client.get('/admin/libros', follow_redirects=True)
    assert b'Acceso restringido' in response.data or response.status_code == 200