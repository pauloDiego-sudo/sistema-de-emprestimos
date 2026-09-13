"use client";

import { useCallback, useEffect, useState } from "react";
import { AvisoErro, Voltar } from "@/app/componentes";
import { buscar, enviar, formatarDataHora, type ErroApi } from "@/lib/api";
import type { Pendencia, PendenciaAberta } from "@/lib/tipos";

export default function Pendencias() {
  const [itens, setItens] = useState<PendenciaAberta[] | null>(null);
  const [erro, setErro] = useState<ErroApi | null>(null);
  const [motivos, setMotivos] = useState<Record<number, string>>({});
  const [quitando, setQuitando] = useState<number | null>(null);
  const [quitada, setQuitada] = useState<Pendencia | null>(null);

  const carregar = useCallback(async () => {
    const resultado = await buscar<PendenciaAberta[]>("/pendencias/abertas");
    if (resultado.ok) {
      setItens(resultado.dados);
      setErro(null);
    } else {
      setErro(resultado.erro);
    }
  }, []);

  useEffect(() => {
    carregar();
  }, [carregar]);

  async function quitar(evento: React.FormEvent, id: number) {
    evento.preventDefault();
    setQuitando(id);
    setErro(null);
    setQuitada(null);

    const resultado = await enviar<Pendencia>(`/pendencias/${id}/quitacao`, {
      motivo_quitacao: motivos[id] ?? "",
    });

    if (resultado.ok) {
      setQuitada(resultado.dados);
      setMotivos((atual) => ({ ...atual, [id]: "" }));
      await carregar();
    } else {
      setErro(resultado.erro);
    }
    setQuitando(null);
  }

  return (
    <>
      <Voltar />
      <h1>Pendencias abertas</h1>
      <p className="subtitulo">Quitacao vale apenas para pendencia de dano.</p>

      {erro && <AvisoErro erro={erro} />}

      {quitada && (
        <div className="aviso aviso-ok">
          <p>
            Pendencia {quitada.id} de {quitada.nome} quitada em{" "}
            {quitada.quitada_em ? formatarDataHora(quitada.quitada_em) : "-"}.
          </p>
          <dl>
            <div>Motivo: {quitada.motivo_quitacao}</div>
          </dl>
        </div>
      )}

      {!erro && itens === null && <p className="vazio">Carregando...</p>}
      {itens !== null && itens.length === 0 && (
        <p className="vazio">Nenhuma pendencia aberta.</p>
      )}

      {itens?.map((item, indice) => (
        <div className="pendencia" key={item.id ?? `atraso-${indice}`}>
          <h2>
            {item.tipo} — {item.nome} ({item.matricula})
          </h2>
          <dl>
            <div>Aberta em: {formatarDataHora(item.aberta_em)}</div>
            {item.emprestimos_em_atraso.length > 0 && (
              <div>Equipamentos em atraso: {item.emprestimos_em_atraso.join(", ")}</div>
            )}
            {item.id !== null && <div>Id da pendencia: {item.id}</div>}
          </dl>

          {item.quitavel && item.id !== null && (
            <form onSubmit={(evento) => quitar(evento, item.id as number)}>
              <label>
                Motivo da quitacao
                <input
                  type="text"
                  required
                  value={motivos[item.id] ?? ""}
                  onChange={(e) =>
                    setMotivos((atual) => ({ ...atual, [item.id as number]: e.target.value }))
                  }
                />
              </label>
              <button type="submit" disabled={quitando === item.id}>
                {quitando === item.id ? "Quitando..." : "Quitar"}
              </button>
            </form>
          )}
        </div>
      ))}
    </>
  );
}
