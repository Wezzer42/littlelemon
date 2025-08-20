import Image from "next/image";
import Link from "next/link";

export default function Hero() {
  return (
    <section className="container mt-4">
      <div className="relative overflow-hidden rounded-2xl bg-brand text-white">
        {/* декоративные пятна лимона */}
        <div
          className="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full"
          style={{ background: "var(--ll-lemon)", filter: "blur(12px)", opacity: 0.25 }}
        />
        <div
          className="pointer-events-none absolute -right-10 bottom-0 hidden md:block h-56 w-56 rounded-full"
          style={{ background: "var(--ll-lemon)", filter: "blur(10px)", opacity: 0.18 }}
        />

        <div className="px-6 py-8 md:px-10 md:py-12 lg:py-16 relative">
          <div className="flex items-center gap-2">
            {/* логотип слева от заголовка (можно убрать, если не нужен) */}
            <Image
              src="/brand/lemon-colored.png"
              alt=""
              width={44}
              height={44}
              className="rounded-full"
            />
            <span className="font-brand tracking-[0.18em] text-lemon">LITTLE LEMON</span>
          </div>

          <h1 className="mt-3 font-brand tracking-wide leading-tight text-3xl sm:text-4xl lg:text-5xl">
            Bright Mediterranean flavors — every day
          </h1>

          <p className="mt-3 max-w-2xl opacity-90">
            Fresh, seasonal dishes prepared daily. Order for pickup or dine in.
          </p>

          <div className="mt-5 flex flex-col sm:flex-row gap-3">
            <Link href="/menu" className="llem-btn llem-btn--accent">
              Browse menu
            </Link>
            <Link href="/orders" className="llem-btn llem-btn--outline">
              My orders
            </Link>
          </div>

          {/* маленькие бейджи-преимущества */}
          <ul className="mt-6 flex flex-wrap gap-2 opacity-90 text-sm">
            <li className="rounded-full bg-white/10 px-3 py-1">Fresh & seasonal</li>
            <li className="rounded-full bg-white/10 px-3 py-1">Pickup in 15–20 min</li>
            <li className="rounded-full bg-white/10 px-3 py-1">Vegetarian options</li>
          </ul>
        </div>

        {/* вертикальный знак бренда справа (скрыт на мобиле) */}
        <div className="absolute right-4 top-1/2 -translate-y-1/2 hidden md:block">
          <Image
            src="/brand/lockup-vertical.png"
            alt="Little Lemon"
            width={220}
            height={340}
            priority
          />
        </div>
      </div>
    </section>
  );
}