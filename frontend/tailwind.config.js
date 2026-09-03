/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#e0f9ff',
          100: '#b3f0ff',
          200: '#80e5ff',
          300: '#4dd9ff',
          400: '#26d0ff',
          500: '#00c8ff',
          600: '#00b3e6',
          700: '#0099cc',
          800: '#007fa6',
          900: '#005580',
        },
        dark: {
          50:  '#f0f4ff',
          100: '#d9e2ff',
          200: '#aec0ff',
          300: '#7e9bff',
          400: '#5578ff',
          500: '#2b55ff',
          600: '#1a3de6',
          700: '#1230cc',
          800: '#0d23a6',
          900: '#081580',
        },
        surface: {
          900: '#070b14',
          800: '#0d1117',
          700: '#131920',
          600: '#161b22',
          500: '#1c2333',
          400: '#21262d',
          300: '#30363d',
          200: '#3d4450',
          100: '#8b949e',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4,0,0.6,1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'float': 'float 3s ease-in-out infinite',
        'slide-in': 'slideIn 0.3s ease-out',
      },
      keyframes: {
        glow: {
          '0%':   { boxShadow: '0 0 5px #00c8ff33' },
          '100%': { boxShadow: '0 0 20px #00c8ff88, 0 0 40px #00c8ff44' },
        },
        float: {
          '0%,100%': { transform: 'translateY(0px)' },
          '50%':     { transform: 'translateY(-6px)' },
        },
        slideIn: {
          from: { opacity: '0', transform: 'translateY(-8px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
      },
      backdropBlur: { xs: '2px' },
    },
  },
  plugins: [],
}
