import { api } from "@/lib/api";

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