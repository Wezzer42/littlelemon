"use client";
import ManagerGuard from "@/components/ManagerGuard";
import { api } from "@/lib/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

export default function AdminOrders() {
  const qc = useQueryClient();
  const { data: orders } = useQuery({ queryKey: ["orders-all"], queryFn: async () => (await api.get("/api/orders")).data });
  const { data: crew } = useQuery({ queryKey: ["delivery-crew"], queryFn: async () => (await api.get("/api/groups/delivery-crew/users")).data });

  const list = Array.isArray(orders) ? orders : orders?.results ?? [];
  const people = Array.isArray(crew) ? crew : crew?.results ?? crew ?? [];

  const patch = useMutation({
    mutationFn: (payload: { id: number; delivery_crew_id?: number; status?: number }) =>
      api.patch(`/api/orders/${payload.id}`, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["orders-all"] }),
  });

  return (
    <ManagerGuard>
      <div className="llem-card">
        <h2 className="llem-dish__title">Orders</h2>
        <div className="mt-3" style={{ display: "grid", gap: 12 }}>
          {list.map((o: any) => (
            <div key={o.id} className="llem-card" style={{ padding: 12 }}>
              <div style={{ display: "flex", gap: 12, alignItems: "center", justifyContent: "space-between" }}>
                <div>
                  <div className="text-brand">Order #{o.id}</div>
                  <div className="llem-price">${o.total}</div>
                </div>
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <select
                    className="llem-select"
                    defaultValue={o.delivery_crew?.id ?? ""}
                    onChange={(e)=> patch.mutate({ id: o.id, delivery_crew_id: Number(e.target.value), status: o.status })}
                  >
                    <option value="">Assign courier…</option>
                    {people.map((u: any)=> (<option key={u.id} value={u.id}>{u.username}</option>))}
                  </select>
                  <select
                    className="llem-select"
                    defaultValue={o.status}
                    onChange={(e)=> patch.mutate({ id: o.id, status: Number(e.target.value), delivery_crew_id: o.delivery_crew?.id })}
                  >
                    <option value={0}>In progress</option>
                    <option value={1}>Delivered</option>
                  </select>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </ManagerGuard>
  );
}
