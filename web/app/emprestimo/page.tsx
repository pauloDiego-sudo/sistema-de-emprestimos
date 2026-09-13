"use client";

import { useState } from "react";
import { AvisoErro, Voltar } from "@/app/componentes";
import { enviar, formatarDataHora, type ErroApi } from "@/lib/api";
import type { Emprestimo } from "@/lib/tipos";

export default function RegistrarEmprestimo() {
  const [matricula, setMatricula] = useState("");
  const [patrimonio, setPatrimonio] = useState("");
  const [operador, setOperador] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<ErroApi | null>(null);
  const [emprestimo, setEmprestimo] = useState<Emprestimo | null>(null);

  async function aoEnviar(evento: React.FormEvent) {
    evento.preventDefault();
    setEnviando(true);
    setErro(null);
    setEmprestimo(null);

    const resultado = await enviar<Emprestimo>("/emprestimos", {
      matricula,
      patrimonio,
      operador,
    });

    if (resultado.ok) {
      setEmprestimo(resultado.dados);
      setMatricula("");
      setPatrimonio("");
    } else {
      setErro(resultado.erro);
    }
    setEnviando(false);
  }

  return (
    <>
      <Voltar />
      <h1>Registrar emprestimo</h1>
      <p className="subtitulo">O prazo e definido pela API.</p>

      <form onSubmit={aoEnviar}>
        <label>
          Matricula do aluno
          <input
            type="text"
            required
            value={matricula}
            onChange={(e) => setMatricula(e.target.value)}
          />
        </label>
        <label>
          Patrimonio do equipamento
          <input
            type="text"
            required
            value={patrimonio}
            onChange={(e) => setPatrimonio(e.target.value)}
          />
        </label>
        <label>
          Operador
          <input
            type="text"
            required
            value={operador}
            onChange={(e) => setOperador(e.target.value)}
          />
        </label>
        <button type="submit" disabled={enviando}>
          {enviando ? "Registrando..." : "Registrar emprestimo"}
        </button>
      </form>

      {erro && <AvisoErro erro={erro} />}

      {emprestimo && (
        <div className="aviso aviso-ok">
          <p>
            Emprestimo {emprestimo.id} registrado para {emprestimo.nome} (
            {emprestimo.matricula}).
          </p>
          <dl>
            <div>
              Equipamento: {emprestimo.patrimonio} — {emprestimo.descricao}
            </div>
            <div>Emprestado em: {formatarDataHora(emprestimo.emprestado_em)}</div>
            <div>Vence em: {formatarDataHora(emprestimo.vence_em)}</div>
          </dl>
        </div>
      )}
    </>
  );
}
