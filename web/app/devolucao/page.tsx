"use client";

import { useState } from "react";
import { AvisoErro, Voltar } from "@/app/componentes";
import { enviar, formatarDataHora, type ErroApi } from "@/lib/api";
import type { Devolucao } from "@/lib/tipos";

export default function RegistrarDevolucao() {
  const [patrimonio, setPatrimonio] = useState("");
  const [operador, setOperador] = useState("");
  const [comDano, setComDano] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<ErroApi | null>(null);
  const [devolucao, setDevolucao] = useState<Devolucao | null>(null);

  async function aoEnviar(evento: React.FormEvent) {
    evento.preventDefault();
    setEnviando(true);
    setErro(null);
    setDevolucao(null);

    const resultado = await enviar<Devolucao>("/devolucoes", {
      patrimonio,
      operador,
      com_dano: comDano,
    });

    if (resultado.ok) {
      setDevolucao(resultado.dados);
      setPatrimonio("");
      setComDano(false);
    } else {
      setErro(resultado.erro);
    }
    setEnviando(false);
  }

  return (
    <>
      <Voltar />
      <h1>Registrar devolucao</h1>
      <p className="subtitulo">Marque o dano apenas se o tecnico constatou dano.</p>

      <form onSubmit={aoEnviar}>
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
        <label className="caixa-checkbox">
          <input
            type="checkbox"
            checked={comDano}
            onChange={(e) => setComDano(e.target.checked)}
          />
          Devolvido com dano
        </label>
        <button type="submit" disabled={enviando}>
          {enviando ? "Registrando..." : "Registrar devolucao"}
        </button>
      </form>

      {erro && <AvisoErro erro={erro} />}

      {devolucao && (
        <div className="aviso aviso-ok">
          <p>
            Devolucao do equipamento {devolucao.emprestimo.patrimonio} registrada para{" "}
            {devolucao.emprestimo.nome} ({devolucao.emprestimo.matricula}).
          </p>
          <dl>
            <div>
              Devolvido em:{" "}
              {devolucao.emprestimo.devolvido_em
                ? formatarDataHora(devolucao.emprestimo.devolvido_em)
                : "-"}
            </div>
            <div>Estado do equipamento: {devolucao.equipamento_estado}</div>
            <div>
              Pendencia de dano:{" "}
              {devolucao.pendencia_aberta
                ? `aberta (id ${devolucao.pendencia_aberta.id})`
                : "nenhuma"}
            </div>
          </dl>
        </div>
      )}
    </>
  );
}
