<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="logo">TaskFlow</h1>
      <p class="subtitle">Войдите в аккаунт</p>

      <form @submit.prevent="submit">
        <div class="field">
          <label>Логин</label>
          <input v-model="form.username" type="text" placeholder="username" required />
        </div>
        <div class="field">
          <label>Пароль</label>
          <input v-model="form.password" type="password" placeholder="••••••••" required />
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <button type="submit" :disabled="loading">
          {{ loading ? "Вход..." : "Войти" }}
        </button>
      </form>

      <p class="switch-link">Нет аккаунта? <RouterLink to="/register">Зарегистрироваться</RouterLink></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { RouterLink, useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"

const router = useRouter()
const auth = useAuthStore()

const form = ref({ username: "", password: "" })
const error = ref("")
const loading = ref(false)

async function submit() {
  error.value = ""
  loading.value = true
  try {
    await auth.login(form.value.username, form.value.password)
    router.push("/")
  } catch (e) {
    error.value = e.response?.data?.detail || "Ошибка входа"
  } finally {
    loading.value = false
  }
}
</script>
