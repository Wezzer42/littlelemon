"use client";
import ManagerGuard from "@/components/ManagerGuard";
import { api } from "@/lib/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import Image from "next/image";

export default function AdminMenu() {
  const qc = useQueryClient();
  const { data: cats } = useQuery({ queryKey: ["categories"], queryFn: async () => (await api.get("/api/categories")).data });
  const { data: items } = useQuery({ queryKey: ["menu"], queryFn: async () => (await api.get("/api/menu-items?ordering=-id")).data });

  const [title, setTitle] = useState("");
  const [price, setPrice] = useState("");
  const [category, setCategory] = useState<number | "">("");
  const [featured, setFeatured] = useState(false);
  const [file, setFile] = useState<File | null>(null);

  const create = useMutation({
    mutationFn: async () => {
      const fd = new FormData();
      fd.append("title", title);
      fd.append("price", price);
      fd.append("featured", String(featured));
      if (category) fd.append("category", String(category));
      if (file) fd.append("image", file);
      await api.post("/api/menu-items", fd, { headers: { "Content-Type": "multipart/form-data" } });
    },
    onSuccess: () => {
      setTitle(""); setPrice(""); setCategory(""); setFeatured(false); setFile(null);
      qc.invalidateQueries({ queryKey: ["menu"] });
    }
  });

  const list = Array.isArray(items) ? items : items?.results ?? [];
  const categories = Array.isArray(cats) ? cats : cats?.results ?? [];

  return (
    <ManagerGuard>
      <div className="llem-card">
        <h2 className="llem-dish__title">Menu</h2>

        <div className="mt-3" style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr auto auto auto", gap: 8 }}>
          <input className="llem-input" placeholder="Title" value={title} onChange={e=>setTitle(e.target.value)} />
          <input className="llem-input" placeholder="Price" value={price} onChange={e=>setPrice(e.target.value)} />
          <select className="llem-select" value={category} onChange={e=>setCategory(Number(e.target.value))}>
            <option value="">Category…</option>
            {categories.map((c: any) => <option key={c.id} value={c.id}>{c.title}</option>)}
          </select>
          <label style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <input type="checkbox" checked={featured} onChange={e=>setFeatured(e.target.checked)} /> Featured
          </label>
          <input className="llem-input" type="file" accept="image/*" onChange={(e)=>setFile(e.target.files?.[0] ?? null)} />
          <button className="llem-btn llem-btn--accent" onClick={()=>title && price && category && create.mutate()}>Add</button>
        </div>

        <div className="llem-grid mt-4">
          {list.map((m: any) => (
            <div key={m.id} className="llem-card">
              <div className="aspect-[4/3] overflow-hidden rounded-xl border" style={{borderColor: "var(--ll-border)"}}>
                {m.image ? (
                  <Image src={m.image} alt={m.title} width={600} height={450} className="h-full w-full object-cover"/>
                ) : (
                  <div className="h-full w-full grid place-items-center bg-[var(--ll-paper)] text-sm opacity-70">No image</div>
                )}
              </div>
              <div className="llem-dish__title mt-2">{m.title}</div>
              <div className="llem-price">${m.price}</div>
              <div style={{ fontSize: 12, opacity: .75 }}>#{m.id} • {m.featured ? "Featured" : "Regular"}</div>
            </div>
          ))}
        </div>
      </div>
    </ManagerGuard>
  );
}
