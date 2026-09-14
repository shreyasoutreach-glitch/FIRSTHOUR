/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        graphite: "#000000",     // True OLED Black
        surface: "#1C1C1E",      // Apple iOS Card background
        surface_raised: "#2C2C2E", // Apple elevated Card
        titanium: "#0A84FF",     // Apple iOS Blue
        text_primary: "#FFFFFF", // True White
        text_secondary: "#8E8E93", // Apple System Gray
        emerald: "#32D74B",      // Apple iOS Green Dark
        vermillion: "#FF453A",   // Apple iOS Red Dark
        amber: "#FF9F0A",        // Apple iOS Orange Dark
      },
      fontFamily: {
        display: ["Inter", "-apple-system", "BlinkMacSystemFont", "SF Pro Display", "Segoe UI", "sans-serif"],
        ui: ["Inter", "-apple-system", "BlinkMacSystemFont", "SF Pro Text", "Segoe UI", "sans-serif"],
        label: ["Inter", "-apple-system", "BlinkMacSystemFont", "SF Pro Text", "Segoe UI", "sans-serif"],
      },
      maxWidth: {
        canvas: "1440px",
      },
      transitionDuration: {
        250: "250ms",
        400: "400ms",
      },
      boxShadow: {
        paper: "0 1px 3px rgba(0, 0, 0, 0.2), 0 1px 2px rgba(0, 0, 0, 0.12)",
        raised: "0 8px 24px rgba(0, 0, 0, 0.4)",
      },
    },
  },
  plugins: [],
};
