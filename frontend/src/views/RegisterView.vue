<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="logo">TaskFlow</h1>
      <p class="subtitle">Создать аккаунт</p>

      <form @submit.prevent="submit">
        <div class="field">
          <label>Логин</label>
          <input v-model="form.username" type="text" placeholder="username" required />
        </div>
        <div class="field">
          <label>Email</label>
          <input v-model="form.email" type="email" placeholder="you@example.com" required />
        </div>
        <div class="field">
          <label>Пароль</label>
          <input v-model="form.password" type="password" placeholder="••••••••" required />
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <button type="submit" :disabled="loading">
          {{ loading ? "Создаём..." : "Зарегистрироваться" }}
        </button>
      </form>

      <p class="switch-link">Уже есть аккаунт? <RouterLink to="/login">Войти</RouterLink></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { RouterLink, useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"

const router = useRouter()
const auth = useAuthStore()

const form = ref({ username: "", email: "", password: "" })
const error = ref("")
const loading = ref(false)

async function submit() {
  error.value = ""
  loading.value = true
  try {
    await auth.register(form.value.username, form.value.email, form.value.password)
    router.push("/")
  } catch (e) {
    error.value = e.response?.data?.detail || "Ошибка регистрации"
  } finally {
    loading.value = false
  }
}
</script>
