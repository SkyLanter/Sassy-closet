import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#D82B60",
          foreground: "#fff7fa",
        },
        card: "#fff8fb",
      },
      fontFamily: {
        sans: ["Nunito", "ui-sans-serif", "system-ui"],
        script: ["Allura", "cursive"],
      },
    },
  },
  plugins: [],
};

export default config;
