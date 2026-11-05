/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        airtel: {
          red: "#E40000",
          darkred: "#B30000",
          black: "#1A1A1A",
          gray: "#F4F5F7",
          border: "#E2E8F0",
        }
      }
    },
  },
  plugins: [],
}
