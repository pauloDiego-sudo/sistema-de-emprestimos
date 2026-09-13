Quem opera: técnico no balcão (pois no pedido infere-se que tem um técnico envolvido no acao de emprestimo, e tambem isso adiciona uma camada de verificacao, a humana)

Modelo de equipamento: item unico com n de patrimonio (pois fica mais facil rastrear qual equipamento de qual modelo esta com quem)

Identidade do aluno: id interno + matrícula única (ficaria mais facil a migracao das FKs, eu acredito)

O que consta como pendencia: Atraso ou dano, ou ambos (o atraso eh facil de identificar, ja o dano deve ser identificado visualmente, por exemplo, se o material ainda funciona ou n, entao deveria eh pertinente usar a tabela pendencias com dano e atraso, com motivo em aberto)

## IA
Registrar o operador como um campo simples:  
    - Se dois técnicos usam o balcão e um item some, o registro não diz quem operou. Isso tensiona diretamente o "não queremos que os equipamentos sumam" do pedido.