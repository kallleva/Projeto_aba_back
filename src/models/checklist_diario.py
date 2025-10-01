from datetime import date
from . import db
from .meta_terapeutica import MetaTerapeutica
from .checklist_respostas import ChecklistResposta

class ChecklistDiario(db.Model):
    __tablename__ = 'checklists_diarios'

    id = db.Column(db.Integer, primary_key=True)
    meta_id = db.Column(db.Integer, db.ForeignKey('metas_terapeuticas.id'), nullable=False)
    data = db.Column(db.Date, nullable=False, default=date.today)
    nota = db.Column(db.Integer, nullable=True)
    observacao = db.Column(db.Text, nullable=True)

    meta = db.relationship('MetaTerapeutica', back_populates='checklists_diarios')
    respostas = db.relationship('ChecklistResposta', back_populates='checklist', cascade='all, delete-orphan', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('meta_id', 'data', name='unique_meta_data'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'meta_id': self.meta_id,
            'meta_descricao': self.meta.descricao if self.meta else None,
            'data': self.data.isoformat() if self.data else None,
            'nota': self.nota,
            'observacao': self.observacao,
            'respostas': [r.to_dict() for r in self.respostas],
            'perguntas': self.obter_perguntas_formularios()
        }
    
    def obter_perguntas_formularios(self):
        """Retorna todas as perguntas dos formulários vinculados à meta"""
        perguntas = []
        if self.meta and self.meta.formularios:
            for formulario in self.meta.formularios:
                perguntas.extend([p.to_dict() for p in formulario.perguntas])
        return perguntas

    def validar_respostas(self, respostas_dict):
        """
        Valida se todas as perguntas obrigatórias foram respondidas
        respostas_dict: dict com {pergunta_id: resposta}
        """
        if not self.meta or not self.meta.formularios:
            return True, "Nenhum formulário vinculado à meta"
        
        perguntas_obrigatorias = []
        for formulario in self.meta.formularios:
            for pergunta in formulario.perguntas:
                if pergunta.obrigatoria and pergunta.tipo.value != 'FORMULA':
                    perguntas_obrigatorias.append(pergunta)
        
        perguntas_nao_respondidas = []
        for pergunta in perguntas_obrigatorias:
            resposta = respostas_dict.get(str(pergunta.id), "")
            if not resposta or resposta.strip() == "":
                perguntas_nao_respondidas.append(pergunta.texto)
        
        if perguntas_nao_respondidas:
            return False, f"Perguntas obrigatórias não respondidas: {', '.join(perguntas_nao_respondidas)}"
        
        return True, "Validação aprovada"
