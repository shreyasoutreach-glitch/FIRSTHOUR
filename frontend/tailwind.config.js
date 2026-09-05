/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        forest: "#071510",     // Deep forest -- dark canvas / nav
        charcoal: "#101713",   // Charcoal -- dark surfaces
        ivory: "#F3EBDD",      // Warm ivory -- primary workspace
        parchment: "#E8DECB",  // Parchment -- cards / evidence sheets
        gold: "#C9A45C",       // Antique gold -- money / focus / dividers
        champagne: "#E0C37A",  // Champagne -- secondary financial emphasis
        emerald: "#19A974",    // Emerald -- verified / cleared
        vermillion: "#B83A32", // Vermillion -- confirmed incident / contradiction
        amber: "#C58A27",      // Amber -- human judgment / unresolved
      },
      fontFamily: {
        display: ["Georgia", "Iowan Old Style", "Palatino Linotype", "URW Palladio", "serif"],
        ui: ["Aptos", "Segoe UI", "Calibri", "ui-sans-serif", "system-ui", "sans-serif"],
        label: ["Aptos Display", "Segoe UI Semibold", "Segoe UI", "ui-sans-serif", "sans-serif"],
      },
      maxWidth: {
        canvas: "1440px",
      },
      transitionDuration: {
        250: "250ms",
        400: "400ms",
      },
      boxShadow: {
        paper: "0 1px 2px rgba(7, 21, 16, 0.06), 0 1px 1px rgba(7, 21, 16, 0.04)",
        raised: "0 4px 16px rgba(7, 21, 16, 0.10)",
      },
    },
  },
  plugins: [],
};
