export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <section className="container mt-4">
      <div className="llem-card" style={{ padding: 12 }}>
        <nav style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <a href="/admin" className="llem-btn llem-btn--outline">Dashboard</a>
          <a href="/admin/menu" className="llem-btn llem-btn--outline">Menu</a>
          <a href="/admin/categories" className="llem-btn llem-btn--outline">Categories</a>
          <a href="/admin/orders" className="llem-btn llem-btn--outline">Orders</a>
        </nav>
      </div>
      <div className="mt-4">{children}</div>
    </section>
  );
}
