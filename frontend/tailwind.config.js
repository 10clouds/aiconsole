/** @type {import('tailwindcss').Config} */

import path from 'path';

export default {
  // Note that those paths are set up this way because in electron build the ./xxx path seem to be relative to the electron folder
  content: [path.resolve(__dirname, 'index.html'), path.resolve(__dirname, 'src') + '/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  plugins: [require('@tailwindcss/typography')],

  variants: {
    extend: {
      display: ['group-hover'],
    },
  },
  theme: {
    screens: {
      md: '800px',
      xl: '1200px',
      '2xl': '1440px',
    },
    extend: {
      keyframes: {
        fadeInUp: {
          '0%': { transform: 'translateY(30px)', opacity: 0 },
          '100%': { transform: 'translateY(0)', opacity: 1 },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        overlayShow: {
          from: { opacity: 0 },
          to: { opacity: 1 },
        },
        contentShow: {
          from: { opacity: 0, transform: 'translate(-50%, -48%) scale(0.96)' },
          to: { opacity: 1, transform: 'translate(-50%, -50%) scale(1)' },
        },
        slideDownAndFade: {
          from: { opacity: 0, transform: 'translateY(40px)' },
          to: { opacity: 1, transform: 'translateY(0)' },
        },
        slideLeftAndFade: {
          from: { opacity: 0, transform: 'translateX(-40px)' },
          to: { opacity: 1, transform: 'translateX(0)' },
        },
        slideUpAndFade: {
          from: { opacity: 0, transform: 'translateY(-40px)' },
          to: { opacity: 1, transform: 'translateY(0)' },
        },
        slideRightAndFade: {
          from: { opacity: 0, transform: 'translateX(40px)' },
          to: { opacity: 1, transform: 'translateX(0)' },
        },
      },
      animation: {
        fadeInUp: 'fadeInUp .2s ease-in-out',
        fadeIn: 'fadeIn .1s ease-in-out',
        overlayShow: 'overlayShow 150ms cubic-bezier(0.16, 1, 0.3, 1)',
        contentShow: 'contentShow 150ms cubic-bezier(0.16, 1, 0.3, 1)',
        slideDownAndFade: 'slideDownAndFade 200ms cubic-bezier(0.16, 1, 0.3, 1)',
        slideLeftAndFade: 'slideLeftAndFade 200ms cubic-bezier(0.16, 1, 0.3, 1)',
        slideUpAndFade: 'slideUpAndFade 200ms cubic-bezier(0.16, 1, 0.3, 1)',
        slideRightAndFade: 'slideRightAndFade 200ms cubic-bezier(0.16, 1, 0.3, 1)',
      },
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
      },
      backgroundImage: {
        'recent-bg': "url('/bg1.png')",
        'top-elipse': "url('/elipse-top.png')",
        'primary-gradient': 'radial-gradient(circle at 50% -40%, rgba(173,122,255,1) -150%, rgba(26,26,26,1) 60%)',
        'secondary-gradient': 'linear-gradient(180deg, rgba(31,31,31,1) 0%, rgba(17,17,17,1) 100%)',
        'project-item-gradient': 'linear-gradient(180deg, #161616 29.17%, #2D253E 100%)',
        'project-item-gradient-2': 'linear-gradient(180deg, rgba(17, 17, 17, 0.00) 65.1%, #111 100%)',
      },
      boxShadow: {
        dark: '0px 20px 40px 0px rgba(0, 0, 0, 0.25)',
        agent: '0px 0px 5px 0px #62ADF2;',
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            color: '#ABABAB',
            h1: {
              fontSize: '28px',
              color: theme('colors.white'),
              fontWeight: 700,
              lineHeight: 'normal',
              letterSpacing: '-1.12px',
            },
            h2: {
              fontSize: '24px',
              color: theme('colors.white'),
              fontWeight: 700,
              lineHeight: 'normal',
            },
            h3: {
              fontSize: '18px',
              color: theme('colors.white'),
              fontWeight: 700,
              lineHeight: 'normal',
            },
            h4: {
              fontSize: '15px',
              color: theme('colors.gray[300]'),
              fontWeight: 700,
              lineHeight: 'normal',
            },
            p: {
              fontSize: '15px',
              color: theme('colors.gray[300]'),
              fontWeight: 400,
              lineHeight: '24px',
            },
            a: {
              color: '#1f6feb',
            },
            'pre, code': {
              padding: 0,
              background: 'transparent',
            },
          },
        },
      }),
      colors: {
        primary: '#A67CFF',
        'primary-light': '#B68CFF',
        'primary-dark': '#966CFF',
        secondary: '#F1FF99',
        'secondary-light': '#FFFFEE',
        'secondary-dark': '#D5FF00',
        agent: '#62ADF2',
        material: '#CFA740',
        chat: '#7C43F5',
        danger: '#CF4840',
        success: '#60C164',
        black: '#000000',
        white: '#FFFFFF',
        yellow: '#F1FF99',
        purple: {
          200: '#E5D9FF',
          300: '#C6ABFF',
          400: '#A67CFF',
          500: '#7C43F5',
          600: '#5427B4',
          700: '#442586',
        },
        grayPurple: {
          200: '#DED6EE',
          300: '#C0B2DF',
          400: '#8F7EB1',
          500: '#725C9F',
          600: '#4B3A6F',
          700: '#3A2E58',
          800: '#271E3C',
          900: '#1D162C',
        },
        gray: {
          100: '#E6E6E6',
          200: '#C3C3C3',
          300: '#A6A6A6',
          400: '#737373',
          500: '#3E3E3E',
          600: '#272727',
          700: '#1F1F1F',
          800: '#1A1A1A',
          900: '#111111',
        },
        green: '#60C164',
        red: '#CF4840',
        orange: '#CFA740',
        blue: '#62ADF2',
        'primary-gradient': 'radial-gradient(circle at 50% -40%, rgba(173,122,255,1) -150%, rgba(26,26,26,1) 60%)',
        topGradient: '#2D253E',
      },
    },
  },
};
