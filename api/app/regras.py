from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import ErroDeNegocio, NaoEncontrado
from app.models import (
    Aluno,
    Emprestimo,
    Equipamento,
    EstadoEquipamento,
    Pendencia,
    TipoPendencia,
    agora,
)

PRAZO_DIAS = 7


def calcular_vencimento(emprestado_em: datetime) -> datetime:
    return emprestado_em + timedelta(days=PRAZO_DIAS)


def dias_de_atraso(vence_em: datetime, referencia: datetime) -> int:
    if referencia <= vence_em:
        return 0
    return (referencia - vence_em).days + 1


def buscar_aluno(db: Session, matricula: str) -> Aluno:
    aluno = db.scalar(select(Aluno).where(Aluno.matricula == matricula))
    if aluno is None:
        raise NaoEncontrado(
            "ALUNO_NAO_ENCONTRADO",
            f"Nao existe aluno com a matricula {matricula}.",
        )
    return aluno


def buscar_equipamento(db: Session, patrimonio: str) -> Equipamento:
    equipamento = db.scalar(select(Equipamento).where(Equipamento.patrimonio == patrimonio))
    if equipamento is None:
        raise NaoEncontrado(
            "EQUIPAMENTO_NAO_ENCONTRADO",
            f"Nao existe equipamento com o patrimonio {patrimonio}.",
        )
    return equipamento


def emprestimos_em_aberto(db: Session) -> list[Emprestimo]:
    return list(
        db.scalars(
            select(Emprestimo)
            .where(Emprestimo.devolvido_em.is_(None))
            .order_by(Emprestimo.vence_em)
        )
    )


def emprestimos_vencidos(db: Session, referencia: datetime) -> list[Emprestimo]:
    return [e for e in emprestimos_em_aberto(db) if e.vence_em < referencia]


def emprestimo_aberto_do_equipamento(db: Session, equipamento: Equipamento) -> Emprestimo | None:
    return db.scalar(
        select(Emprestimo).where(
            Emprestimo.equipamento_id == equipamento.id,
            Emprestimo.devolvido_em.is_(None),
        )
    )


def atrasos_do_aluno(db: Session, aluno: Aluno, referencia: datetime) -> list[Emprestimo]:
    return [e for e in emprestimos_vencidos(db, referencia) if e.aluno_id == aluno.id]


def danos_em_aberto_do_aluno(db: Session, aluno: Aluno) -> list[Pendencia]:
    return list(
        db.scalars(
            select(Pendencia)
            .where(
                Pendencia.aluno_id == aluno.id,
                Pendencia.tipo == TipoPendencia.DANO,
                Pendencia.quitada_em.is_(None),
            )
            .order_by(Pendencia.aberta_em)
        )
    )


def motivo_bloqueio(db: Session, aluno: Aluno, referencia: datetime) -> str | None:
    tem_atraso = bool(atrasos_do_aluno(db, aluno, referencia))
    tem_dano = bool(danos_em_aberto_do_aluno(db, aluno))
    if tem_atraso and tem_dano:
        return "ATRASO_E_DANO"
    if tem_atraso:
        return "ATRASO"
    if tem_dano:
        return "DANO"
    return None


def registrar_emprestimo(
    db: Session, matricula: str, patrimonio: str, operador: str
) -> Emprestimo:
    referencia = agora()
    aluno = buscar_aluno(db, matricula)
    equipamento = buscar_equipamento(db, patrimonio)

    motivo = motivo_bloqueio(db, aluno, referencia)
    if motivo is not None:
        raise ErroDeNegocio(
            "PENDENCIA",
            f"O aluno {aluno.matricula} possui pendencia em aberto e nao pode "
            f"receber novo emprestimo.",
            motivo=motivo,
        )

    if equipamento.estado == EstadoEquipamento.EMPRESTADO:
        raise ErroDeNegocio(
            "EQUIPAMENTO_EMPRESTADO",
            f"O equipamento {equipamento.patrimonio} ja esta emprestado.",
        )
    if equipamento.estado == EstadoEquipamento.INDISPONIVEL:
        raise ErroDeNegocio(
            "EQUIPAMENTO_INDISPONIVEL",
            f"O equipamento {equipamento.patrimonio} esta indisponivel.",
        )

    emprestimo = Emprestimo(
        aluno_id=aluno.id,
        equipamento_id=equipamento.id,
        emprestado_em=referencia,
        vence_em=calcular_vencimento(referencia),
        operador_emprestimo=operador,
    )
    equipamento.estado = EstadoEquipamento.EMPRESTADO
    db.add(emprestimo)
    db.commit()
    return emprestimo


