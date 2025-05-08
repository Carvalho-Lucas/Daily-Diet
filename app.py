from flask import Flask, request, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from database import db
from models.user import User
from models.refeicao import Refeicao

# Configuração principal do app
app = Flask(__name__)
app.config['SECRET_KEY'] = "secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://toningas:admin123@127.0.0.1:3306/daily_diet'

# Inicialização do banco e login manager
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Função para recarregar usuário logado
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# -----------------------------
# 🔐 Autenticação e Sessão
# -----------------------------

# Registro de novo usuário
@app.route("/user", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if username and password:
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Usuário criado com sucesso!"})
    return jsonify({"error": "Dados inválidos"}), 400

# Login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()
    if user and user.password == data.get("password"):
        login_user(user)
        return jsonify({"message": "Login realizado!"})
    return jsonify({"error": "Credencial inválida"}), 400

# Logout
@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout realizado com sucesso!"})

# -----------------------------
# 🍽️ Rotas de Refeições
# -----------------------------

# Criar nova refeição
@app.route("/refeicao", methods=["POST"])
@login_required
def criar_refeicao():
    data = request.json
    nova_refeicao = Refeicao(
        nome=data["nome"],
        descricao=data["descricao"],
        data_hora=data["data_hora"],
        dentro_dieta=data["dentro_dieta"],
        user_id=current_user.id
    )
    db.session.add(nova_refeicao)
    db.session.commit()
    return jsonify({"message": "Refeição registrada!"})

# Listar todas as refeições do usuário logado
@app.route("/refeicao", methods=["GET"])
@login_required
def listar_refeicoes():
    refeicoes = Refeicao.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        "id": r.id,
        "nome": r.nome,
        "descricao": r.descricao,
        "data_hora": r.data_hora,
        "dentro_dieta": r.dentro_dieta
    } for r in refeicoes])

# Visualizar uma refeição específica
@app.route("/refeicao/<int:id>", methods=["GET"])
@login_required
def get_refeicao(id):
    refeicao = Refeicao.query.filter_by(id=id, user_id=current_user.id).first()
    if refeicao:
        return jsonify({
            "id": refeicao.id,
            "nome": refeicao.nome,
            "descricao": refeicao.descricao,
            "data_hora": refeicao.data_hora,
            "dentro_dieta": refeicao.dentro_dieta
        })
    return jsonify({"error": "Refeição não encontrada"}), 404

# Atualizar refeição existente
@app.route("/refeicao/<int:id>", methods=["PUT"])
@login_required
def atualizar_refeicao(id):
    data = request.json
    refeicao = Refeicao.query.filter_by(id=id, user_id=current_user.id).first()
    if refeicao:
        refeicao.nome = data["nome"]
        refeicao.descricao = data["descricao"]
        refeicao.data_hora = data["data_hora"]
        refeicao.dentro_dieta = data["dentro_dieta"]
        db.session.commit()
        return jsonify({"message": "Refeição atualizada com sucesso!"})
    return jsonify({"error": "Refeição não encontrada"}), 404

# Deletar refeição
@app.route("/refeicao/<int:id>", methods=["DELETE"])
@login_required
def deletar_refeicao(id):
    refeicao = Refeicao.query.filter_by(id=id, user_id=current_user.id).first()
    if refeicao:
        db.session.delete(refeicao)
        db.session.commit()
        return jsonify({"message": "Refeição deletada!"})
    return jsonify({"error": "Refeição não encontrada"}), 404

# -----------------------------
# 🧪 Execução
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)
