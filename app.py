from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Libro, Usuario, Prestamo
from datetime import date
import hashlib

app = Flask(__name__)
app.secret_key = 'biblioteca_secret_key_2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ── Utilidad ──────────────────────────────────────────────
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ── Inicializar BD con datos de prueba ────────────────────
def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        if not Usuario.query.first():
            admin = Usuario(nombre='Bibliotecario Admin', email='admin@biblioteca.com',
                            password=hash_password('admin123'), rol='bibliotecario')
            user1 = Usuario(nombre='Samuel Florez', email='samuel@biblioteca.com',
                            password=hash_password('user123'), rol='usuario')
            db.session.add_all([admin, user1])
            libros = [
                Libro(titulo='Cien años de soledad', autor='Gabriel García Márquez', disponible=True),
                Libro(titulo='El principito',         autor='Antoine de Saint-Exupéry', disponible=True),
                Libro(titulo='1984',                  autor='George Orwell',           disponible=True),
                Libro(titulo='Don Quijote',           autor='Miguel de Cervantes',     disponible=True),
                Libro(titulo='Sapiens',               autor='Yuval Noah Harari',       disponible=True),
            ]
            db.session.add_all(libros)
            db.session.commit()

# ── Rutas de Autenticación ────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email']
        password = hash_password(request.form['password'])
        usuario  = Usuario.query.filter_by(email=email, password=password).first()
        if usuario:
            session['usuario_id']     = usuario.id
            session['usuario_nombre'] = usuario.nombre
            session['rol']            = usuario.rol
            return redirect(url_for('catalogo'))
        flash('Credenciales incorrectas', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── RF-1: Catálogo ────────────────────────────────────────
@app.route('/catalogo')
def catalogo():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    busqueda = request.args.get('q', '')
    if busqueda:
        libros = Libro.query.filter(
            (Libro.titulo.ilike(f'%{busqueda}%')) |
            (Libro.autor.ilike(f'%{busqueda}%'))
        ).all()
    else:
        libros = Libro.query.all()
    return render_template('catalogo.html', libros=libros, busqueda=busqueda)

# ── RF-2 / RF-4: Solicitar préstamo ──────────────────────
@app.route('/prestamo/nuevo/<int:libro_id>', methods=['POST'])
def nuevo_prestamo(libro_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    libro = Libro.query.get_or_404(libro_id)
    if not libro.disponible:
        flash('El libro no está disponible.', 'warning')
        return redirect(url_for('catalogo'))
    prestamo = Prestamo(
        libro_id    = libro.id,
        usuario_id  = session['usuario_id'],
        fecha_inicio= date.today(),
        estado      = 'activo'
    )
    libro.disponible = False  # RF-8: actualización automática
    db.session.add(prestamo)
    db.session.commit()
    flash(f'Préstamo de "{libro.titulo}" registrado exitosamente.', 'success')
    return redirect(url_for('catalogo'))

# ── RF-5: Registrar devolución ────────────────────────────
@app.route('/prestamo/devolver/<int:prestamo_id>', methods=['POST'])
def devolver(prestamo_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    prestamo = Prestamo.query.get_or_404(prestamo_id)
    prestamo.fecha_devolucion = date.today()
    prestamo.estado           = 'finalizado'
    prestamo.libro.disponible = True  # RF-8: actualización automática
    db.session.commit()
    flash('Devolución registrada correctamente.', 'success')
    return redirect(url_for('prestamos'))

# ── RF-3: Historial personal ──────────────────────────────
@app.route('/historial')
def historial():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    mis_prestamos = Prestamo.query.filter_by(usuario_id=session['usuario_id']).all()
    return render_template('historial.html', prestamos=mis_prestamos)

# ── Panel préstamos activos (bibliotecario) ───────────────
@app.route('/prestamos')
def prestamos():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    if session['rol'] != 'bibliotecario':
        flash('Acceso restringido.', 'danger')
        return redirect(url_for('catalogo'))
    todos = Prestamo.query.filter_by(estado='activo').all()
    return render_template('prestamos.html', prestamos=todos)

# ── RF-6: Gestión de libros ───────────────────────────────
@app.route('/admin/libros', methods=['GET', 'POST'])
def admin_libros():
    if 'usuario_id' not in session or session['rol'] != 'bibliotecario':
        flash('Acceso restringido.', 'danger')
        return redirect(url_for('catalogo'))
    if request.method == 'POST':
        libro = Libro(
            titulo     = request.form['titulo'],
            autor      = request.form['autor'],
            disponible = True
        )
        db.session.add(libro)
        db.session.commit()
        flash('Libro agregado al catálogo.', 'success')
    libros = Libro.query.all()
    return render_template('admin_libros.html', libros=libros)

# ── RF-7: Registrar sanciones ─────────────────────────────
@app.route('/sancion/<int:prestamo_id>', methods=['POST'])
def registrar_sancion(prestamo_id):
    if 'usuario_id' not in session or session['rol'] != 'bibliotecario':
        return redirect(url_for('login'))
    prestamo = Prestamo.query.get_or_404(prestamo_id)
    prestamo.sancion = request.form.get('motivo', 'Retraso en devolución')
    db.session.commit()
    flash('Sanción registrada.', 'warning')
    return redirect(url_for('prestamos'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)