import { MenuItem } from "@/types/dto";
import Image from "next/image";
import AddToCartButton from "@/components/AddToCartButton";
import Hero from "@/components/Hero";

export const revalidate = 60;


export default async function Home() {
const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/menu-items`, { next: { revalidate } });
const data = await res.json();
const items: MenuItem[] = Array.isArray(data) ? data : data.results ?? [];


return (
<>
<Hero />
<div className="grid grid-cols-2 md:grid-cols-3 gap-4">
{items.map((it) => (
<div key={it.id} className="llem-card">
  <div className="aspect-[4/3] overflow-hidden rounded-xl border" style={{borderColor: "var(--ll-border)"}}>
    {it.image ? (
      <Image src={it.image} alt={it.title} width={600} height={450} className="h-full w-full object-cover"/>
    ) : (
      <div className="h-full w-full grid place-items-center bg-[var(--ll-paper)] text-sm opacity-70">No image</div>
    )}
  </div>
  <div className="llem-dish__title mt-2">{it.title}</div>
  <div className="llem-price">${it.price}</div>
  <AddToCartButton id={it.id} />
</div>
))}
</div>
</>
);
}