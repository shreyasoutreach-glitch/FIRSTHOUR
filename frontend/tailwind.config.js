/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        forest: "#1D1D1F",     // Apple typography
        charcoal: "#000000",   // True black
        ivory: "#F5F5F7",      // Apple system background
        parchment: "#FFFFFF",  // Apple elevated surfaces (cards)
        gold: "#0066CC",       // Royal / Apple system blue
        champagne: "#0071E3",  // Apple vibrant blue
        emerald: "#34C759",    // Apple success green
        vermillion: "#FF3B30", // Apple destructive red
        amber: "#FF9500",      // Apple warning orange
      },
      fontFamily: {
        display: ["-apple-system", "BlinkMacSystemFont", "SF Pro Display", "Segoe UI", "sans-serif"],
        ui: ["-apple-system", "BlinkMacSystemFont", "SF Pro Text", "Segoe UI", "sans-serif"],
        label: ["-apple-system", "BlinkMacSystemFont", "SF Pro Text", "Segoe UI", "sans-serif"],
      },
      maxWidth: {
        canvas: "1440px",
      },
      transitionDuration: {
        250: "250ms",
        400: "400ms",
      },
      boxShadow: {
        paper: "0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03)",
        raised: "0 8px 24px rgba(0, 0, 0, 0.08)",
      },
    },
  },
  plugins: [],
};
