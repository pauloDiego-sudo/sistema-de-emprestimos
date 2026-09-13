const BASE_URL = process.env.NEXT_PUBLIC_API_URL;

export type ErroApi = {
  codigo: string;
  motivo: string | null;
  mensagem: string;
};

export type Resultado<T> =
  | { ok: true; dados: T }
  | { ok: false; erro: ErroApi };

async function requisitar<T>(caminho: string, init?: RequestInit): Promise<Resultado<T>> {
  let resposta: Response;
  try {
    resposta = await fetch(`${BASE_URL}${caminho}`, init);
  } catch {
    return {
      ok: false,
      erro: {
        codigo: "API_INACESSIVEL",
        motivo: null,
        mensagem: `Nao foi possivel falar com a API em ${BASE_URL}.`,
      },
    };
  }

  const corpo = await resposta.json().catch(() => null);

  if (!resposta.ok) {
    const erro = corpo as ErroApi | null;
    return {
      ok: false,
      erro: erro?.codigo
        ? erro
        : {
            codigo: `HTTP_${resposta.status}`,
            motivo: null,
            mensagem: `A API respondeu ${resposta.status}.`,
          },
    };
  }

  return { ok: true, dados: corpo as T };
}

export function buscar<T>(caminho: string): Promise<Resultado<T>> {
  return requisitar<T>(caminho, { cache: "no-store" });
}

export function enviar<T>(caminho: string, corpo: unknown): Promise<Resultado<T>> {
  return requisitar<T>(caminho, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(corpo),
  });
}

export function formatarDataHora(iso: string): string {
  return new Date(iso).toLocaleString("pt-BR");
}
