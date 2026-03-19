from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Libro(db.Model):
    __tablename__ = 'libros'
    id         = db.Column(db.Integer, primary_key=True)
    titulo     = db.Column(db.String(200), nullable=False)
    autor      = db.Column(db.String(150), nullable=False)
    disponible = db.Column(db.Boolean, default=True)
    prestamos  = db.relationship('Prestamo', backref='libro', lazy=True)

    def __repr__(self):
        return f'<Libro {self.titulo}>'


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id        = db.Column(db.Integer, primary_key=True)
    nombre    = db.Column(db.String(150), nullable=False)
    email     = db.Column(db.String(150), unique=True, nullable=False)
    password  = db.Column(db.String(256), nullable=False)
    rol       = db.Column(db.String(20), default='usuario')  # 'usuario' o 'bibliotecario'
    prestamos = db.relationship('Prestamo', backref='usuario', lazy=True)

    def __repr__(self):
        return f'<Usuario {self.nombre}>'


class Prestamo(db.Model):
    __tablename__ = 'prestamos'
    id                = db.Column(db.Integer, primary_key=True)
    libro_id          = db.Column(db.Integer, db.ForeignKey('libros.id'), nullable=False)
    usuario_id        = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_inicio      = db.Column(db.Date, nullable=False)
    fecha_devolucion  = db.Column(db.Date, nullable=True)
    estado            = db.Column(db.String(20), default='activo')  # 'activo' o 'finalizado'
    sancion           = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f'<Prestamo libro={self.libro_id} usuario={self.usuario_id}>'