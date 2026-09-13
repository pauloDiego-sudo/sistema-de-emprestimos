"use client";

import Link from "next/link";
import type { ErroApi } from "@/lib/api";

export function Voltar() {
  return (
    <Link className="voltar" href="/">
      &larr; Inicio
    </Link>
  );
}

export function AvisoErro({ erro }: { erro: ErroApi }) {
  return (
    <div className="aviso aviso-erro">
      <p>{erro.mensagem}</p>
      <dl>
        <div>
          codigo: <span className="codigo">{erro.codigo}</span>
        </div>
        <div>
          motivo: <span className="codigo">{erro.motivo ?? "null"}</span>
        </div>
      </dl>
    </div>
  );
}
