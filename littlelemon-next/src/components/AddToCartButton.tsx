"use client";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { addToCart } from "@/lib/cart";
import { useRouter } from "next/navigation";

export default function AddToCartButton({ id }: { id: number }) {
  const qc = useQueryClient();
  const router = useRouter();
  const m = useMutation({
    mutationFn: () => addToCart(id, 1),
    onSuccess: () => {
      // обновим корзину, если открыта где-то
      qc.invalidateQueries({ queryKey: ["cart"] });
    },
    onError: (err: any) => {
      if (err?.response?.status === 401) router.push("/login");
    },
  });

  return (
    <button
      className="llem-btn llem-btn--accent mt-3"
      disabled={m.isPending}
      onClick={() => m.mutate()}
    >
      {m.isPending ? "Adding…" : m.isSuccess ? "Added!" : "Add to cart"}
    </button>
  );
}