Quem opera: técnico no balcão (pois no pedido infere-se que tem um técnico envolvido no acao de emprestimo, e tambem isso adiciona uma camada de verificacao, a humana)

Modelo de equipamento: item unico com n de patrimonio (pois fica mais facil rastrear qual equipamento de qual modelo esta com quem)

Identidade do aluno: id interno + matrícula única (ficaria mais facil a migracao das FKs, eu acredito)

O que consta como pendencia: Atraso ou dano, ou ambos (o atraso eh facil de identificar, ja o dano deve ser identificado visualmente, por exemplo, se o material ainda funciona ou n, entao deveria eh pertinente usar a tabela pendencias com dano e atraso, com motivo em aberto)

## IA
Registrar o operador como um campo simples:

- O que é: em cada empréstimo e devolução, o técnico digita o próprio nome num campo de texto. Não há login nem cadastro de técnicos.
- Por que faz sentido: é rápido no balcão e deixa registrado quem fez cada operação, sem criar um sistema de usuários.
- O problema: o sistema grava o nome digitado, mas não confere se ele é verdadeiro. Um técnico pode digitar o nome do colega, errar a grafia ("Joao" e "João" viram duas pessoas) ou escrever qualquer coisa. Se um item some, o registro mostra um nome, mas não garante que foi essa pessoa quem operou. Isso enfraquece o "não queremos que os equipamentos sumam" do pedido.
- Melhoria possível sem login: trocar o texto livre por uma lista fixa de técnicos. Isso acaba com os erros de grafia, mas não impede ninguém de escolher o nome do outro.

### Quando um empréstimo passa a ser "atrasado" (decisão da IA, não solicitada)

O pedido nao especificava quando um empréstimo passa a ser considerado atrasado. A IA decidiu sozinha:

O pedido dizia só "prazo de devolução: 7 dias corridos". Não dizia a partir de que momento se conta, até que hora do sétimo dia o aluno pode devolver, nem se existe tolerância. A IA decidiu sozinha:

- O vencimento é o instante exato do registro mais 7 × 24 horas, com precisão de segundo (`api/app/regras.py:21`). Empréstimo registrado às 09:12 vence às 09:12 do mesmo dia da semana seguinte.
- O empréstimo fica atrasado no primeiro segundo depois do vencimento, sem tolerância (`vence_em < referencia`, `api/app/regras.py:61` e `:211`).
- `dias_de_atraso` arredonda para cima: 1 segundo de atraso já conta como 1 dia (`api/app/regras.py:27`).
- Tudo é calculado no relógio do servidor, em UTC (`api/app/models.py:11`).

Por que é plausível:
- É a leitura mais literal de "7 dias corridos": sete dias de 24 horas.
- Não depende de fuso horário. Instante + 168 horas é o mesmo instante em qualquer fuso, então guardar tudo em UTC não cria erro nenhum.
- É exato e dá para testar de fora: quem testa por HTTP consegue prever o segundo em que o aluno passa a ser bloqueado.
- Não exige configurar nada (horário do laboratório, calendário de feriados, fuso local).

Por que pode estar inadequada para este cliente:

1. **Prazo em hora quebrada.** Para o aluno e o técnico, "7 dias" quer dizer "até o dia 21", não "até as 09:12 do dia 21". Quem devolve na tarde do sétimo dia já aparece atrasado e bloqueado.
2. **Relatório inflado.** Com o arredondamento para cima, 5 horas de atraso viram "1 dia", e o relatório deixa de separar quem atrasou pouco de quem sumiu com o equipamento.
3. **Feriados.** Em 2026, 07/09, 12/10 e 02/11 caem numa segunda. Quem pegou o equipamento na segunda anterior tem o prazo vencendo com o laboratório fechado e fica bloqueado sem ter como devolver. O recesso tem o mesmo efeito.
4. **Sem gradação.** Um minuto de atraso bloqueia o aluno do mesmo jeito que um mês.
5. **Fuso.** "Até o fim do sétimo dia" teria que ser calculado no horário de Fortaleza (UTC−3). Em UTC, o dia acabaria às 21h no horário local. Guardar tudo em UTC fez da regra literal o caminho mais fácil.

Alternativas: vencer ao fim do sétimo dia (ou no fechamento do laboratório) no horário local; adiar o prazo para o próximo dia útil; contar o atraso por data civil; dar uma tolerância curta antes de bloquear.

Perguntas para o cliente: até que horas vale a devolução no sétimo dia? E se o prazo cair num dia sem expediente? Poucas horas de atraso devem bloquear como semanas?
