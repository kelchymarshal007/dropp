/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#000000",
        surface: "#121212",
        card: "#1E1E1E",
        border: "#2A2A2A",
        "dropp-orange": "#FF9900", 
        "chat-system": "#27272A",
        "chat-ai-bg": "#FEF9C3",
        "chat-ai-text": "#422006",
        "chat-buyer": "#2563EB",
        "chat-seller": "#1E3A8A",
        "accent-green": "#22C55E",
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'sans-serif'],
      },
      keyframes: {
        wiggle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      },
      animation: {
        wiggle: 'wiggle 0.6s ease-in-out infinite',
      }
    },
  },
  plugins: [],
}
