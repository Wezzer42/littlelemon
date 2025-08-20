"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { CartItem } from "@/types/dto";
import Guard from "@/components/Guard";


async function getCart() {
const { data } = await api.get("/api/cart/menu-items");
return data as CartItem[];
}
async function removeCartItem(id: number) {
await api.delete(`/api/cart/menu-items/${id}`);
}

export async function addToCart(menuitemId: number, quantity = 1) {
  try {
    await api.post("/api/cart/menu-items", { menuitem: menuitemId, quantity });
  } catch (err: any) {
    if (err?.response?.status === 400) {
      await api.post("/api/cart/menu-items", { menuitem_id: menuitemId, quantity });
      return;
    }
    throw err;
  }
}

export default function CartPage() {
const qc = useQueryClient();
const { data, isLoading } = useQuery({ queryKey: ["cart"], queryFn: getCart });
const m = useMutation({
mutationFn: removeCartItem,
onSuccess: () => qc.invalidateQueries({ queryKey: ["cart"] }),
});


return (
<Guard>
<h1 className="text-xl font-semibold mb-3">Cart</h1>
{isLoading ? "Loading…" : (
<div className="grid gap-2">
{data?.map((ci) => (
<div key={ci.id} className="border rounded p-2 flex justify-between">
<div>
<div className="font-medium">{ci.menuitem.title}</div>
<div className="text-sm opacity-70">x{ci.quantity} • ${ci.price}</div>
</div>
<button className="border px-2 rounded" onClick={() => m.mutate(ci.id)}>Remove</button>
</div>
))}
</div>
)}
</Guard>
);
}