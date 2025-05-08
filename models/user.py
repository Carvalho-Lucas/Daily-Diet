from database import db
from flask_login import UserMixin

# Tabela de usuários
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

    # Relacionamento com Refeição
    refeicoes = db.relationship("Refeicao", backref="user", lazy=True)
