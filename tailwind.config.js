/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './*/templates/**/*.html',
    './orders/templatetags/*.py',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#FBE4EC',
        secondary: '#F6CFDD',
        accent: '#D67D9C',
        neutral: '#5C4550',
        base: '#FFF8FA',
      },
      fontFamily: {
        sans: ['"Noto Sans TC"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
