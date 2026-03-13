/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eefcf8',
          100: '#d3f8ec',
          200: '#a9f0dd',
          300: '#76e3ca',
          400: '#3dcdb2',
          500: '#1eb39a',
          600: '#0f8f7d',
          700: '#107364',
          800: '#125b50',
          900: '#124b43'
        }
      },
      boxShadow: {
        panel: '0 16px 40px rgba(15, 31, 43, 0.08)'
      }
    }
  },
  plugins: []
};
