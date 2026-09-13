from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, PlainSerializer, StringConstraints

from app.models import Emprestimo, Pendencia


def _iso_utc(valor: datetime) -> str:
    return valor.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


DataHoraUTC = Annotated[datetime, PlainSerializer(_iso_utc, return_type=str)]
Texto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
TextoLongo = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=240)]


class EmprestimoIn(BaseModel):
    matricula: Texto
    patrimonio: Texto
    operador: Texto


class DevolucaoIn(BaseModel):
    patrimonio: Texto
    operador: Texto
    com_dano: bool = False


class QuitacaoIn(BaseModel):
    motivo_quitacao: TextoLongo


class EmprestimoOut(BaseModel):
    id: int
    matricula: str
    nome: str
    patrimonio: str
    descricao: str
    emprestado_em: DataHoraUTC
    vence_em: DataHoraUTC
    devolvido_em: DataHoraUTC | None
    operador_emprestimo: str
    operador_devolucao: str | None


class PendenciaOut(BaseModel):
    id: int
    matricula: str
    nome: str
    tipo: str
    aberta_em: DataHoraUTC
    quitada_em: DataHoraUTC | None
    motivo_quitacao: str | None


class DevolucaoOut(BaseModel):
    emprestimo: EmprestimoOut
    equipamento_estado: str
    pendencia_aberta: PendenciaOut | None


class EmprestadoOut(BaseModel):
    emprestimo_id: int
    patrimonio: str
    descricao: str
    matricula: str
    nome: str
    emprestado_em: DataHoraUTC
    vence_em: DataHoraUTC
    em_atraso: bool
    dias_de_atraso: int
    operador_emprestimo: str


class AtrasoOut(BaseModel):
    emprestimo_id: int
    patrimonio: str
    descricao: str
    matricula: str
    nome: str
    emprestado_em: DataHoraUTC
    vence_em: DataHoraUTC
    dias_de_atraso: int
    operador_emprestimo: str


class PendenciaAbertaOut(BaseModel):
    id: int | None
    matricula: str
    nome: str
    tipo: str
    aberta_em: DataHoraUTC
    quitada_em: DataHoraUTC | None
    motivo_quitacao: str | None
    quitavel: bool
    emprestimos_em_atraso: list[str]


def emprestimo_out(emprestimo: Emprestimo) -> EmprestimoOut:
    return EmprestimoOut(
        id=emprestimo.id,
        matricula=emprestimo.aluno.matricula,
        nome=emprestimo.aluno.nome,
        patrimonio=emprestimo.equipamento.patrimonio,
        descricao=emprestimo.equipamento.descricao,
        emprestado_em=emprestimo.emprestado_em,
        vence_em=emprestimo.vence_em,
        devolvido_em=emprestimo.devolvido_em,
        operador_emprestimo=emprestimo.operador_emprestimo,
        operador_devolucao=emprestimo.operador_devolucao,
    )


def pendencia_out(pendencia: Pendencia) -> PendenciaOut:
    return PendenciaOut(
        id=pendencia.id,
        matricula=pendencia.aluno.matricula,
        nome=pendencia.aluno.nome,
        tipo=pendencia.tipo.value,
        aberta_em=pendencia.aberta_em,
        quitada_em=pendencia.quitada_em,
        motivo_quitacao=pendencia.motivo_quitacao,
    )
