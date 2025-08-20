import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: "http", hostname: "localhost", port: "8000", pathname: "/media/**" },
      // если будет прод: { protocol: "https", hostname: "api.your-domain.com", pathname: "/media/**" }
    ],
  },
};

export default nextConfig;
