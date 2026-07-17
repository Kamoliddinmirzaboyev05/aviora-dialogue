/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        night: "#07061a",
        deep: "#0d0a26",
        panel: "#151034",
        stroke: "#241c4d",
        violet: "#7c5cff",
        glow: "#5b7bff"
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"]
      },
      keyframes: {
        float: {
          "0%,100%": { transform: "translateY(0) scale(1)" },
          "50%": { transform: "translateY(-24px) scale(1.06)" }
        }
      },
      animation: {
        float: "float 9s ease-in-out infinite"
      }
    }
  },
  plugins: []
};
