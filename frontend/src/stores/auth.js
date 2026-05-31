import { defineStore } from "pinia"
import { ref, computed } from "vue"
import api from "@/api"

export const useAuthStore = defineStore("auth", () => {
  const token = ref(localStorage.getItem("token"))
  const user = ref(JSON.parse(localStorage.getItem("user") || "null"))

  const isManager = computed(() => user.value?.role === "manager" || user.value?.role === "admin")
  const isAdmin = computed(() => user.value?.role === "admin")

  async function login(username, password) {
    const { data } = await api.post("/auth/login", { username, password })
    setSession(data)
  }

  async function register(username, email, password) {
    const { data } = await api.post("/auth/register", { username, email, password })
    setSession(data)
  }

  function setSession(data) {
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem("token", data.access_token)
    localStorage.setItem("user", JSON.stringify(data.user))
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem("token")
    localStorage.removeItem("user")
  }

  return { token, user, isManager, isAdmin, login, register, logout }
})
