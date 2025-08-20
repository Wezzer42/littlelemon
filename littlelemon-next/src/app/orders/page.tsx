"use client";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Order } from "@/types/dto";
import Guard from "@/components/Guard";


async function myOrders() {
const { data } = await api.get("/api/orders");
return (Array.isArray(data) ? data : data.results) as Order[];
}


export default function OrdersPage() {
const { data, isLoading } = useQuery({ queryKey: ["orders"], queryFn: myOrders });
return (
<Guard>
<h1 className="text-xl font-semibold mb-3">My Orders</h1>
{isLoading ? "Loading…" : (
<div className="grid gap-2">
{data?.map((o) => (
<div key={o.id} className="border rounded p-2 flex justify-between">
<div>Order #{o.id}</div>
<div>${o.total}</div>
</div>
))}
</div>
)}
</Guard>
);
}