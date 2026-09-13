# API — Sistema de Emprestimos do Laboratorio

Backend em FastAPI + SQLAlchemy + SQLite. Sem autenticacao.

## Pre-requisitos

- Python 3.11 ou superior

## Instalacao

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Popular o banco

```bash
python seed.py
```

O script recria `api/emprestimos.db` do zero a cada execucao.

## Rodar

```bash
uvicorn app.main:app --reload --port 8000
```

A API sobe em `http://localhost:8000`. A origem liberada no CORS vem da variavel
de ambiente `FRONTEND_ORIGIN` (padrao `http://localhost:3000`).

## Endpoints

| Operacao | Metodo e rota |
| --- | --- |
| Registrar emprestimo | `POST /emprestimos` |
| Registrar devolucao | `POST /devolucoes` |
| Consultar o que esta emprestado | `GET /emprestimos/abertos` |
| Relatorio de atrasos | `GET /atrasos` |
| Pendencias abertas | `GET /pendencias/abertas` |
| Quitar pendencia de dano | `POST /pendencias/{id}/quitacao` |

O aluno e identificado nas rotas pela matricula; o equipamento, pelo patrimonio.
Datas e horas sao sempre UTC em ISO-8601 com sufixo `Z`.

## Codigos de erro

Toda recusa responde com o corpo:

```json
{"codigo": "<CODIGO>", "motivo": "<MOTIVO ou null>", "mensagem": "<texto>"}
```

| HTTP | codigo | motivo | Quando |
| --- | --- | --- | --- |
| 409 | `PENDENCIA` | `ATRASO`, `DANO` ou `ATRASO_E_DANO` | Emprestimo para aluno com pendencia aberta |
| 409 | `EQUIPAMENTO_EMPRESTADO` | `null` | Emprestimo de equipamento no estado EMPRESTADO |
| 409 | `EQUIPAMENTO_INDISPONIVEL` | `null` | Emprestimo de equipamento no estado INDISPONIVEL |
| 409 | `EQUIPAMENTO_NAO_EMPRESTADO` | `null` | Devolucao de equipamento sem emprestimo em aberto |
| 409 | `PENDENCIA_JA_QUITADA` | `null` | Quitacao de pendencia de dano ja quitada |
| 404 | `ALUNO_NAO_ENCONTRADO` | `null` | Matricula inexistente |
| 404 | `EQUIPAMENTO_NAO_ENCONTRADO` | `null` | Patrimonio inexistente |
| 404 | `PENDENCIA_NAO_ENCONTRADA` | `null` | Id sem pendencia de dano correspondente |
| 422 | `DADOS_INVALIDOS` | nome do campo | Corpo malformado ou campo obrigatorio vazio |

No `POST /emprestimos` a pendencia do aluno e verificada antes do estado do
equipamento: um aluno bloqueado recebe `PENDENCIA` mesmo que o equipamento
tambem esteja indisponivel.

## Regras

- Prazo de devolucao: 7 dias corridos a partir do registro do emprestimo.
- Pendencia de ATRASO e derivada dos emprestimos em aberto vencidos; nao existe
  como linha na tabela `pendencias` e deixa de existir quando o item e devolvido.
- Pendencia de DANO e criada apenas quando a devolucao informa `com_dano: true`,
  e so sai de aberta pelo endpoint de quitacao.
- Devolucao com dano leva o equipamento para INDISPONIVEL; sem dano, para
  DISPONIVEL.
