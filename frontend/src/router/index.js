import { createRouter, createWebHistory } from "vue-router"
import { useAuthStore } from "@/stores/auth"

const routes = [
  { path: "/login", component: () => import("@/views/LoginView.vue"), meta: { guest: true } },
  { path: "/register", component: () => import("@/views/RegisterView.vue"), meta: { guest: true } },
  { path: "/", component: () => import("@/views/DashboardView.vue"), meta: { auth: true } },
  { path: "/projects/:id", component: () => import("@/views/ProjectView.vue"), meta: { auth: true } },
  { path: "/admin", component: () => import("@/views/AdminView.vue"), meta: { auth: true, admin: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.auth && !auth.token) return "/login"
  if (to.meta.guest && auth.token) return "/"
  if (to.meta.admin && !auth.isAdmin) return "/"
})

export default router