def registrar_devolucao(
    db: Session, patrimonio: str, operador: str, com_dano: bool
) -> tuple[Emprestimo, Pendencia | None]:
    referencia = agora()
    equipamento = buscar_equipamento(db, patrimonio)

    emprestimo = emprestimo_aberto_do_equipamento(db, equipamento)
    if emprestimo is None:
        raise ErroDeNegocio(
            "EQUIPAMENTO_NAO_EMPRESTADO",
            f"O equipamento {equipamento.patrimonio} nao esta emprestado.",
        )

    emprestimo.devolvido_em = referencia
    emprestimo.operador_devolucao = operador

    pendencia = None
    if com_dano:
        equipamento.estado = EstadoEquipamento.INDISPONIVEL
        pendencia = Pendencia(
            aluno_id=emprestimo.aluno_id,
            tipo=TipoPendencia.DANO,
            aberta_em=referencia,
        )
        db.add(pendencia)
    else:
        equipamento.estado = EstadoEquipamento.DISPONIVEL

    db.commit()
    return emprestimo, pendencia


def quitar_pendencia_de_dano(db: Session, pendencia_id: int, motivo_quitacao: str) -> Pendencia:
    pendencia = db.scalar(
        select(Pendencia).where(
            Pendencia.id == pendencia_id,
            Pendencia.tipo == TipoPendencia.DANO,
        )
    )
    if pendencia is None:
        raise NaoEncontrado(
            "PENDENCIA_NAO_ENCONTRADA",
            f"Nao existe pendencia de dano com o id {pendencia_id}.",
        )
    if pendencia.quitada_em is not None:
        raise ErroDeNegocio(
            "PENDENCIA_JA_QUITADA",
            f"A pendencia {pendencia.id} ja foi quitada em "
            f"{pendencia.quitada_em.isoformat()}Z.",
        )

    pendencia.quitada_em = agora()
    pendencia.motivo_quitacao = motivo_quitacao
    db.commit()
    return pendencia


def listar_emprestados(db: Session) -> list[dict]:
    referencia = agora()
    return [
        {
            "emprestimo_id": e.id,
            "patrimonio": e.equipamento.patrimonio,
            "descricao": e.equipamento.descricao,
            "matricula": e.aluno.matricula,
            "nome": e.aluno.nome,
            "emprestado_em": e.emprestado_em,
            "vence_em": e.vence_em,
            "em_atraso": e.vence_em < referencia,
            "dias_de_atraso": dias_de_atraso(e.vence_em, referencia),
            "operador_emprestimo": e.operador_emprestimo,
        }
        for e in emprestimos_em_aberto(db)
    ]


def relatorio_de_atrasos(db: Session) -> list[dict]:
    referencia = agora()
    return [
        {
            "emprestimo_id": e.id,
            "patrimonio": e.equipamento.patrimonio,
            "descricao": e.equipamento.descricao,
            "matricula": e.aluno.matricula,
            "nome": e.aluno.nome,
            "emprestado_em": e.emprestado_em,
            "vence_em": e.vence_em,
            "dias_de_atraso": dias_de_atraso(e.vence_em, referencia),
            "operador_emprestimo": e.operador_emprestimo,
        }
        for e in emprestimos_vencidos(db, referencia)
    ]


def listar_pendencias_abertas(db: Session) -> list[dict]:
    referencia = agora()
    pendencias = []

    for aluno, emprestimos in _agrupar_por_aluno(emprestimos_vencidos(db, referencia)):
        pendencias.append(
            {
                "id": None,
                "matricula": aluno.matricula,
                "nome": aluno.nome,
                "tipo": TipoPendencia.ATRASO.value,
                "aberta_em": min(e.vence_em for e in emprestimos),
                "quitada_em": None,
                "motivo_quitacao": None,
                "quitavel": False,
                "emprestimos_em_atraso": [e.equipamento.patrimonio for e in emprestimos],
            }
        )

    abertas = db.scalars(
        select(Pendencia)
        .where(Pendencia.tipo == TipoPendencia.DANO, Pendencia.quitada_em.is_(None))
        .order_by(Pendencia.aberta_em)
    )
    for p in abertas:
        pendencias.append(
            {
                "id": p.id,
                "matricula": p.aluno.matricula,
                "nome": p.aluno.nome,
                "tipo": p.tipo.value,
                "aberta_em": p.aberta_em,
                "quitada_em": None,
                "motivo_quitacao": None,
                "quitavel": True,
                "emprestimos_em_atraso": [],
            }
        )

    return pendencias


def _agrupar_por_aluno(emprestimos: list[Emprestimo]) -> list[tuple[Aluno, list[Emprestimo]]]:
    grupos: dict[int, list[Emprestimo]] = {}
    for e in emprestimos:
        grupos.setdefault(e.aluno_id, []).append(e)
    return [(es[0].aluno, es) for es in grupos.values()]
