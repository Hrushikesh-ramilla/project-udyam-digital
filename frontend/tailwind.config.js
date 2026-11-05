/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Sora"', '"DM Sans"', '-apple-system', 'sans-serif'],
        serif: ['"Cormorant Garamond"', 'Georgia', 'serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        // Apple / Ivory / Dark Navy Palette from hrushikeshramilla.in & DALE
        canvas: "#030405",
        surface: {
          DEFAULT: "#080a0d",
          soft: "#0b0e12",
          elevated: "#0f1216",
          hover: "#15191f",
        },
        ivory: {
          DEFAULT: "#EBE5D9",
          soft: "#d8d1c3",
          muted: "#8c867a",
        },
        sand: {
          DEFAULT: "#B39D82",
          light: "#c9b69f",
          dark: "#8f7a62",
        },
        gold: {
          DEFAULT: "#a68a50",
          warm: "#d9ad63",
          glow: "rgba(217, 173, 99, 0.25)",
        },
        steel: {
          DEFAULT: "#7EA8C4",
          soft: "rgba(126, 168, 196, 0.15)",
        },
        airtel: {
          DEFAULT: "#e40000",
          bright: "#EF4444",
          soft: "rgba(228, 0, 0, 0.15)",
          glow: "rgba(228, 0, 0, 0.35)",
        }
      },
      boxShadow: {
        'apple-card': '0 20px 40px -15px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(235, 229, 217, 0.06)',
        'apple-elevated': '0 30px 60px -20px rgba(0, 0, 0, 0.85), 0 0 0 1px rgba(235, 229, 217, 0.1)',
        'apple-glow': '0 0 25px -4px rgba(228, 0, 0, 0.35)',
        'ivory-glow': '0 0 25px -4px rgba(235, 229, 217, 0.15)',
      },
      transitionTimingFunction: {
        'apple-spring': 'cubic-bezier(0.22, 1, 0.36, 1)',
      }
    },
  },
  plugins: [],
}
