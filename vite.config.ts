import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Relative base so the build works on GitHub Pages under /Portfolio-3/ and anywhere else.
export default defineConfig({
  base: "./",
  plugins: [react()],
});
