let chat = document.getElementById("chat")
let chatWrapper = document.getElementById("chatWrapper")
let chatInput = document.getElementById("chatInput")
let chatMessages = document.getElementById("chatMessages")

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min) + min);
}

document.getElementById("chatRepeat").onclick = async () => {
    document.getElementById("chatInput").classList.remove('hidden')
    document.getElementById("chatInput").animate(
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
    document.getElementById("chatButtons").animate(
        [
            { opacity: 1 },
            { opacity: 0 }
        ],
        {
            duration: 300,
            easing: "ease-in-out",
            fill: "forwards"
        }
    )
    await sleep(300)
    document.getElementById("chatButtons").classList.add("hidden")
    let children = chatMessages.children;
    for (let i = 0; i < children.length; i++) {
        children[i].animate(
            [
                { opacity: 1 },
                { opacity: 0 }
            ],
            {
                duration: 300,
                easing: "ease-in-out",
                fill: "forwards"
            }
        )
    }
    await sleep(300)
    while (chatMessages.firstChild) {
        chatMessages.removeChild(chatMessages.lastChild);
    }

    await play_animation()
}

document.getElementById("chatClose").onclick = hide_chat.bind(window, false)
document.getElementById("chatCloseForever").onclick = hide_chat.bind(window, true)

async function hide_chat(forever = false) {
    if (forever) 
        localStorage.setItem("hideChat", "1")
    chat.animate(
        [
            { opacity: 1 },
            { opacity: 0 }
        ],
        {
            duration: 300,
            easing: "ease-in-out",
            fill: "forwards"
        }
    )
    await sleep(300)
    chatWrapper.classList.add('hidden')
}

async function play_animation() {
    clear_input();
    await sleep(750)
    await type_into_input("!music");
    await sleep(1000);
    create_chat_message("@holy_jesus__", ", Rick Astley - Never Gonna Give You Up", true);
    await sleep(450);
    await type_into_input("!game");
    await sleep(450);
    create_chat_message("@holy_jesus__", ", Just Chatting [00:31:48]", true)
    await sleep(300);
    document.getElementById("chatInput").animate(
        [
            { opacity: 1 },
            { opacity: 0 }
        ],
        {
            duration: 300,
            easing: "ease-in-out",
            fill: "forwards"
        }
    )
    document.getElementById("chatButtons").classList.remove("hidden")
    document.getElementById("chatButtons").animate(
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
    document.getElementById("chatInput").classList.add('hidden')
}

async function type_into_input(text) {
    for (let char of text) {
        chatInput.value += char;
        await sleep(getRandomInt(75, 150))
    }
    clear_input()
    await sleep(75)
    create_chat_message("", text, false);
}

function create_chat_message(ping, message_text, as_bot) {
    let message = document.createElement("div")
    let badge = document.createElement("img")
    let total = document.createElement("a")
    let author = document.createElement("a")
    let colon = document.createElement("a")
    let bold = document.createElement("b")
    if (as_bot) {
        nick_color = "color: #ffed80;"
        nick = "hoIy_bot"
        badge.src = "https://static-cdn.jtvnw.net/badges/v1/3267646d-33f0-4b17-b3df-f923a41db1d0/1"
        author.href = "https://twitch.tv/hoiy_bot"
    } else {
        nick_color = "color: #00ff7f;"
        nick = "holy_jesus__"
        badge.src = "https://static-cdn.jtvnw.net/badges/v1/5527c58c-fb7d-422d-b71b-f309dcb85cc1/1"
        author.href = "https://twitch.tv/holy_jesus__"
    }
    message.className = "inline-flex my-1"
    badge.className = "w-[18px] h-[18px] my-1 mx-1"
    author.className = "font-semibold"
    colon.className = "mr-1"

    author.style = nick_color

    author.innerText = nick
    colon.innerText = ":"
    bold.innerText = ping

    total.innerHTML = `${author.outerHTML}${colon.outerHTML}${bold.outerHTML} ${message_text}`
    message.append(badge)
    message.append(total)
    chatMessages.insertBefore(message, chatMessages.firstChild);
}

function clear_input() {
    chatInput.value = ""
}


if (document.readyState === "loading") {
    addEventListener('DOMContentLoaded', () => play_animation());
} else {
    play_animation();
}