import os
import sys
import io
import logging
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from flasgger import Swagger

# -------------------------
# Forçar UTF-8 no stdout/stderr
# -------------------------
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# -------------------------
# Corrigir path para imports
# -------------------------
# Adiciona a pasta raiz do projeto ao sys.path
# Assim podemos importar src.models, src.routes, etc.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)

# -------------------------
# Agora os imports funcionam
# -------------------------
from src.models import db
from src.routes.user import user_bp
from src.routes.paciente import paciente_bp
from src.routes.profissional import profissional_bp
from src.routes.profissional_paciente import profissional_paciente_bp
from src.routes.plano_terapeutico import plano_terapeutico_bp
from src.routes.meta_terapeutica import meta_terapeutica_bp
from src.routes.checklist_diario import checklist_diario_bp
from src.routes.relatorios import relatorios_bp
from src.routes.auth import auth_bp
from src.routes.pergunta import pergunta_bp
from src.routes.formulario import formulario_bp
from src.routes.agenda import agenda_bp

# -------------------------
# Inicialização do Flask
# -------------------------
app = Flask(__name__, static_folder=os.path.join(current_dir, 'static'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# -------------------------
# Configuração CORS
# -------------------------
CORS(
    app,
    resources={r"/api/*": {"origins": "http://localhost:5173"}},
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

# -------------------------
# Configuração do banco PostgreSQL
# -------------------------
DB_USER = os.environ.get("DB_USER", "aba_user")
DB_PASS = os.environ.get("DB_PASS", "aba_pass123")
DB_NAME = os.environ.get("DB_NAME", "aba_postgres")
DB_HOST = os.environ.get("DB_HOST", "db")
DB_PORT = os.environ.get("DB_PORT", "5432")

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa SQLAlchemy
db.init_app(app)

# -------------------------
# Configuração Swagger
# -------------------------
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "API Terapêutica",
        "description": "Documentação da API para formulários, pacientes, profissionais e autenticação.",
        "version": "1.0.0"
    },
    "basePath": "/api",
})

# -------------------------
# Registrar Blueprints
# -------------------------
blueprints = [
    user_bp, paciente_bp, profissional_bp, profissional_paciente_bp,
    plano_terapeutico_bp, meta_terapeutica_bp, checklist_diario_bp,
    relatorios_bp, auth_bp, pergunta_bp, formulario_bp, agenda_bp
]

for bp in blueprints:
    app.register_blueprint(bp, url_prefix='/api')

# -------------------------
# Criar tabelas e popular dados iniciais
# -------------------------
with app.app_context():
    try:
        db.create_all()
        print("✅ Tabelas criadas com sucesso.")

        # Executar seed data se necessário
        from src.database.seed_data import create_seed_data
        create_seed_data()

    except Exception as e:
        print("❌ Erro ao inicializar banco de dados:", e)

# -------------------------
# Rota de teste
# -------------------------
@app.route('/api/hello', methods=['GET'])
def hello():
    return {"mensagem": "Olá, mundo!"}

# -------------------------
# Servir frontend (SPA)
# -------------------------
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder = app.static_folder
    requested_path = os.path.join(static_folder, path)

    if path != "" and os.path.exists(requested_path):
        return send_from_directory(static_folder, path)

    index_path = os.path.join(static_folder, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(static_folder, 'index.html')

    return "index.html not found", 404

# -------------------------
# Endpoint de exemplo PUT com logging de payload
# -------------------------
@app.route('/api/test-put/<int:id>', methods=['PUT'])
def test_put(id):
    try:
        data = request.json
        print(f"Payload recebido para update {id}: {data}")
        return jsonify({"status": "ok", "id": id, "payload": data})
    except Exception as e:
        print("Erro ao processar PUT:", e)
        return jsonify({"error": str(e)}), 500

# -------------------------
# Inicialização do Flask
# -------------------------
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.debug(f"Tentando conectar ao banco: {DB_USER}@{DB_HOST}:{DB_NAME}")
    app.run(host='0.0.0.0', port=5000, debug=True)
