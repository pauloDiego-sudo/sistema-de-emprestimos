export type Emprestimo = {
  id: number;
  matricula: string;
  nome: string;
  patrimonio: string;
  descricao: string;
  emprestado_em: string;
  vence_em: string;
  devolvido_em: string | null;
  operador_emprestimo: string;
  operador_devolucao: string | null;
};

export type Pendencia = {
  id: number;
  matricula: string;
  nome: string;
  tipo: string;
  aberta_em: string;
  quitada_em: string | null;
  motivo_quitacao: string | null;
};

export type Devolucao = {
  emprestimo: Emprestimo;
  equipamento_estado: string;
  pendencia_aberta: Pendencia | null;
};

export type Emprestado = {
  emprestimo_id: number;
  patrimonio: string;
  descricao: string;
  matricula: string;
  nome: string;
  emprestado_em: string;
  vence_em: string;
  em_atraso: boolean;
  dias_de_atraso: number;
  operador_emprestimo: string;
};

export type Atraso = {
  emprestimo_id: number;
  patrimonio: string;
  descricao: string;
  matricula: string;
  nome: string;
  emprestado_em: string;
  vence_em: string;
  dias_de_atraso: number;
  operador_emprestimo: string;
};

export type PendenciaAberta = {
  id: number | null;
  matricula: string;
  nome: string;
  tipo: string;
  aberta_em: string;
  quitada_em: string | null;
  motivo_quitacao: string | null;
  quitavel: boolean;
  emprestimos_em_atraso: string[];
};
