/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"DM Sans"', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        serif: ['"Cormorant Garamond"', 'Georgia', 'serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        obsidian: {
          950: "#080807",
          900: "#111110",
          850: "#181817",
          800: "#222220",
          750: "#282825",
          700: "#33332f",
          600: "#454540",
          500: "#60605a",
        },
        champagne: {
          400: "#e2be7e",
          500: "#d9ad63",
          600: "#b88a3b",
        },
        airtel: {
          500: "#ef4444",
          600: "#e40000",
          700: "#b30000",
          darkred: "#8b0000",
          black: "#111110",
          gray: "#f4f3ef",
          border: "#2e2e2c",
        }
      },
      boxShadow: {
        'glow-red': '0 0 25px -5px rgba(228, 0, 0, 0.35)',
        'glow-champagne': '0 0 25px -5px rgba(217, 173, 99, 0.35)',
        'depth': '0 20px 40px -15px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(255, 255, 255, 0.08)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37), inset 0 0 0 1px rgba(255, 255, 255, 0.08)',
      }
    },
  },
  plugins: [],
}
