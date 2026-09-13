# Sistema de Emprestimos do Laboratorio

Controle de emprestimo dos equipamentos do laboratorio, operado pelo tecnico no
balcao. O backend fica em `api/` (Python + FastAPI + SQLite) e o frontend em
`web/` (Next.js). Todas as regras de negocio vivem no backend; o frontend apenas
envia a requisicao e mostra a resposta.

## Pre-requisitos

- Python 3.11 ou superior
- Node.js 20.9 ou superior (com npm)

## Instalacao

Backend:

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Frontend:

```bash
cd web
npm install
cp .env.example .env.local
```

`.env.local` define `NEXT_PUBLIC_API_URL`, a URL da API que o frontend consome.
O padrao e `http://localhost:8000`.

## Popular o banco

```bash
cd api
source .venv/bin/activate
python seed.py
```

O script recria `api/emprestimos.db` do zero e insere:

| Aluno | Matricula | Situacao |
| --- | --- | --- |
| Ana Ribeiro | `2023001` | sem pendencia, com um emprestimo dentro do prazo |
| Bruno Carvalho | `2023002` | emprestimo vencido em aberto (pendencia de ATRASO) |
| Carla Dias | `2023003` | pendencia de DANO em aberto (id 1) |
| Diego Lopes | `2023004` | pendencia de DANO ja quitada |

| Patrimonio | Equipamento | Estado |
| --- | --- | --- |
| `PAT-001` | Notebook Dell Latitude | DISPONIVEL |
| `PAT-002` | Projetor Epson PowerLite | EMPRESTADO |
| `PAT-003` | Multimetro Minipa ET-2042 | INDISPONIVEL |
| `PAT-004` | Osciloscopio Tektronix TBS1052 | DISPONIVEL |
| `PAT-005` | Kit Arduino Uno completo | EMPRESTADO |
| `PAT-006` | Fonte de bancada Instrutherm FA-3005 | INDISPONIVEL |

## Rodar

Sao dois terminais.

Terminal 1 — API em `http://localhost:8000`:

```bash
cd api
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Terminal 2 — frontend em `http://localhost:3000`:

```bash
cd web
npm run dev
```

O CORS da API libera apenas a origem do frontend. Se o Next subir em outra
porta, exporte `FRONTEND_ORIGIN` antes do uvicorn:

```bash
FRONTEND_ORIGIN=http://localhost:3001 uvicorn app.main:app --port 8000
```

## Telas

| Rota | Para que serve |
| --- | --- |
| `/` | navegacao |
| `/emprestimo` | registrar emprestimo |
| `/devolucao` | registrar devolucao, com ou sem dano |
| `/emprestados` | o que esta emprestado e para quem |
| `/atrasos` | relatorio de atrasos |
| `/pendencias` | pendencias abertas e quitacao de dano |

## Regras de negocio

- Prazo de devolucao: 7 dias corridos a partir do registro do emprestimo.
- Aluno com qualquer pendencia aberta (atraso, dano ou ambos) nao recebe novo
  emprestimo.
- A pendencia de ATRASO e derivada: calculada a partir do vencimento dos
  emprestimos em aberto, nunca gravada na tabela `pendencias`. Ela deixa de
  existir quando o equipamento e devolvido.
- A pendencia de DANO so nasce de um ato explicito do tecnico na devolucao
  (`com_dano: true`) e so termina pelo endpoint de quitacao.
- Devolucao com dano leva o equipamento para INDISPONIVEL; sem dano, para
  DISPONIVEL.
- Todo emprestimo e toda devolucao gravam o nome do operador. E registro, nao
  autenticacao: o sistema nao valida quem digitou.
- Datas e horas na API sao sempre UTC em ISO-8601 com sufixo `Z`.

## Codigos de erro

Toda recusa responde com este corpo:

```json
{"codigo": "<CODIGO>", "motivo": "<MOTIVO ou null>", "mensagem": "<texto>"}
```

| HTTP | codigo | motivo | Quando acontece |
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

No `POST /emprestimos` a pendencia do aluno e checada antes do estado do
equipamento: aluno bloqueado recebe `PENDENCIA` mesmo que o equipamento tambem
esteja indisponivel.

## As seis operacoes por curl

Os exemplos abaixo valem contra o banco recem-populado pelo `seed.py`.

### 1. Registrar emprestimo

```bash
curl -i -X POST http://localhost:8000/emprestimos \
  -H 'Content-Type: application/json' \
  -d '{"matricula":"2023001","patrimonio":"PAT-001","operador":"Tecnico Joao"}'
```

Responde `201` com o emprestimo criado, incluindo `vence_em`.

### 2. Registrar devolucao (com ou sem dano)

Sem dano — o equipamento volta para DISPONIVEL:

```bash
curl -i -X POST http://localhost:8000/devolucoes \
  -H 'Content-Type: application/json' \
  -d '{"patrimonio":"PAT-001","operador":"Tecnica Maria","com_dano":false}'
```

Com dano — abre pendencia de DANO para o aluno e o equipamento vai para
INDISPONIVEL:

```bash
curl -i -X POST http://localhost:8000/devolucoes \
  -H 'Content-Type: application/json' \
  -d '{"patrimonio":"PAT-005","operador":"Tecnica Maria","com_dano":true}'
```

### 3. Consultar o que esta emprestado e para quem

```bash
curl -i http://localhost:8000/emprestimos/abertos
```

### 4. Relatorio de atrasos

```bash
curl -i http://localhost:8000/atrasos
```

### 5. Bloqueio de emprestimo para aluno com pendencia

Bruno (`2023002`) tem emprestimo vencido — responde `409` com
`{"codigo":"PENDENCIA","motivo":"ATRASO",...}`:

```bash
curl -i -X POST http://localhost:8000/emprestimos \
  -H 'Content-Type: application/json' \
  -d '{"matricula":"2023002","patrimonio":"PAT-004","operador":"Tecnico Joao"}'
```

Carla (`2023003`) tem dano em aberto — mesmo `409`, com `"motivo":"DANO"`:

```bash
curl -i -X POST http://localhost:8000/emprestimos \
  -H 'Content-Type: application/json' \
  -d '{"matricula":"2023003","patrimonio":"PAT-004","operador":"Tecnico Joao"}'
```

### 6. Quitar pendencia de dano

A pendencia aberta de Carla tem id `1` no banco populado. Para descobrir os ids
em qualquer banco, use `curl http://localhost:8000/pendencias/abertas` — as
pendencias quitaveis sao as que trazem `id` preenchido e `"quitavel": true`.

```bash
curl -i -X POST http://localhost:8000/pendencias/1/quitacao \
  -H 'Content-Type: application/json' \
  -d '{"motivo_quitacao":"Equipamento reparado e custo pago pelo aluno"}'
```

Depois da quitacao, Carla volta a poder receber emprestimo.
