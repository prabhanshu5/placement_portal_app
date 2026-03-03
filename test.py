
from flask import Flask
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_models.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    # create tables
    db.create_all()

    # create a sample user (password stored as-is in your current model)
    u = User(email='test@example.com', password='pass123', role='student')
    db.session.add(u)
    db.session.commit()

    print('Created user id:', u.id, 'email:', u.email)
