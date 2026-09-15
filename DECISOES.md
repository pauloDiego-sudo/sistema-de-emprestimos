## 1. Decisões assumidas

### 1.1 Quem opera o sistema

O pedido não especifica quem usa o sistema, se seria o aluno, o técnico ou os dois. Assumi que só o técnico opera, no balcão, e que o aluno nunca acessa o sistema. O pedido cita um técnico, e ter uma pessoa no balcão acrescenta uma verificação humana a cada empréstimo. Se o cliente esperasse que o próprio aluno registrasse o empréstimo, o impacto seria de criar login de aluno (hoje a API não tem autenticação nenhuma), impedir que um aluno registre empréstimo em nome de outro, criar telas para o aluno, e fazer o campo `operador` vir do usuário logado em vez de ser digitado.

### 1.2 Identificação de quem operou

O pedido não especifica se é preciso saber qual técnico fez cada operação. Assumi que cada empréstimo e cada devolução gravam o nome do operador digitado como texto livre, sem login e sem cadastro de técnicos (colunas `operador_emprestimo` e `operador_devolucao` em `emprestimos`). O sistema grava o nome, mas não confere se é verdadeiro: um técnico pode digitar o nome do colega, errar a grafia ("Joao" e "João" viram duas pessoas) ou escrever qualquer coisa. Como o operador é só texto, um técnico que também é aluno e tem pendência continua podendo registrar empréstimos para outros alunos, porque o bloqueio vale só para quem recebe o equipamento. Se o cliente esperasse saber com certeza quem operou quando um item some, o impacto seria ter que criar a tabela `tecnicos` e um login, e trocar as duas colunas de texto por FKs para `tecnicos.id`. Os registros antigos, em texto livre, não teriam como ser convertidos com segurança. Uma lista fixa de nomes, sem login, acabaria com os erros de grafia, mas não impediria ninguém de escolher o nome do outro.

### 1.3 Equipamento: peça individual ou quantidade

O pedido não especifica se um equipamento é uma peça individual ou um tipo com estoque. Assumi item único, identificado pelo número de patrimônio (`patrimonio` UNIQUE em `equipamentos`), com estado DISPONIVEL, EMPRESTADO ou INDISPONIVEL, porque assim se sabe exatamente qual peça está com quem. Por isso não existe "quantidade zero": pedir um item que não está disponível é recusado com 409 `EQUIPAMENTO_EMPRESTADO` ou `EQUIPAMENTO_INDISPONIVEL`. Se o cliente esperasse controlar itens por quantidade (ex.: "12 cabos jumper"), o impacto seria: `equipamentos` ganharia uma coluna de quantidade e perderia o estado por item; `emprestimos` ganharia quantidade; seria preciso tratar devolução parcial; e as rotas, que hoje identificam o equipamento pelo patrimônio, mudariam.

### 1.4 Identidade do aluno

O pedido não especifica como o aluno é identificado. Assumi um id interno inteiro como chave primária e a matrícula como coluna UNIQUE. Todas as FKs apontam para o id, mas as rotas usam a matrícula. Assim, mudar a matrícula de um aluno não obriga a mexer nas FKs. Se o cliente esperasse que o mesmo aluno pudesse ter mais de uma matrícula (ex.: técnico integrado e depois graduação) e que a pendência o acompanhasse, o impacto seria: criar uma tabela de matrículas ligada a `alunos.id` e mudar `buscar_aluno` para procurar nela. `emprestimos` e `pendencias` não mudariam, porque já apontam para o id interno.

### 1.5 Cadastro de alunos e equipamentos

O pedido não especifica como alunos e equipamentos entram no sistema. Assumi que não há cadastro pela API nem pelas telas, eles entram só pelo `seed.py` ou direto no banco. Se o cliente esperasse que o técnico cadastrasse um aluno novo no balcão, o impacto seria ter que criar `POST /alunos` e `POST /equipamentos`, duas telas novas e códigos de erro para matrícula e patrimônio repetidos. Hoje, um aluno que não está no banco recebe 404 `ALUNO_NAO_ENCONTRADO` e não consegue pegar nada.

