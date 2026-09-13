"use client";

import { useEffect, useState } from "react";
import { AvisoErro, Voltar } from "@/app/componentes";
import { buscar, formatarDataHora, type ErroApi } from "@/lib/api";
import type { Emprestado } from "@/lib/tipos";

export default function Emprestados() {
  const [itens, setItens] = useState<Emprestado[] | null>(null);
  const [erro, setErro] = useState<ErroApi | null>(null);

  useEffect(() => {
    buscar<Emprestado[]>("/emprestimos/abertos").then((resultado) => {
      if (resultado.ok) setItens(resultado.dados);
      else setErro(resultado.erro);
    });
  }, []);

  return (
    <>
      <Voltar />
      <h1>Emprestados</h1>
      <p className="subtitulo">O que esta com aluno neste momento.</p>

      {erro && <AvisoErro erro={erro} />}
      {!erro && itens === null && <p className="vazio">Carregando...</p>}
      {itens !== null && itens.length === 0 && (
        <p className="vazio">Nenhum equipamento emprestado.</p>
      )}

      {itens !== null && itens.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Patrimonio</th>
              <th>Equipamento</th>
              <th>Aluno</th>
              <th>Emprestado em</th>
              <th>Vence em</th>
              <th>Situacao</th>
              <th>Operador</th>
            </tr>
          </thead>
          <tbody>
            {itens.map((item) => (
              <tr key={item.emprestimo_id}>
                <td>{item.patrimonio}</td>
                <td>{item.descricao}</td>
                <td>
                  {item.nome} ({item.matricula})
                </td>
                <td>{formatarDataHora(item.emprestado_em)}</td>
                <td>{formatarDataHora(item.vence_em)}</td>
                <td>{item.em_atraso ? `Em atraso (${item.dias_de_atraso} dia(s))` : "No prazo"}</td>
                <td>{item.operador_emprestimo}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}
