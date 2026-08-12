/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1a1410",
        cocoa: {
          50: "#faf6f2",
          100: "#f0e6db",
          200: "#ddc4a8",
          300: "#c8a074",
          400: "#a97a4a",
          500: "#7a4f2b",
          600: "#5c3a1f",
          700: "#432a17",
          800: "#2e1c0f",
          900: "#1a0f08",
        },
        brass: {
          50: "#fdf8ec",
          100: "#f7e9c4",
          200: "#edd08a",
          300: "#e0b354",
          400: "#c99530",
          500: "#a97b24",
          600: "#87611c",
        },
        paper: "#fbf7f0",
      },
      fontFamily: {
        display: ["Fraunces", "Georgia", "serif"],
        sans: ["Public Sans", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
      },
    },
  },
  plugins: [],
}
