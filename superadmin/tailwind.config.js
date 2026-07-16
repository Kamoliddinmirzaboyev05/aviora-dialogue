/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#10201c",
        surface: "#f5f7f2",
        panel: "#ffffff",
        line: "#d9e1d6",
        emerald: "#087f5b",
        gold: "#c58a17",
        danger: "#b42318",
        muted: "#66746d"
      }
    }
  },
  plugins: []
};
