import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#a85d74",
          foreground: "#fffaf8",
        },
        card: "#fffaf8",
        rose: {
          50: "#fbf6f4",
          100: "#f3e6e2",
          200: "#e6d0ca",
          500: "#c48b9a",
          600: "#a86d7e",
          700: "#7d5360",
          800: "#5c3d48",
          900: "#3f2c33",
          950: "#2a1d22",
        },
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
