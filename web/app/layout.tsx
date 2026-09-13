import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Emprestimos do Laboratorio",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>
        <main>{children}</main>
      </body>
    </html>
  );
}
