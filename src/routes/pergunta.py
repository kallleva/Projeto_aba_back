# src/routes/pergunta.py
from flask import Blueprint, request, jsonify
from src.models import db
from src.models.pergunta import Pergunta, TipoPerguntaEnum

pergunta_bp = Blueprint("pergunta", __name__)

# Mapeamento de valores recebidos do frontend para enum PostgreSQL
TIPO_MAP = {e.name: e for e in TipoPerguntaEnum}

@pergunta_bp.route("/perguntas", methods=["GET"])
def listar_perguntas():
    perguntas = Pergunta.query.all()
    return jsonify([p.to_dict() for p in perguntas]), 200

@pergunta_bp.route("/perguntas/<int:pergunta_id>", methods=["GET"])
def obter_pergunta(pergunta_id):
    pergunta = Pergunta.query.get_or_404(pergunta_id)
    return jsonify(pergunta.to_dict()), 200

@pergunta_bp.route("/perguntas", methods=["POST"])
def criar_pergunta():
    dados = request.get_json()
    if not dados.get("texto") or not dados.get("tipo"):
        return jsonify({"erro": "Texto e tipo são obrigatórios"}), 400

    # Converter tipo recebido para enum PostgreSQL
    try:
        tipo_enum = TIPO_MAP[dados["tipo"].lower()]
    except KeyError:
        return jsonify({"erro": f"Tipo inválido: {dados['tipo']}"}), 400

    pergunta = Pergunta(
        texto=dados["texto"],
        tipo=tipo_enum,
        formula=dados.get("formula")
    )
    db.session.add(pergunta)
    db.session.commit()
    return jsonify(pergunta.to_dict()), 201

@pergunta_bp.route("/perguntas/<int:pergunta_id>", methods=["PUT"])
def atualizar_pergunta(pergunta_id):
    pergunta = Pergunta.query.get_or_404(pergunta_id)
    dados = request.get_json()

    if "texto" in dados:
        pergunta.texto = dados["texto"]

    if "tipo" in dados:
        try:
            pergunta.tipo = TIPO_MAP[dados["tipo"].lower()]
        except KeyError:
            return jsonify({"erro": f"Tipo inválido: {dados['tipo']}"}), 400

    if "formula" in dados:
        pergunta.formula = dados["formula"]

    db.session.commit()
    return jsonify(pergunta.to_dict()), 200

@pergunta_bp.route("/perguntas/<int:pergunta_id>", methods=["DELETE"])
def deletar_pergunta(pergunta_id):
    pergunta = Pergunta.query.get_or_404(pergunta_id)
    db.session.delete(pergunta)
    db.session.commit()
    return jsonify({"mensagem": "Pergunta deletada com sucesso"}), 200
