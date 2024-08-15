/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./static/css/*.css", "./templates/*.html", "./static/js/*.js"],
  theme: {
    extend: {colors:{
      "blue": "#00a6ff",
      "lightblue": "#69d7f3"
    }},
  },
  plugins: [],
  darkMode: 'class',
}
