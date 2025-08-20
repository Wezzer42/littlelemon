export type Category = { id: number; title: string };
export type MenuItem = {
id: number; title: string; price: string; featured: boolean;
category: Category | number; inventory: number; image?: string | null; 
};
export type CartItem = {
id: number; quantity: number; unit_price: string; price: string; menuitem: MenuItem;
};
export type Order = {
id: number; status: number; total: string; date: string; delivery_crew?: { id: number; username: string } | null;
items?: CartItem[];
};