### 1.6 O que conta como pendência

O pedido diz que aluno com pendência não pode pegar nada, mas não diz o que é pendência. Assumi dois tipos, atraso e dano, que podem aparecer juntos (motivo `ATRASO_E_DANO`). O atraso é fácil de identificar pela data, então é calculado na hora a partir dos empréstimos em aberto já vencidos, sem ser gravado. O dano precisa ser constatado por uma pessoa (ex.: se o equipamento ainda funciona), então é gravado na tabela `pendencias`, com data de abertura, data de quitação e motivo. Consequência: quando o aluno devolve um item atrasado, o atraso desaparece e ele volta a poder pegar equipamentos, sem registro de que atrasou. Se o cliente esperasse punir o atraso depois da devolução (ex.: suspensão de 7 dias) ou incluir outros tipos (perda, multa), o impacto seria: gravar o atraso em `pendencias` no momento da devolução, com data de fim ou quitação; mudar `motivo_bloqueio` e a listagem de pendências; e acrescentar os novos tipos ao enum `TipoPendencia`.

### 1.7 Como o dano é registrado

O pedido não especifica quem decide que houve dano, nem quando. Assumi que o técnico marca o dano no ato da devolução (`com_dano: true`) e que o sistema nunca infere dano sozinho. A pendência de dano guarda o aluno, mas não o empréstimo nem o equipamento que a originou. Se o cliente esperasse registrar um dano descoberto depois (ex.: o técnico testa o equipamento no dia seguinte), o impacto seria: acrescentar `emprestimo_id` à tabela `pendencias` e criar um endpoint para abrir pendência de dano sobre um empréstimo já encerrado. Hoje, depois de uma devolução registrada sem dano, não há como voltar atrás.

### 1.8 Destino do equipamento danificado

O pedido não especifica o que acontece com um equipamento devolvido com dano. Assumi que ele passa para INDISPONIVEL e que não existe operação para voltar a DISPONIVEL; quitar a pendência do aluno não muda o estado do equipamento. Se o cliente esperasse que o item voltasse ao acervo depois do conserto, o impacto seria: criar um endpoint e uma tela para mudar o estado de INDISPONIVEL para DISPONIVEL. Hoje isso só se faz editando o banco. (Decisão tomada pela IA, detalhada na seção 4.2.)

### 1.9 Prazo de devolução

O pedido não especifica o prazo nem quando o atraso começa. Assumi 7 dias corridos, iguais para todos os equipamentos, contados do instante do registro, um empréstimo das 09:12 vence às 09:12 do mesmo dia da semana seguinte, sem tolerância. Se o cliente esperasse outro prazo único, o impacto seria só trocar a constante `PRAZO_DIAS` nas regras de negócio. Se esperasse prazos diferentes por equipamento (ex.: notebook 1 dia, multímetro 14 dias), `equipamentos` ganharia uma coluna de prazo e `calcular_vencimento` passaria a lê-la. Se esperasse "até o fim do sétimo dia" ou que feriados adiassem o prazo, seria preciso introduzir o fuso America/Fortaleza no backend e um calendário de dias sem expediente. (A forma de contar o prazo foi decisão da IA, detalhada na seção 4.1.)

### 1.10 Quantos equipamentos um aluno pode ter ao mesmo tempo

O pedido não especifica um limite. Assumi que não há limite, um aluno sem pendência pode pegar quantos equipamentos quiser, e só a pendência bloqueia. Se o cliente esperasse um limite (ex.: um item por vez), o impacto seria ter q acrescentar em `registrar_emprestimo` uma contagem dos empréstimos em aberto do aluno e um novo código de recusa (ex.: 409 `LIMITE_DE_EMPRESTIMOS`), documentado no README.

