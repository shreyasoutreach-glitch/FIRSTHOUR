import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 2090,
    // Dev-server-only proxy so `npm run dev` can talk to a locally running
    // backend without CORS friction. This never ships to the browser bundle
    // -- production builds call the relative "/api" path (see src/lib/api.ts).
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
