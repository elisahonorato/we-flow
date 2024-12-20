const colors = require('tailwindcss/colors')

module.exports = {
    content: [
        "./templates/**/*.html",
        "./**/templates/**/*.html",
        "./static/js/**/*.js"
      ],
    purge: [
        './django_admin_tailwind/**/*.html',
    ],
    darkMode: 'media',
    theme: {
        fill: {
            current: 'currentColor',
        },
        colors: {
            white: colors.white,
            red: colors.red,
            yellow: colors.yellow,
            green: colors.green,
            orange: colors.orange,
            light: {
                0: 'var(--color-light-0)',
                50: 'var(--color-light-50)',
                100: 'var(--color-light-100)',
                200: 'var(--color-light-200)',
                300: 'var(--color-light-300)',
                400: 'var(--color-light-400)',
                500: 'var(--color-light-500)',
                600: 'var(--color-light-600)',
                700: 'var(--color-light-700)',
                800: 'var(--color-light-800)',
                900: 'var(--color-light-900)',
            },
            dark: {
                0: 'var(--color-dark-0)',
                50: 'var(--color-dark-50)',
                100: 'var(--color-dark-100)',
                200: 'var(--color-dark-200)',
                300: 'var(--color-dark-300)',
                400: 'var(--color-dark-400)',
                500: 'var(--color-dark-500)',
                600: 'var(--color-dark-600)',
                700: 'var(--color-dark-700)',
                800: 'var(--color-dark-800)',
                900: 'var(--color-dark-900)',
            },
            primary: {
                50: 'var(--color-primary-50)',
                100: 'var(--color-primary-100)',
                200: 'var(--color-primary-200)',
                300: 'var(--color-primary-300)',
                400: 'var(--color-primary-400)',
                500: 'var(--color-primary-500)',
                600: 'var(--color-primary-600)',
                700: 'var(--color-primary-700)',
                800: 'var(--color-primary-800)',
                900: 'var(--color-primary-900)',
            },
            secondary: {
                50: 'var(--color-secondary-50)',
                100: 'var(--color-secondary-100)',
                200: 'var(--color-secondary-200)',
                300: 'var(--color-secondary-300)',
                400: 'var(--color-secondary-400)',
                500: 'var(--color-secondary-500)',
                600: 'var(--color-secondary-600)',
                700: 'var(--color-secondary-700)',
                800: 'var(--color-secondary-800)',
                900: 'var(--color-secondary-900)',
            },
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
    ],
}