### 1.11 Repetição da mesma operação

O pedido não especifica o que acontece quando a mesma operação é feita duas vezes. Assumi que a repetição é recusada com 409 e nada é alterado: emprestar um item já emprestado dá `EQUIPAMENTO_EMPRESTADO`, devolver um item que não está emprestado dá `EQUIPAMENTO_NAO_EMPRESTADO` e quitar uma pendência já quitada dá `PENDENCIA_JA_QUITADA`. Se o cliente esperasse que a repetição fosse aceita como sucesso (ex.: a rede cai, o técnico clica de novo em "Registrar devolução" e espera ver a confirmação, não um erro), o impacto seria: `registrar_devolucao` teria que localizar o último empréstimo encerrado daquele equipamento e responder com ele, e o frontend deixaria de mostrar esse caso como recusa.

### 1.12 Dois técnicos ao mesmo tempo

O pedido não especifica se há mais de um ponto de atendimento. Assumi um único balcão e não tratamos concorrência, `registrar_emprestimo` primeiro lê o estado do equipamento e só depois grava, e nada no banco impede dois empréstimos em aberto do mesmo equipamento. Se dois técnicos emprestarem o mesmo patrimônio no mesmo instante, os dois podem ser aceitos. Se o cliente esperasse dois balcões operando juntos, o impacto seria ter que criar um índice único parcial em `emprestimos(equipamento_id) WHERE devolvido_em IS NULL`, ou trocar a leitura por um `UPDATE equipamentos ... WHERE estado = 'DISPONIVEL'` que confira quantas linhas foram alteradas, e converter a violação em 409 `EQUIPAMENTO_EMPRESTADO`.

### 1.13 Erro do operador

O pedido não especifica como corrigir um registro feito errado. Assumi que não existe desfazer nem editar. Matrícula ou patrimônio que não existem são recusados com 404 e nada é gravado. Mas se o técnico digitar a matrícula de outro aluno que existe, o empréstimo fica no nome errado até alguém registrar a devolução. E se marcar dano por engano, a pendência só sai pela quitação (com um motivo como "registrado por engano") e o equipamento continua INDISPONIVEL. Nos dois casos, o erro fica no histórico. Se o cliente esperasse poder corrigir, o impacto seria: criar uma operação de estorno com endpoint e tela próprios, com uma coluna de cancelamento em `emprestimos` e em `pendencias` para não apagar o histórico. Também seria preciso decidir quem pode estornar, e sem login qualquer pessoa no balcão poderia fazer isso.

### 1.14 Conteúdo do relatório de atrasos

O pedido não especifica o que o relatório mostra. Assumi que ele lista só os empréstimos em aberto já vencidos, com aluno, equipamento, vencimento, dias de atraso e operador, calculados no momento da consulta. Quem já devolveu com atraso não aparece. Se o cliente esperasse um histórico (ex.: todos os atrasos do semestre, para advertir reincidentes), o impacto seria pequeno, porque `emprestimos` já guarda `vence_em` e `devolvido_em`, bastaria mudar a consulta de `relatorio_de_atrasos` para incluir empréstimos devolvidos depois do vencimento e aceitar um período como filtro.

### 1.15 Quitação da pendência de dano

O pedido não especifica como uma pendência de dano termina. Assumi um endpoint próprio que exige apenas um motivo em texto (`motivo_quitacao`). Ele não registra quem quitou, nem valor pago, nem exige que o equipamento tenha sido consertado. Se o cliente esperasse controlar o ressarcimento, o impacto seria: acrescentar a `pendencias` colunas para o operador da quitação e o valor, e decidir se a quitação devolve o equipamento a DISPONIVEL (ver 1.8).

## 2. Perguntas ao cliente

Escolhidas pelo impacto, levei em conta o fato onde cada resposta possível leva a um sistema diferente.

