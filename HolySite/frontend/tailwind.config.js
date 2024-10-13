/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./src/**/*.{js,ts,jsx,tsx,vue}",
    ],
    theme: {
        extend: {
            colors: {
                blue: "#00a6ff",
                lightblue: "#69d7f3",
            },
        },
    },
    plugins: [],
    darkMode: "class",
};
