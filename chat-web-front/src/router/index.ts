import { createRouter, createWebHashHistory } from "vue-router";

import Loginregister from "@/components/login/first.vue";
import home from "@/components/home/home.vue";
import Settings from "@/components/settings/Settings.vue";

const routes = [
  {
    path: "/",
    name: "login",
    component: Loginregister,
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
