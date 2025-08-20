"use client";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { isAuthed, logout } from "@/lib/auth";
import { useMe } from "@/lib/useMe";

export default function Navbar() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const authed = mounted && isAuthed();
  const { data: me } = useMe(authed);

  // cart count
  const { data: cart } = useQuery({
    queryKey: ["cart-count"],
    queryFn: async () => (await api.get("/api/cart/menu-items")).data,
    enabled: authed,
    staleTime: 30_000,
  });
  const count = Array.isArray(cart) ? cart.length : cart?.results?.length ?? 0;

  // dropdown
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const onDoc = (e: MouseEvent) => { if (menuRef.current && !menuRef.current.contains(e.target as Node)) setOpen(false); };
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("mousedown", onDoc);
    document.addEventListener("keydown", onKey);
    return () => { document.removeEventListener("mousedown", onDoc); document.removeEventListener("keydown", onKey); };
  }, []);

  if (!mounted) return <div className="h-14" />;

  return (
    <nav className="llem-navbar">
      <div className="llem-navbar__inner">
        {/* logo */}
        <Link href="/" className="llem-brand">
          <Image src="/brand/wordmark.png" alt="Little Lemon" width={140} height={40} priority />
        </Link>

        <div className="ml-auto flex items-center gap-2">
          {/* profile (avatar + name) */}
          <div ref={menuRef} className="relative">
            <button
              className="flex items-center gap-2 rounded-xl px-2 py-1 hover:bg-black/5"
              aria-haspopup="menu"
              aria-expanded={open}
              onClick={() => setOpen((v) => !v)}
            >
              <Avatar name={me?.username} />
              <span className="hidden sm:block">{authed ? me?.username : "Guest"}</span>
              <ChevronDownIcon className={`transition ${open ? "rotate-180" : ""}`} />
            </button>

            {open && (
              <div
                role="menu"
                className="absolute right-0 mt-2 w-56 overflow-hidden rounded-2xl border bg-white shadow-lg"
                style={{ borderColor: "var(--ll-border)" }}
              >
                {authed ? (
                  <>
                    <MenuLink href="/profile" label="Profile" onClick={() => setOpen(false)} />
                    <MenuLink href="/orders" label="My orders" onClick={() => setOpen(false)} />
                    <div className="border-t" style={{ borderColor: "var(--ll-border)" }} />
                    <button
                      role="menuitem"
                      className="block w-full px-3 py-2 text-left hover:bg-black/5"
                      onClick={async () => { await logout(); setOpen(false); router.push("/login"); }}
                    >
                      Logout
                    </button>
                  </>
                ) : (
                  <>
                    <MenuLink href="/login" label="Login" onClick={() => setOpen(false)} />
                    <MenuLink href="/register" label="Register" onClick={() => setOpen(false)} />
                  </>
                )}
              </div>
            )}
          </div>

          {/* shopping bag (cart) — справа от профиля */}
          <button
            className="relative rounded-xl p-2 hover:bg-black/5"
            aria-label="Cart"
            onClick={() => router.push("/cart")}
          >
            <ShoppingBagIcon />
            {authed && count > 0 && (
              <span className="absolute -top-1 -right-1 grid h-5 min-w-5 place-items-center rounded-full px-1 text-xs bg-lemon text-black">
                {count}
              </span>
            )}
          </button>
        </div>
      </div>
    </nav>
  );
}

function MenuLink({ href, label, onClick }: { href: string; label: string; onClick?: () => void }) {
  return (
    <Link href={href} role="menuitem" className="block px-3 py-2 hover:bg-black/5" onClick={onClick}>
      {label}
    </Link>
  );
}

function Avatar({ name, src }: { name?: string; src?: string }) {
  if (src) return <Image src={src} alt="" width={28} height={28} className="rounded-full" />;
  const initial = (name?.[0] ?? "U").toUpperCase();
  return <div className="grid h-7 w-7 place-items-center rounded-full bg-brand text-white text-sm">{initial}</div>;
}

function ChevronDownIcon({ className }: { className?: string }) {
  return (
    <svg className={className} width="16" height="16" viewBox="0 0 20 20" aria-hidden="true">
      <path d="M5 7l5 5 5-5" fill="none" stroke="currentColor" strokeWidth="2" />
    </svg>
  );
}

function ShoppingBagIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" {...props}>
      <path d="M6 7h12l-1 12a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2L6 7Z" stroke="currentColor" strokeWidth="1.8" />
      <path d="M9 7a3 3 0 1 1 6 0" stroke="currentColor" strokeWidth="1.8" />
    </svg>
  );
}
