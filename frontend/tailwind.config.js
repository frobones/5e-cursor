/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // D&D-inspired color palette
        parchment: {
          50: '#fefdfb',
          100: '#fdf9f3',
          200: '#f9f0e1',
          300: '#f3e4c8',
          400: '#e9d4a8',
          500: '#dfc288',
          600: '#c9a55e',
          700: '#a88442',
          800: '#8a6a36',
          900: '#71562e',
        },
        ink: {
          50: '#f6f5f4',
          100: '#e7e5e3',
          200: '#d1cdc9',
          300: '#b4aea7',
          400: '#958c82',
          500: '#7a7168',
          600: '#625b54',
          700: '#504a45',
          800: '#423e3a',
          900: '#393634',
          950: '#1a1918',
        },
        // Role colors
        ally: {
          light: '#dcfce7',
          DEFAULT: '#22c55e',
          dark: '#166534',
        },
        neutral: {
          light: '#e0e7ff',
          DEFAULT: '#6366f1',
          dark: '#3730a3',
        },
        enemy: {
          light: '#fee2e2',
          DEFAULT: '#ef4444',
          dark: '#991b1b',
        },
      },
      fontFamily: {
        display: ['Cinzel', 'serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
