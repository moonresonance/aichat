import { createRouter, createWebHashHistory } from 'vue-router'

import Loginregister from '@/components/login/first.vue'
import home from '@/components/home/home.vue'


const routes = [
    {
        path: '/',
        component: Loginregister
    },
    {
        path: '/home',
        component: home
    },
]

const router = createRouter({
    history: createWebHashHistory(),
    routes: routes
})

export default router
