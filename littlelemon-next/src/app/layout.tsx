import "./globals.css";
import Providers from "./providers";
import dynamic from "next/dynamic";
import { Fraunces, Inter } from "next/font/google";
import Navbar from "@/components/Navbar";

const brand = Fraunces({ subsets: ["latin"], weight: ["600","700","900"], variable: "--font-fraunces" });
const ui = Inter({ subsets: ["latin"], variable: "--font-geist-sans" });


export const metadata = { title: "Little Lemon" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${brand.variable} ${ui.variable}`}>
      <body className="bg-background text-foreground font-sans">
        <Providers>
          <Navbar />
          <main className="max-w-5xl mx-auto p-4">{children}</main>
        </Providers>
      </body>
    </html>
  );
}