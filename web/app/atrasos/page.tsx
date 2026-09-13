"use client";

import { useEffect, useState } from "react";
import { AvisoErro, Voltar } from "@/app/componentes";
import { buscar, formatarDataHora, type ErroApi } from "@/lib/api";
import type { Atraso } from "@/lib/tipos";

export default function Atrasos() {
  const [itens, setItens] = useState<Atraso[] | null>(null);
  const [erro, setErro] = useState<ErroApi | null>(null);

  useEffect(() => {
    buscar<Atraso[]>("/atrasos").then((resultado) => {
      if (resultado.ok) setItens(resultado.dados);
      else setErro(resultado.erro);
    });
  }, []);

  return (
    <>
      <Voltar />
      <h1>Relatorio de atrasos</h1>
      <p className="subtitulo">Emprestimos em aberto com prazo vencido.</p>

      {erro && <AvisoErro erro={erro} />}
      {!erro && itens === null && <p className="vazio">Carregando...</p>}
      {itens !== null && itens.length === 0 && <p className="vazio">Nenhum atraso.</p>}

      {itens !== null && itens.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Patrimonio</th>
              <th>Equipamento</th>
              <th>Aluno</th>
              <th>Emprestado em</th>
              <th>Venceu em</th>
              <th>Dias de atraso</th>
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
                <td>{item.dias_de_atraso}</td>
                <td>{item.operador_emprestimo}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}
