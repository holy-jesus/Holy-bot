import { createApp } from "vue";
import "./output.css";
import App from "./App.vue";
import { createMemoryHistory, createRouter } from "vue-router";

import index from "./components/index.vue";

const routes = [{ path: "/", component: index }];

const router = createRouter({
    history: createMemoryHistory(),
    routes,
});

createApp(App).use(router).mount("#app");
