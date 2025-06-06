/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#4F46E5",   // 以 Colorful Stage 为灵感，主色调适当延展
        secondary: "#6366F1",
        accent: "#EC4899",
        muted: "#F3F4F6",
        dark: "#1F2937",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"],
        heading: ["Poppins", "ui-sans-serif", "system-ui"]
      },
    },
  },
  plugins: [],
};
