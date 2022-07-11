import { createRouter, createWebHistory } from "vue-router"
import HomeView from "@/views/HomeView.vue"
import PingPongView from "@/views/PingPongView.vue"

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/ping-pong",
      name: "ping-pong",
      component: PingPongView,
    }
  ],
})

export default router
