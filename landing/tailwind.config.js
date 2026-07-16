/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#16211f",
        moss: "#355e4b",
        coral: "#c75f4a",
        gold: "#d69f38",
        cloud: "#f4f7f4",
        line: "#d8dfd8"
      }
    }
  },
  plugins: []
};
