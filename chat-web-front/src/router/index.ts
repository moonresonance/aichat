import { createRouter, createWebHashHistory } from "vue-router";

import Loginregister from "@/components/login/first.vue";
import home from "@/components/home/home.vue";
import Settings from "@/components/settings/Settings.vue";
import IntroPage from "@/components/intro/IntroPage.vue";

const routes = [
  {
    path: "/login",
    name: "login",
    component: Loginregister,
  },
  {
    path: "/",
    name: "intro",
    component: IntroPage,
  },
  {
    path: "/home",
    name: "home",
    component: home,
  },
  {
    path: "/settings",
    name: "settings",
    component: Settings,
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes: routes,
});

export default router;
