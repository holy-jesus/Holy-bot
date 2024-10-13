<script setup>
const props = defineProps(["user", "text", "ping"])

</script>

<template>
    <div class="inline-flex my-1">
        <img :src="props.user.badge"
            class="w-[18px] h-[18px] my-1 mx-1" /><a><a :href="'https://twitch.tv/' + props.user.nickname.toLowerCase()"
                class="font-semibold" :style="{ color: props.user.color }">{{ props.user.nickname }}</a><a class="mr-1">:</a><b>{{
                props.ping }}</b>{{ props.text }}</a>
    </div>
</template>
