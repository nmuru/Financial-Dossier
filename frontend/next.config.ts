import type { NextConfig } from "next";

const Production_mode = true;

const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: Production_mode
      ? "https://blvd-bob-sailing-inner.trycloudflare.com"
      : "http://localhost:8000",
  },
};

export default nextConfig;
