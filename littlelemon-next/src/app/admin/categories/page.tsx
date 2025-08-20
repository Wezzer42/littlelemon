"use client";
import ManagerGuard from "@/components/ManagerGuard";
import { api } from "@/lib/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

export default function AdminCategories() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["categories"], queryFn: async () => (await api.get("/api/categories")).data });
  const [title, setTitle] = useState("");

  const create = useMutation({
    mutationFn: () => api.post("/api/categories", { title }),
    onSuccess: () => { setTitle(""); qc.invalidateQueries({ queryKey: ["categories"] }); },
  });

  const list = Array.isArray(data) ? data : data?.results ?? [];

  return (
    <ManagerGuard>
      <div className="llem-card">
        <h2 className="llem-dish__title">Categories</h2>
        <div className="mt-3" style={{ display: "flex", gap: 8 }}>
          <input className="llem-input" placeholder="New category title" value={title} onChange={e=>setTitle(e.target.value)}/>
          <button className="llem-btn llem-btn--accent" onClick={()=>title && create.mutate()}>Add</button>
        </div>
        <ul className="mt-3" style={{ columns: 2 }}>
          {list.map((c: any) => (<li key={c.id} style={{ padding: 6 }}>{c.title}</li>))}
        </ul>
      </div>
    </ManagerGuard>
  );
}
