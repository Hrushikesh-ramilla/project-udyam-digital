/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Sora"', '"DM Sans"', 'system-ui', '-apple-system', 'sans-serif'],
        serif: ['"Cormorant Garamond"', 'Georgia', 'serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        obsidian: {
          950: "#050505",
          900: "#0c0c0b",
          850: "#121210",
          800: "#181816",
          750: "#22221f",
          700: "#2e2e2a",
          600: "#40403b",
          500: "#60605a",
        },
        champagne: {
          300: "#f0d5a8",
          400: "#e2be7e",
          500: "#d9ad63",
          600: "#b88a3b",
        },
        airtel: {
          500: "#ef4444",
          600: "#e40000",
          700: "#b30000",
          darkred: "#8b0000",
          ink: "#f2efea",
          surface: "#0c0c0b",
          border: "rgba(255, 255, 255, 0.07)",
        }
      },
      boxShadow: {
        'airtel-glow': '0 0 25px -4px rgba(228, 0, 0, 0.35)',
        'champagne-glow': '0 0 25px -4px rgba(217, 173, 99, 0.35)',
        'subtle-depth': '0 20px 40px -15px rgba(0, 0, 0, 0.9), 0 0 0 1px rgba(255, 255, 255, 0.07)',
        'glass-card': '0 12px 36px 0 rgba(0, 0, 0, 0.5), inset 0 0 0 1px rgba(255, 255, 255, 0.08)',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        pulseGlow: {
          '0%, 100%': { opacity: '0.4' },
          '50%': { opacity: '0.8' },
        }
      },
      animation: {
        'shimmer': 'shimmer 8s ease-in-out infinite',
        'pulse-glow': 'pulseGlow 3s ease-in-out infinite',
      }
    },
  },
  plugins: [],
}
