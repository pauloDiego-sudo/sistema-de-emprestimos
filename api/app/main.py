import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import regras, schemas
from app.database import criar_tabelas, get_db
from app.errors import registrar_tratadores

ORIGEM_FRONTEND = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")


@asynccontextmanager
async def lifespan(app: FastAPI):
    criar_tabelas()
    yield


app = FastAPI(title="Sistema de Emprestimos do Laboratorio", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ORIGEM_FRONTEND],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

registrar_tratadores(app)


@app.post("/emprestimos", status_code=201, response_model=schemas.EmprestimoOut)
def registrar_emprestimo(dados: schemas.EmprestimoIn, db: Session = Depends(get_db)):
    emprestimo = regras.registrar_emprestimo(
        db, dados.matricula, dados.patrimonio, dados.operador
    )
    return schemas.emprestimo_out(emprestimo)


@app.post("/devolucoes", status_code=201, response_model=schemas.DevolucaoOut)
def registrar_devolucao(dados: schemas.DevolucaoIn, db: Session = Depends(get_db)):
    emprestimo, pendencia = regras.registrar_devolucao(
        db, dados.patrimonio, dados.operador, dados.com_dano
    )
    return schemas.DevolucaoOut(
        emprestimo=schemas.emprestimo_out(emprestimo),
        equipamento_estado=emprestimo.equipamento.estado.value,
        pendencia_aberta=schemas.pendencia_out(pendencia) if pendencia else None,
    )


@app.get("/emprestimos/abertos", response_model=list[schemas.EmprestadoOut])
def listar_emprestados(db: Session = Depends(get_db)):
    return regras.listar_emprestados(db)


@app.get("/atrasos", response_model=list[schemas.AtrasoOut])
def relatorio_de_atrasos(db: Session = Depends(get_db)):
    return regras.relatorio_de_atrasos(db)


@app.get("/pendencias/abertas", response_model=list[schemas.PendenciaAbertaOut])
def listar_pendencias_abertas(db: Session = Depends(get_db)):
    return regras.listar_pendencias_abertas(db)


@app.post("/pendencias/{pendencia_id}/quitacao", response_model=schemas.PendenciaOut)
def quitar_pendencia(
    pendencia_id: int, dados: schemas.QuitacaoIn, db: Session = Depends(get_db)
):
    pendencia = regras.quitar_pendencia_de_dano(db, pendencia_id, dados.motivo_quitacao)
    return schemas.pendencia_out(pendencia)
