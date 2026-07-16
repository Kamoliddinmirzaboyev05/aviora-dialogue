/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17202a",
        panel: "#f7f8fb",
        line: "#d9dee8",
        teal: "#0f766e",
        amber: "#b45309"
      }
    }
  },
  plugins: []
};
