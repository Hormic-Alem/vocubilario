from flask import Flask, render_template, redirect, url_for, request, session
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'mysecretkey'  # Cambia esto en producción
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Bootstrap(app)
db = SQLAlchemy(app)

# Modelo de Usuarios
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

# Modelo de Vocabulario
class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)  # La palabra en el idioma original
    translation = db.Column(db.String(100), nullable=False)  # La traducción al idioma destino
    level = db.Column(db.String(50))  # Ejemplo: 'Principiante', 'Intermedio', 'Avanzado'
    topic = db.Column(db.String(100))  # Ejemplo: 'Colores', 'Familia'

# Crear la base de datos
with app.app_context():
    db.create_all()

def add_default_admin():
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", password="admin123", is_admin=True)
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username, password=password).first()
    if user:
        session['username'] = username
        return redirect(url_for('home'))
    else:
        return render_template('login.html', error="Usuario o contraseña incorrectos.")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not User.query.filter_by(username=username).first():
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return "Usuario ya registrado."

    return render_template('register.html')

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('home.html')

@app.route('/area/<area>')
def area(area):
    if 'username' not in session:
        return redirect(url_for('index'))

    words = Word.query.filter_by(topic=area).all()
    return render_template('area.html', area=area, words=words)

@app.route('/quick_trainer')
def quick_trainer():
    if 'username' not in session:
        return redirect(url_for('index'))

    from random import choice
    words = Word.query.all()
    random_word = choice(words)

    return render_template('quick_trainer.html', word=random_word.word, translation=random_word.translation)

@app.route('/add_word', methods=['GET', 'POST'])
def add_word():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    current_user = User.query.filter_by(username=session['username']).first()
    if not current_user or not current_user.is_admin:
        return "Acceso denegado. No tienes permisos para agregar palabras."
    
    if request.method == 'POST':
        word = request.form['word']
        translation = request.form['translation']
        level = request.form['level']
        topic = request.form['topic']
        
        new_word = Word(word=word, translation=translation, level=level, topic=topic)
        db.session.add(new_word)
        db.session.commit()
        return redirect(url_for('lessons'))  # Redirige a la página de lecciones

    return render_template('add_word.html')

@app.route('/lessons', methods=['GET', 'POST'])
def lessons():
    if 'username' not in session:
        return redirect(url_for('index'))

    level_filter = request.args.get('level')
    if level_filter:
        words = Word.query.filter_by(level=level_filter).all()
    else:
        words = Word.query.all()
    
    return render_template('lessons.html', words=words)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

# Añadir admin por defecto al inicio
with app.app_context():
    add_default_admin()

if __name__ == '__main__':
    app.run(debug=True)
