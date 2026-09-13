import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def agora() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)


class EstadoEquipamento(str, enum.Enum):
    DISPONIVEL = "DISPONIVEL"
    EMPRESTADO = "EMPRESTADO"
    INDISPONIVEL = "INDISPONIVEL"


class TipoPendencia(str, enum.Enum):
    ATRASO = "ATRASO"
    DANO = "DANO"


class Aluno(Base):
    __tablename__ = "alunos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    matricula: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)

    emprestimos: Mapped[list["Emprestimo"]] = relationship(back_populates="aluno")
    pendencias: Mapped[list["Pendencia"]] = relationship(back_populates="aluno")


class Equipamento(Base):
    __tablename__ = "equipamentos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    patrimonio: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    descricao: Mapped[str] = mapped_column(String(120), nullable=False)
    estado: Mapped[EstadoEquipamento] = mapped_column(
        Enum(EstadoEquipamento, native_enum=False, length=16),
        nullable=False,
        default=EstadoEquipamento.DISPONIVEL,
    )

    emprestimos: Mapped[list["Emprestimo"]] = relationship(back_populates="equipamento")


class Emprestimo(Base):
    __tablename__ = "emprestimos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("alunos.id"), nullable=False, index=True)
    equipamento_id: Mapped[int] = mapped_column(
        ForeignKey("equipamentos.id"), nullable=False, index=True
    )
    emprestado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=agora)
    vence_em: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    devolvido_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    operador_emprestimo: Mapped[str] = mapped_column(String(120), nullable=False)
    operador_devolucao: Mapped[str | None] = mapped_column(String(120), nullable=True)

    aluno: Mapped["Aluno"] = relationship(back_populates="emprestimos")
    equipamento: Mapped["Equipamento"] = relationship(back_populates="emprestimos")


class Pendencia(Base):
    __tablename__ = "pendencias"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    aluno_id: Mapped[int] = mapped_column(ForeignKey("alunos.id"), nullable=False, index=True)
    tipo: Mapped[TipoPendencia] = mapped_column(
        Enum(TipoPendencia, native_enum=False, length=16), nullable=False
    )
    aberta_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=agora)
    quitada_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    motivo_quitacao: Mapped[str | None] = mapped_column(String(240), nullable=True)

    aluno: Mapped["Aluno"] = relationship(back_populates="pendencias")
