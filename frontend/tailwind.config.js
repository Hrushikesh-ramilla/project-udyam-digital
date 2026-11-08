/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', '"Inter"', 'system-ui', '-apple-system', 'sans-serif'],
        serif: ['"Plus Jakarta Sans"', '"Inter"', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        // Modern Crisp High-Contrast Airtel Enterprise Palette
        canvas: "#090D16",
        surface: {
          DEFAULT: "#111827",
          soft: "#141D2E",
          elevated: "#1E293B",
          hover: "#243248",
        },
        ivory: {
          DEFAULT: "#FFFFFF",
          soft: "#F8FAFC",
          muted: "#94A3B8",
        },
        sand: {
          DEFAULT: "#94A3B8",
          light: "#CBD5E1",
          dark: "#64748B",
        },
        gold: {
          DEFAULT: "#F59E0B",
          warm: "#F59E0B",
          glow: "rgba(245, 158, 11, 0.25)",
        },
        steel: {
          DEFAULT: "#60A5FA",
          soft: "rgba(96, 165, 250, 0.15)",
        },
        airtel: {
          DEFAULT: "#e40000",
          bright: "#EF4444",
          soft: "rgba(228, 0, 0, 0.15)",
          glow: "rgba(228, 0, 0, 0.35)",
        }
      },
      boxShadow: {
        'apple-card': '0 10px 30px -10px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.08)',
        'apple-elevated': '0 20px 40px -15px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(255, 255, 255, 0.12)',
        'apple-glow': '0 0 25px -4px rgba(228, 0, 0, 0.35)',
        'ivory-glow': '0 0 25px -4px rgba(255, 255, 255, 0.15)',
      },
      transitionTimingFunction: {
        'apple-spring': 'cubic-bezier(0.22, 1, 0.36, 1)',
      }
    },
  },
  plugins: [],
}
