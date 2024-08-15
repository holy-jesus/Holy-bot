if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.classList.add('dark')
    localStorage.theme = "dark"
} else {
    document.documentElement.classList.remove('dark')
    localStorage.theme = "light"
}

function changeTheme() {
    console.log("HEHE")
    if (localStorage.theme === "dark") {
        document.documentElement.classList.remove('dark')
        localStorage.theme = "light"
    } else {
        document.documentElement.classList.add('dark')
        localStorage.theme = "dark"
    }
}