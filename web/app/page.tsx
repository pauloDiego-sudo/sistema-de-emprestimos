import Link from "next/link";

const telas = [
  { href: "/emprestimo", titulo: "Registrar emprestimo", ajuda: "Aluno leva um equipamento." },
  { href: "/devolucao", titulo: "Registrar devolucao", ajuda: "Aluno devolve, com ou sem dano." },
  { href: "/emprestados", titulo: "Emprestados", ajuda: "O que esta emprestado e para quem." },
  { href: "/atrasos", titulo: "Atrasos", ajuda: "Relatorio de devolucoes vencidas." },
  { href: "/pendencias", titulo: "Pendencias", ajuda: "Pendencias abertas e quitacao de dano." },
];

export default function Inicio() {
  return (
    <>
      <h1>Emprestimos do Laboratorio</h1>
      <p className="subtitulo">Balcao do tecnico.</p>
      <ul className="navegacao">
        {telas.map((tela) => (
          <li key={tela.href}>
            <Link href={tela.href}>
              {tela.titulo}
              <span>{tela.ajuda}</span>
            </Link>
          </li>
        ))}
      </ul>
    </>
  );
}
