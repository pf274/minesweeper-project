import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  base: "/minesweeper-project/",
  publicDir: "public",
  assetsInclude: ["src/assets/*", "assets/*", "src/assets/**/*", "assets/**/*"],
  plugins: [react()],
});