### Pergunta 1 - Os equipamentos são todos peças individuais, ou também há itens contados por quantidade (cabos, resistores, protoboards)?

| Resposta plausível | O que muda no sistema |
| --- | --- |
| Só peças individuais, com patrimônio | Nada. É o modelo atual (1.3). |
| Também há itens por quantidade, que voltam | Muda o modelo de dados: quantidade em `equipamentos` e em `emprestimos`, devolução parcial, e o patrimônio deixa de identificar o item. A regra de disponibilidade inteira é refeita. |
| Há itens que são consumidos e não voltam | Esses itens não cabem em "empréstimo". Seria preciso separá-los em um controle de estoque à parte, fora das regras de devolução e atraso. |

### Pergunta 2 - Depois que o aluno devolve um equipamento atrasado, ele continua bloqueado?

| Resposta plausível | O que muda no sistema |
| --- | --- |
| Não, o bloqueio acaba na devolução | Nada. É o comportamento atual (1.6). |
| Sim, fica suspenso por um tempo (ex.: tantos dias quanto atrasou) | O atraso passa a ser gravado em `pendencias` na devolução, com data de fim, e `motivo_bloqueio` passa a considerar essas linhas. |
| Sim, até o técnico liberar | Como no caso anterior, mas sem data de fim: a pendência de atraso ganha quitação manual, e o endpoint de quitação passa a aceitar os dois tipos. |

### Pergunta 3 - Até que momento o aluno pode devolver sem ser considerado atrasado?

| Resposta plausível | O que muda no sistema |
| --- | --- |
| Até o mesmo horário do empréstimo, sete dias depois | Nada. É o comportamento atual (seção 4.1). |
| Até o fim do sétimo dia, ou até o fechamento do laboratório nesse dia | `calcular_vencimento` passa a usar o fuso America/Fortaleza e a fixar a hora do vencimento; `dias_de_atraso` passa a contar por data. |
| Se o sétimo dia cair em feriado ou recesso, até o próximo dia com expediente | Além do caso anterior, o sistema precisa de um calendário de feriados e recesso, mantido pelo técnico. |

## 3. Critérios de aceite

Pré-condição de cada critério: API rodando em `http://localhost:8000` e banco recém-populado com `python seed.py`, executado na pasta `api`. Os três critérios usam dados diferentes do seed e podem ser executados em qualquer ordem.

### Critério 1 - Aluno com devolução vencida não recebe novo empréstimo

Entrada:

```bash
curl -i -X POST http://localhost:8000/emprestimos \
  -H 'Content-Type: application/json' \
  -d '{"matricula":"2023002","patrimonio":"PAT-004","operador":"Teste"}'
```

Resultado esperado: HTTP 409, corpo com `"codigo":"PENDENCIA"` e `"motivo":"ATRASO"`. Em seguida, `curl http://localhost:8000/emprestimos/abertos` não contém nenhum item com `"matricula":"2023002"` e `"patrimonio":"PAT-004"`.

### Critério 2 - Devolução com dano abre pendência e bloqueia o aluno

Entrada, dois comandos em sequência:

```bash
curl -i -X POST http://localhost:8000/devolucoes \
  -H 'Content-Type: application/json' \
  -d '{"patrimonio":"PAT-005","operador":"Teste","com_dano":true}'

curl -i -X POST http://localhost:8000/emprestimos \
  -H 'Content-Type: application/json' \
  -d '{"matricula":"2023001","patrimonio":"PAT-001","operador":"Teste"}'
```

Resultado esperado: o primeiro responde HTTP 201, com `"equipamento_estado":"INDISPONIVEL"` e `"pendencia_aberta"` contendo `"tipo":"DANO"` e `"matricula":"2023001"`. O segundo responde HTTP 409, com `"codigo":"PENDENCIA"` e `"motivo":"DANO"`.

### Critério 3 - O vencimento é 7 dias depois do empréstimo

