function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function init() {
    if (STATE != "None") {
        let host = location.protocol + '//' + location.host;
        if (host.includes("127.0.0.1")) {
            host = document.location.replace(host.replace("127.0.0.1", "localhost"));
        } else if (host.includes("0.0.0.0")) {
            host = document.location.replace(host.replace("0.0.0.0", "localhost"));
        }
        let loginUrl = `https://id.twitch.tv/oauth2/authorize?response_type=code&scope=&client_id=f7cx3c3iftgmukun3hkzxkdm267e4l&redirect_uri=${host}/login&state=${STATE}`
        let loginButton = document.getElementById("loginButton");
        let loginHeader = document.getElementById("loginHeader")
        if (loginButton != null) {
            loginButton.setAttribute("href", loginUrl)
        }
        if (loginHeader != null) {
            loginHeader.setAttribute("href", loginUrl)
        }
    }
    document.body.animate(
        [
            { opacity: 0 },
            { opacity: 1 }
        ],
        {
            duration: 300,
            easing: "ease-in-out",
            fill: "forwards"
        }
    )
    await sleep(300)
    document.body.classList.remove("opacity-0")
}

if (document.readyState === "loading") {
    addEventListener('DOMContentLoaded', () => init());
} else {
    init();
}