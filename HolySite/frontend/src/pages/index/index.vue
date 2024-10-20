<script setup>
import ChatComponent from "src/pages/index/chat/chat.vue";
import BackgroundComponent from "src/pages/index/background.vue";

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

const scope = ""
const state = getCookie("state")
</script>

<template>
    <BackgroundComponent />
    <div class="flex flex-row h-screen items-center justify-center relative z-[2]">
        <div class="basis-0 xl:basis-1/4 h-full w-full transition-colors duration-300"></div>
        <div
            class="basis-full md:basis-1/2 xl:basis-1/4 flex flex-col place-items-center content-center transition-colors duration-300">
            <img src="/src/assets/favicon.ico" class="h-16 w-16 mx-2" />
            <div class="flex flex-row justify-center mb-2">
                <h1 class="text-6xl mr-2 dark:text-white text-black transition-colors duration-300">
                    Holy-bot
                </h1>
                <h1 class="text-xl dark:text-white text-black text-opacity-60 transition-colors duration-300">
                    BETA
                </h1>
            </div>
            <p class="text-black dark:text-white mb-2 max-w-sm text-center transition-colors duration-300">
                Ваш
                <b title="Это значит не надо платить!!!">бесплатный</b>
                помощник.
            </p>
            <a id="loginButton"
                :href="'https://id.twitch.tv/oauth2/authorize?response_type=code&scope=' + scope + '&client_id=f7cx3c3iftgmukun3hkzxkdm267e4l&redirect_uri=http://localhost:8000/login&state=' + state"
                v-if="!loggedIn">
                <button
                    class="px-4 py-1 text-sm text-white font-semibold rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all duration-300 bg-gradient-to-tr from-[#69d7f3] to-[#00a6ff] scale-100 hover:scale-105">
                    Войти через твич
                </button>
            </a>
            <a id="loginButton" @click="$router.push('/profile')" v-else>
                <button
                    class="px-4 py-1 text-sm text-white font-semibold rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all duration-300 bg-gradient-to-tr from-[#69d7f3] to-[#00a6ff] scale-100 hover:scale-105">
                    Перейти в профиль
                </button>
            </a>
        </div>
        <ChatComponent />

        <div class="basis-0 xl:basis-1/4 h-full w-full transition-colors duration-300"></div>
    </div>
</template>