Entrada:

```bash
curl -i -X POST http://localhost:8000/emprestimos \
  -H 'Content-Type: application/json' \
  -d '{"matricula":"2023004","patrimonio":"PAT-004","operador":"Teste"}'
```

Resultado esperado: HTTP 201. O campo `vence_em` tem a mesma hora, minuto e segundo de `emprestado_em`, com a data 7 dias depois (ex.: `2026-09-15T17:48:20Z` → `2026-09-22T17:48:20Z`).

## 4. Decisões da ferramenta de IA

Decisões que o assistente tomou sem que eu tivésse pedido, localizadas relendo o código gerado.

### 4.1 Quando um empréstimo passa a ser "atrasado"

Pedimos à IA apenas "prazo de devolução de 7 dias corridos", sem dizer a partir de que momento se conta, até que hora do sétimo dia o aluno pode devolver, nem se existe tolerância. A IA decidiu sozinha:

- O vencimento é o instante exato do registro mais 7 × 24 horas, com precisão de segundo. Um empréstimo registrado às 09:12 vence às 09:12 do mesmo dia da semana seguinte.
- O empréstimo fica atrasado no primeiro segundo depois do vencimento, sem tolerância.
- `dias_de_atraso` arredonda para cima: 1 segundo de atraso já conta como 1 dia.
- Tudo é calculado no relógio do servidor, em UTC.

**Por que é plausível.**

- É a leitura mais literal de "7 dias corridos": sete dias de 24 horas.
- Não depende de fuso horário. Instante + 168 horas é o mesmo instante em qualquer fuso, então guardar tudo em UTC não cria erro nenhum.
- É exato e dá para testar de fora: quem testa por HTTP consegue prever o segundo em que o aluno passa a ser bloqueado.
- Não exige configurar nada (horário do laboratório, calendário de feriados, fuso local).

**Por que pode estar inadequada para este cliente.**

1. **Prazo em hora quebrada.** Para o aluno e o técnico, "7 dias" quer dizer "até o dia 21", não "até as 09:12 do dia 21". Quem devolve na tarde do sétimo dia já aparece atrasado e bloqueado.
2. **Relatório inflado.** Com o arredondamento para cima, 5 horas de atraso viram "1 dia", e o relatório deixa de separar quem atrasou pouco de quem sumiu com o equipamento.
3. **Feriados.** Em 2026, 07/09, 12/10 e 02/11 caem numa segunda. Quem pegou o equipamento na segunda anterior tem o prazo vencendo com o laboratório fechado e fica bloqueado sem ter como devolver. O recesso tem o mesmo efeito.
4. **Sem gradação.** Um minuto de atraso bloqueia o aluno do mesmo jeito que um mês.
5. **Fuso.** "Até o fim do sétimo dia" teria que ser calculado no horário de Fortaleza (UTC−3). Em UTC, o dia acabaria às 21h no horário local. Guardar tudo em UTC fez da regra literal o caminho mais fácil.

Alternativas: vencer ao fim do sétimo dia (ou no fechamento do laboratório) no horário local; adiar o prazo para o próximo dia útil; contar o atraso por data civil; dar uma tolerância curta antes de bloquear. A pergunta correspondente ao cliente é a 3 da seção 2.

### 4.2 Devolução com dano torna o equipamento INDISPONIVEL

Em `registrar_devolucao`, uma devolução com `com_dano: true` põe o equipamento em INDISPONIVEL, sem dano, em DISPONIVEL. A IA não criou nenhuma operação para levar um equipamento de INDISPONIVEL de volta a DISPONIVEL.

**Por que é plausível.** Era a única regra que dava uso ao estado INDISPONIVEL, e ela impede que um item danificado seja emprestado de novo antes de ser examinado.

