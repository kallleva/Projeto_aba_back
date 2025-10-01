from flask import Blueprint, request, jsonify
from src.models import db
from src.models.formulario import Formulario
from src.models.pergunta import Pergunta

formulario_bp = Blueprint("formulario", __name__)

# Listar todos
@formulario_bp.route("/formularios", methods=["GET"])
def listar_formularios():
    """
    Lista todos os formulários
    ---
    tags:
      - Formulários
    responses:
      200:
        description: Lista de formulários
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              nome:
                type: string
              descricao:
                type: string
              categoria:
                type: string
              perguntas:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                    texto:
                      type: string
                    tipo:
                      type: string
                    obrigatoria:
                      type: boolean
                    ordem:
                      type: integer
    """
    forms = Formulario.query.all()
    return jsonify([f.to_dict() for f in forms]), 200


# Obter 1
@formulario_bp.route("/formularios/<int:id>", methods=["GET"])
def obter_formulario(id):
    """
    Obtém um formulário específico
    ---
    tags:
      - Formulários
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do formulário
    responses:
      200:
        description: Formulário encontrado
      404:
        description: Formulário não encontrado
    """
    form = Formulario.query.get_or_404(id)
    return jsonify(form.to_dict()), 200


# Criar
@formulario_bp.route("/formularios", methods=["POST"])
def criar_formulario():
    """
    Cria um novo formulário
    ---
    tags:
      - Formulários
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nome
          properties:
            nome:
              type: string
            descricao:
              type: string
            categoria:
              type: string
              default: avaliacao
            perguntas:
              type: array
              items:
                type: object
                properties:
                  texto:
                    type: string
                  tipo:
                    type: string
                    default: texto
                  obrigatoria:
                    type: boolean
                    default: false
                  formula:
                    type: string
    responses:
      201:
        description: Formulário criado com sucesso
      400:
        description: Erro de validação
    """
    dados = request.get_json()
    if not dados.get("nome"):
        return jsonify({"erro": "Nome é obrigatório"}), 400

    form = Formulario(
        nome=dados["nome"],
        descricao=dados.get("descricao"),
        categoria=dados.get("categoria", "avaliacao")
    )
    db.session.add(form)
    db.session.flush()  # garante ID disponível antes das perguntas

    for i, p in enumerate(dados.get("perguntas", []), start=1):
        pergunta = Pergunta(
            texto=p["texto"],
            tipo=p.get("tipo", "texto"),
            obrigatoria=p.get("obrigatoria", False),
            ordem=i,
            formulario_id=form.id,
            formula=p.get("formula")
        )
        db.session.add(pergunta)

    db.session.commit()
    return jsonify(form.to_dict()), 201




# Atualizar
@formulario_bp.route("/formularios/<int:id>", methods=["PUT"])
def atualizar_formulario(id):
    """
    Atualiza um formulário existente
    --- 
    tags:
      - Formulários
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            nome:
              type: string
            descricao:
              type: string
            categoria:
              type: string
            perguntas:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  texto:
                    type: string
                  tipo:
                    type: string
                  obrigatoria:
                    type: boolean
                  formula:
                    type: string
    responses:
      200:
        description: Formulário atualizado com sucesso
      404:
        description: Formulário não encontrado
    """
    form = Formulario.query.get_or_404(id)
    dados = request.get_json()

    form.nome = dados.get("nome", form.nome)
    form.descricao = dados.get("descricao", form.descricao)
    form.categoria = dados.get("categoria", form.categoria)

    # Atualizar perguntas sem apagar as antigas
    for i, p in enumerate(dados.get("perguntas", []), start=1):
        if "id" in p and p["id"]:
            # Atualiza pergunta existente
            pergunta = Pergunta.query.filter_by(id=p["id"], formulario_id=form.id).first()
            if pergunta:
                pergunta.texto = p["texto"]
                pergunta.tipo = p.get("tipo", "texto")
                pergunta.obrigatoria = p.get("obrigatoria", False)
                pergunta.ordem = i
                pergunta.formula = p.get("formula")
        else:
            # Cria nova pergunta
            pergunta = Pergunta(
                texto=p["texto"],
                tipo=p.get("tipo", "texto"),
                obrigatoria=p.get("obrigatoria", False),
                ordem=i,
                formulario_id=form.id,
                formula=p.get("formula")
            )
            db.session.add(pergunta)

    db.session.commit()
    return jsonify(form.to_dict()), 200



# Deletar
@formulario_bp.route("/formularios/<int:id>", methods=["DELETE"])
def deletar_formulario(id):
    """
    Deleta um formulário
    ---
    tags:
      - Formulários
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Formulário deletado com sucesso
      404:
        description: Formulário não encontrado
    """
    form = Formulario.query.get_or_404(id)
    db.session.delete(form)
    db.session.commit()
    return jsonify({"mensagem": "Formulário deletado com sucesso"}), 200
