/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        graphite: "#0F0F0F",
        surface: "#141414",
        surface_raised: "#1A1A1A",
        surface_border: "#2A2A2A",
        titanium: "#A0A0A0",
        text_primary: "#F0F0F0",
        text_secondary: "#808080",
        emerald: "#28A745",
        vermillion: "#DC3545",
        amber: "#FFC107",
      },
      fontFamily: {
        display: ["Geist", "Inter", "sans-serif"],
        ui: ["Geist", "Inter", "sans-serif"],
        label: ["Geist Mono", "JetBrains Mono", "monospace"],
      },
      maxWidth: {
        canvas: "1600px",
      },
      transitionDuration: {
        250: "250ms",
        400: "400ms",
      },
      boxShadow: {
        paper: "none",
        raised: "0 4px 12px rgba(0, 0, 0, 0.5)",
      },
    },
  },
  plugins: [],
};