**Por que pode estar inadequada para este cliente.** Nem todo dano impede o uso (ex.: um arranhão na carcaça do notebook). Como não há caminho de volta, todo item danificado sai do acervo para sempre, a menos que alguém edite o banco: o técnico não consegue devolver ao uso um equipamento consertado. A regra também mistura duas coisas diferentes, o aluno ter causado dano (pendência) e o equipamento poder ser usado (estado).

### 4.3 Identificador inexistente responde 404, não 409

A instrução dada à IA dizia "toda recusa de operação responde HTTP 409". A IA usou 404 quando a matrícula, o patrimônio ou o id da pendência não existem e 422 para campo vazio ou malformado, mantendo o mesmo corpo `{codigo, motivo, mensagem}`.

**Por que é plausível.** É a convenção do HTTP: 404 significa que o recurso não existe, e 409 que a operação conflita com o estado atual. O corpo continua trazendo um código estável, então quem testa de fora ainda consegue distinguir cada caso.

**Por que pode estar inadequada para este cliente.** Os critérios de aceite serão executados por outra dupla, por HTTP. Quem ler "toda recusa responde 409" pode esperar 409 para uma matrícula inexistente e considerar o sistema errado. O README documenta os 404, mas a divergência com a instrução original existe.

## 5. Declaração de uso de IA

- **Ferramenta:** Claude Code, com o modelo Claude Opus 5, na extensão do VS Code.
- **Para quê:** gerar o código da aplicação (API, frontend, `seed.py` e READMEs), ajudar na escrita e estruturacao deste documento e avaliar decisões do sistema, inclusive as tomadas pela própria ferramenta (seção 4).
- **O que foi verificado manualmente:** o código gerado foi revisado e editado por mim antes de ser usado.
- **Testes executados por HTTP (curl) contra a API:** os três critérios da seção 3, cada código de erro da tabela do README e o caso de um técnico com pendência registrando empréstimo para outro aluno (1.2).

## Registro de tempo

Horas escrevendo ou gerando código: 1 hora.
- Horas revisando e editando codigo: 2 horas.

Horas decidindo o que o sistema deveria fazer: 45 minutos.

# Analise de decisões nos dois eixos (trabalho 2)

## Reversível: atraso arredondado para cima

Um segundo depois do vencimento já conta como 1 dia de atraso. Essa decisao esta no quadrante Ágil ( Incerteza ALTA  + iteração BARATA).

Não sabemos se o técnico aceita ler "1 dia" para 5 horas de atraso, mas o número é calculado na consulta, nunca gravado, e o bloqueio usa só `vence_em`.

Depois podemos acrescentar ao script de seed um empréstimo vencido há 5 horas, abrimos a rota de atrasos com o técnico e, se "1 dia" não for o que ele espera, trocamos a conta de dias de atraso na mesma sessão.

## Irreversível: operador gravado como texto livre

Cada empréstimo e cada devolução gravam o nome do operador digitado à mão, sem login nem cadastro de técnicos.

Essa decisão está no quadrante "Comprar informação antes" (Incerteza ALTA  + iteração CARÍSSIMA).

Não sabemos se o cliente vai precisar provar quem entregou um item que sumiu, e, após o primeiro registro real, "Joao", "João" ou o nome de um colega não viram FK para `tecnicos`, porque quem de fato operou nunca foi gravado.

Nenhum empréstimo real entra no banco, que continua só com o `seed.py`, até o cliente responder se precisa saber com certeza quem operou. Se sim, criamos `tecnicos` e trocamos as duas colunas por FK antes do primeiro registro no balcão. 

## Mesmo sistema, quadrantes diferentes

As duas decisões nascem do mesmo `POST /emprestimos`, ele grava `operador_emprestimo` e gera o `vence_em` de onde sai o atraso. Uma se testa e se desfaz em minutos; a outra deixa em cada linha do banco uma marca que não se apaga. Chamar o projeto de ágil ou de cascata erraria uma das duas, o processo certo depende de quanto custa voltar atrás em cada decisão.


