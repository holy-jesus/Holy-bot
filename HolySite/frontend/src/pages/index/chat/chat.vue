<script setup>
import MessageComponent from "src/pages/index/chat/message.vue";
import { ref, onMounted } from 'vue';

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min) + min);
}

const messages = ref([])
const inputBoxText = ref("")
const animationRunning = ref(true)
const hide = ref(false)

const hoIy_jesus = {
    "nickname": "hoIy_jesus",
    "badge": "https://static-cdn.jtvnw.net/badges/v1/5527c58c-fb7d-422d-b71b-f309dcb85cc1/1",
    "color": "rgb(46, 139, 87)",
}

const hoIy_bot = {
    "nickname": "hoIy_bot",
    "badge": "https://static-cdn.jtvnw.net/badges/v1/3267646d-33f0-4b17-b3df-f923a41db1d0/1",
    "color": "rgb(255, 237, 128)",
}

const animationOrder = ref([{
    "user": hoIy_jesus,
    "ping": "",
    "text": "!music",
    "type": true,
}, {
    "user": hoIy_bot,
    "ping": "@hoIy_jesus",
    "text": ", Rick Astley - Never Gonna Give You Up",
    "type": false,
}, {
    "user": hoIy_jesus,
    "ping": "",
    "text": "!game",
    "type": true,
}, {
    "user": hoIy_bot,
    "ping": "@hoIy_jesus",
    "text": ", Just Chatting [00:31:28]",
    "type": false,
}])

async function restartAnimation() {
    if (animationRunning.value != false) return
    animationRunning.value = true
    messages.value = []
    await sleep(300)
    playAnimation()
}

function hideChat(forever = false) {
    hide.value = true
}

async function typeText(text) {
    for (let char of text) {
        inputBoxText.value += char;
        await sleep(getRandomInt(75, 150));
    }
    inputBoxText.value = ""
    await sleep(75);
}

async function playAnimation() {
    await sleep(300)
    animationRunning.value = true;
    for (const message of animationOrder.value) {
        if (message["type"]) {
            await typeText(message["text"])
        }
        messages.value.unshift(message)
        await sleep(600)
    }
    animationRunning.value = false;
}

function preloadBadges() {
    for (const user of [hoIy_jesus, hoIy_bot]) {
        const image = new Image()
        image.src = user.badge
    }
}

onMounted(() => {
    preloadBadges()
    playAnimation()
})
</script>

<template>
    <Transition>
        <div ref="chatWrapper"
            class="basis-0 scale-0 md:basis-1/2 xl:basis-1/4 md:scale-100 grid place-items-center transition-colors duration-300"
            v-if="!hide">
            <div ref="chat"
                class="flex flex-col w-0 scale-0 min-h-[450px] md:w-[340px] md:scale-100 bg-[#18181b] border-[1px] border-[#2a2a2d] rounded-md transition-colors duration-300 hidden-scroolbar select-none">
                <div class="border-b-[1px] border-[#2a2a2d] text-white text-center">
                    <h4 class="my-2 text-sm font-semibold">FAKE CHAT :)</h4>
                </div>
                <div ref="chatMessages" class="flex flex-grow flex-col-reverse text-white mx-2.5 overflow-y-scroll">
                    <TransitionGroup name="only-fadeout">
                        <MessageComponent :key="index" v-for="(message, index) in messages" :user="message['user']"
                            :ping="message['ping']" :text="message['text']" />
                    </TransitionGroup>
                </div>
                <div class="my-5 relative w-[320px] h-[38px]">
                    <Transition>
                        <input ref="chatInput" type="text"
                            class="bg-[#3d3d40] w-[320px] h-[38px] mx-2.5 rounded-sm px-2 text-white absolute"
                            placeholder="Send a message" disabled="true" v-show="animationRunning"
                            :value="inputBoxText" />
                    </Transition>
                    <Transition>
                        <div v-show="!animationRunning"
                            class="top-0 left-0 absolute mx-2.5 w-[320px] h-[38px] flex flex-row justify-between">
                            <button @click="restartAnimation()"
                                class="bg-[#3d3d40] text-[#9ca3af] rounded-sm p-1 h-[38px]">
                                Повторить
                            </button>
                            <button @click="hideChat()"
                                class="bg-[#3d3d40] text-[#9ca3af] rounded-sm p-1 h-[38px]">
                                Скрыть
                            </button>
                            <button @click="hideChat(true)"
                                class="bg-[#3d3d40] text-[#9ca3af] rounded-sm p-1 h-[38px]">
                                Скрыть навсегда
                            </button>
                        </div>
                    </Transition>
                </div>
            </div>
        </div>
    </Transition>
</template>

<style scoped>
.v-enter-active,
.v-leave-active {
    transition: opacity 0.3s ease;
}

.v-enter-from,
.v-leave-to {
    opacity: 0;
}

.only-fadeout-leave-from,
.only-fadeout-leave-active {
    transition: opacity 0.3s ease;
    opacity: 0;
}
</style>