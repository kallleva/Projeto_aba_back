from . import db
from .pergunta import Pergunta

class ChecklistResposta(db.Model):
    __tablename__ = "checklist_respostas"

    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('checklists_diarios.id'), nullable=False)
    pergunta_id = db.Column(db.Integer, db.ForeignKey('perguntas.id'), nullable=False)
    resposta = db.Column(db.Text, nullable=True)
    resposta_calculada = db.Column(db.Text, nullable=True)  # Para armazenar o resultado da fórmula

    checklist = db.relationship('ChecklistDiario', back_populates='respostas')
    pergunta = db.relationship('Pergunta', backref='checklist_respostas')

    def to_dict(self):
        return {
            'id': self.id,
            'checklist_id': self.checklist_id,
            'pergunta_id': self.pergunta_id,
            'resposta': self.resposta,
            'resposta_calculada': self.resposta_calculada,
            'pergunta': self.pergunta.to_dict() if self.pergunta else None,
            'eh_formula': self.pergunta.tipo.value == 'FORMULA' if self.pergunta else False
        }
    
    def calcular_formula(self, respostas_dict):
        """
        Calcula a fórmula da pergunta usando as respostas fornecidas
        respostas_dict: dict com {pergunta_id: resposta}
        """
        if not self.pergunta or self.pergunta.tipo.value != 'FORMULA' or not self.pergunta.formula:
            return None
            
        try:
            formula = self.pergunta.formula
            # Substituir referências de perguntas pelos valores das respostas
            for pergunta_id, resposta in respostas_dict.items():
                # Converter resposta para número se possível
                try:
                    valor = float(resposta) if resposta else 0
                except (ValueError, TypeError):
                    valor = 0
                
                # Substituir {pergunta_id} pelo valor na fórmula
                formula = formula.replace(f'{{{pergunta_id}}}', str(valor))
            
            # Avaliar a fórmula (cuidado com segurança - em produção usar uma biblioteca segura)
            resultado = eval(formula)
            return str(resultado)
        except Exception as e:
            print(f"Erro ao calcular fórmula: {e}")
            return None
