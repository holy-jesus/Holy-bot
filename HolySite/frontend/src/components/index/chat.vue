<template>
    <div
        ref="chatWrapper"
        class="basis-0 scale-0 md:basis-1/2 xl:basis-1/4 md:scale-100 grid place-items-center transition-colors duration-300"
    >
        <div
            ref="chat"
            class="flex flex-col w-0 scale-0 min-h-[450px] md:w-[340px] md:scale-100 bg-[#18181b] border-[1px] border-[#2a2a2d] rounded-md transition-colors duration-300 hidden-scroolbar select-none"
        >
            <div class="border-b-[1px] border-[#2a2a2d] text-white text-center">
                <h4 class="my-2 text-sm font-semibold">FAKE CHAT :)</h4>
            </div>
            <div
                ref="chatMessages"
                class="flex flex-grow flex-col-reverse text-white mx-2.5 overflow-y-scroll"
            >
                <div class="inline-flex my-1" v-for="message in messages">
                    <img
                        src="https://static-cdn.jtvnw.net/badges/v1/3267646d-33f0-4b17-b3df-f923a41db1d0/1"
                        class="w-[18px] h-[18px] my-1 mx-1"
                    /><a
                        ><a
                            href="https://twitch.tv/"
                            class="font-semibold"
                            style="color: rgb(255, 237, 128)"
                            >hoIy_bot</a
                        ><a class="mr-1">:</a><b>@holy_jesus__</b> , Just
                        Chatting [00:31:48]</a
                    >
                </div>
            </div>
            <div class="my-5 relative w-[320px] h-[38px]">
                <transition>
                    <input
                        ref="chatInput"
                        type="text"
                        class="bg-[#3d3d40] w-[320px] h-[38px] mx-2.5 rounded-sm px-2 text-white absolute"
                        placeholder="Send a message"
                        disabled="true"
                        v-if="animationRunning"
                    />
                </transition>
                <div
                    v-if="!animationRunning"
                    class="top-0 left-0 absolute mx-3 w-[320px] h-[38px] flex flex-row justify-around hidden"
                >
                    <button
                        @click="resetAnimation()"
                        class="bg-[#3d3d40] text-[#9ca3af] rounded-sm p-1 h-[38px] mr-1"
                    >
                        Повторить
                    </button>
                    <button
                        @click="hide_chat(false)"
                        class="bg-[#3d3d40] text-[#9ca3af] rounded-sm p-1 h-[38px] mr-1"
                    >
                        Скрыть
                    </button>
                    <button
                        @click="hide_chat(true)"
                        class="bg-[#3d3d40] text-[#9ca3af] rounded-sm p-1 h-[38px] mr-1"
                    >
                        Скрыть навсегда
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from "vue";

const chatWrapper = ref(null);
const chat = ref(null);
const chatInput = ref(null);
const chatMessages = ref(null);
const animationRunning = ref(false);
const messages = [];

function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min) + min);
}

async function resetAnimation() {
    await sleep(300);
    let children = chatMessages.children;
    for (let i = 0; i < children.length; i++) {
        children[i].animate([{ opacity: 1 }, { opacity: 0 }], {
            duration: 300,
            easing: "ease-in-out",
            fill: "forwards",
        });
    }
    await sleep(300);
    while (chatMessages.firstChild) {
        chatMessages.removeChild(chatMessages.lastChild);
    }

    await play_animation();
}

async function hide_chat(forever = false) {
    if (forever) localStorage.setItem("hideChat", "1");
    chat.animate([{ opacity: 1 }, { opacity: 0 }], {
        duration: 300,
        easing: "ease-in-out",
        fill: "forwards",
    });
    await sleep(300);
    chatWrapper.classList.add("hidden");
}

async function play_animation() {
    clear_input();
    await sleep(750);
    await type_into_input("!music");
    await sleep(1000);
    create_chat_message(
        "@holy_jesus__",
        ", Rick Astley - Never Gonna Give You Up",
        true
    );
    await sleep(450);
    await type_into_input("!game");
    await sleep(450);
    create_chat_message("@holy_jesus__", ", Just Chatting [00:31:48]", true);
}

async function type_into_input(text) {
    for (let char of text) {
        chatInput.value += char;
        await sleep(getRandomInt(75, 150));
    }
    clear_input();
    await sleep(75);
    create_chat_message("", text, false);
}

function create_chat_message(ping, message_text, as_bot) {
    let message = document.createElement("div");
    let badge = document.createElement("img");
    let total = document.createElement("a");
    let author = document.createElement("a");
    let colon = document.createElement("a");
    let bold = document.createElement("b");
    let nick_color;
    let nick;
    if (as_bot) {
        nick_color = "color: #ffed80;";
        nick = "hoIy_bot";
        badge.src =
            "https://static-cdn.jtvnw.net/badges/v1/3267646d-33f0-4b17-b3df-f923a41db1d0/1";
        author.href = "https://twitch.tv/hoiy_bot";
    } else {
        nick_color = "color: #00ff7f;";
        nick = "holy_jesus__";
        badge.src =
            "https://static-cdn.jtvnw.net/badges/v1/5527c58c-fb7d-422d-b71b-f309dcb85cc1/1";
        author.href = "https://twitch.tv/holy_jesus__";
    }
    message.className = "inline-flex my-1";
    badge.className = "w-[18px] h-[18px] my-1 mx-1";
    author.className = "font-semibold";
    colon.className = "mr-1";

    author.style = nick_color;

    author.innerText = nick;
    colon.innerText = ":";
    bold.innerText = ping;

    total.innerHTML = `${author.outerHTML}${colon.outerHTML}${bold.outerHTML} ${message_text}`;
    message.append(badge);
    message.append(total);
    chatMessages.value.insertBefore(message, chatMessages.firstChild);
}

function clear_input() {
    chatInput.value = "";
}

if (document.readyState === "loading") {
    addEventListener("DOMContentLoaded", () => play_animation());
} else {
    play_animation();
}
</script>

<style scoped>
.v-enter-active,
.v-leave-active {
    transition: opacity 0.3s ease;
}

.v-enter-from,
.v-leave-to {
    opacity: 0;
}
</style>
