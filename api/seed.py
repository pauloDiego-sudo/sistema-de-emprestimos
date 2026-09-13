from datetime import timedelta

from app.database import Base, SessionLocal, engine
from app.models import (
    Aluno,
    Emprestimo,
    Equipamento,
    EstadoEquipamento,
    Pendencia,
    TipoPendencia,
    agora,
)
from app.regras import calcular_vencimento


def popular() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    hoje = agora()
    db = SessionLocal()

    ana = Aluno(matricula="2023001", nome="Ana Ribeiro")
    bruno = Aluno(matricula="2023002", nome="Bruno Carvalho")
    carla = Aluno(matricula="2023003", nome="Carla Dias")
    diego = Aluno(matricula="2023004", nome="Diego Lopes")
    db.add_all([ana, bruno, carla, diego])

    notebook = Equipamento(
        patrimonio="PAT-001",
        descricao="Notebook Dell Latitude",
        estado=EstadoEquipamento.DISPONIVEL,
    )
    projetor = Equipamento(
        patrimonio="PAT-002",
        descricao="Projetor Epson PowerLite",
        estado=EstadoEquipamento.EMPRESTADO,
    )
    multimetro = Equipamento(
        patrimonio="PAT-003",
        descricao="Multimetro Minipa ET-2042",
        estado=EstadoEquipamento.INDISPONIVEL,
    )
    osciloscopio = Equipamento(
        patrimonio="PAT-004",
        descricao="Osciloscopio Tektronix TBS1052",
        estado=EstadoEquipamento.DISPONIVEL,
    )
    kit_arduino = Equipamento(
        patrimonio="PAT-005",
        descricao="Kit Arduino Uno completo",
        estado=EstadoEquipamento.EMPRESTADO,
    )
    fonte = Equipamento(
        patrimonio="PAT-006",
        descricao="Fonte de bancada Instrutherm FA-3005",
        estado=EstadoEquipamento.INDISPONIVEL,
    )
    db.add_all([notebook, projetor, multimetro, osciloscopio, kit_arduino, fonte])
    db.flush()

    # Ana: emprestimo em aberto e dentro do prazo, sem pendencia.
    inicio_ana = hoje - timedelta(days=2)
    db.add(
        Emprestimo(
            aluno_id=ana.id,
            equipamento_id=kit_arduino.id,
            emprestado_em=inicio_ana,
            vence_em=calcular_vencimento(inicio_ana),
            operador_emprestimo="Tecnico Joao",
        )
    )

    # Bruno: emprestimo em aberto e ja vencido (gera pendencia de ATRASO derivada).
    inicio_bruno = hoje - timedelta(days=20)
    db.add(
        Emprestimo(
            aluno_id=bruno.id,
            equipamento_id=projetor.id,
            emprestado_em=inicio_bruno,
            vence_em=calcular_vencimento(inicio_bruno),
            operador_emprestimo="Tecnico Joao",
        )
    )

    # Carla: devolveu com dano, pendencia de DANO em aberto.
    inicio_carla = hoje - timedelta(days=30)
    db.add(
        Emprestimo(
            aluno_id=carla.id,
            equipamento_id=multimetro.id,
            emprestado_em=inicio_carla,
            vence_em=calcular_vencimento(inicio_carla),
            devolvido_em=hoje - timedelta(days=25),
            operador_emprestimo="Tecnico Joao",
            operador_devolucao="Tecnica Maria",
        )
    )
    db.add(
        Pendencia(
            aluno_id=carla.id,
            tipo=TipoPendencia.DANO,
            aberta_em=hoje - timedelta(days=25),
        )
    )

    # Diego: devolveu com dano, pendencia ja quitada (nao bloqueia novo emprestimo).
    inicio_diego = hoje - timedelta(days=60)
    db.add(
        Emprestimo(
            aluno_id=diego.id,
            equipamento_id=fonte.id,
            emprestado_em=inicio_diego,
            vence_em=calcular_vencimento(inicio_diego),
            devolvido_em=hoje - timedelta(days=55),
            operador_emprestimo="Tecnica Maria",
            operador_devolucao="Tecnica Maria",
        )
    )
    db.add(
        Pendencia(
            aluno_id=diego.id,
            tipo=TipoPendencia.DANO,
            aberta_em=hoje - timedelta(days=55),
            quitada_em=hoje - timedelta(days=40),
            motivo_quitacao="Equipamento reparado e custo pago pelo aluno",
        )
    )

    db.commit()
    db.close()
    print("Banco populado: 4 alunos, 6 equipamentos, 4 emprestimos, 2 pendencias de dano.")


if __name__ == "__main__":
    popular()
