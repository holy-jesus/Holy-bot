import { createWebHistory, createRouter } from "vue-router";
import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import IndexView from "./pages/index/index.vue";
import TestView from "./pages/command/test.vue";
import ProfileView from "./pages/profile/profile.vue";

const routes = [
  { path: "/", component: IndexView },
  { path: "/about", component: TestView },
  { path: "/profile", component: ProfileView}
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

createApp(App).use(router).mount("#app");
