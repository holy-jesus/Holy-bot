import { createMemoryHistory, createRouter } from "vue-router";
import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import IndexView from "./pages/index/index.vue";
import TestView from "./pages/command/test.vue";

const routes = [
  { path: "/", component: IndexView },
  { path: "/about", component: TestView },
];

const router = createRouter({
  history: createMemoryHistory(),
  routes,
});

createApp(App).use(router).mount("#app");
