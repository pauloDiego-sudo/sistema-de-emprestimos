from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ErroDeNegocio(Exception):
    status_code = 409

    def __init__(self, codigo: str, mensagem: str, motivo: str | None = None):
        self.codigo = codigo
        self.motivo = motivo
        self.mensagem = mensagem
        super().__init__(mensagem)

    def corpo(self) -> dict:
        return {"codigo": self.codigo, "motivo": self.motivo, "mensagem": self.mensagem}


class NaoEncontrado(ErroDeNegocio):
    status_code = 404


def registrar_tratadores(app: FastAPI) -> None:
    @app.exception_handler(ErroDeNegocio)
    async def _negocio(request: Request, exc: ErroDeNegocio):
        return JSONResponse(status_code=exc.status_code, content=exc.corpo())

    @app.exception_handler(RequestValidationError)
    async def _validacao(request: Request, exc: RequestValidationError):
        erro = exc.errors()[0]
        campo = ".".join(str(p) for p in erro["loc"][1:]) or None
        return JSONResponse(
            status_code=422,
            content={
                "codigo": "DADOS_INVALIDOS",
                "motivo": campo,
                "mensagem": f"Campo invalido: {campo}. {erro['msg']}",
            },
        )
