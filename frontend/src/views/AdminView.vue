<template>
  <div class="page">
    <header class="topbar">
      <button class="btn-ghost" @click="router.push('/')">← Назад</button>
      <span class="logo">Панель администратора</span>
      <span class="user-badge">{{ auth.user?.username }}</span>
    </header>

    <main class="content">
      <!-- статистика -->
      <div v-if="stats" class="stats-row" style="margin-bottom: 32px">
        <div class="stat-card">
          <span class="stat-num">{{ stats.total_users }}</span>
          <span class="stat-label">Пользователей</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">{{ stats.total_projects }}</span>
          <span class="stat-label">Проектов</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">{{ stats.total_tasks }}</span>
          <span class="stat-label">Задач</span>
        </div>
        <div class="stat-card">
          <span class="stat-num" style="color: var(--red)">{{ stats.overdue_tasks }}</span>
          <span class="stat-label">Просрочено</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">{{ stats.by_status?.todo }}</span>
          <span class="stat-label">To Do</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">{{ stats.by_status?.in_progress }}</span>
          <span class="stat-label">In Progress</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">{{ stats.by_status?.done }}</span>
          <span class="stat-label">Done</span>
        </div>
      </div>

      <!-- вкладки -->
      <div class="admin-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- пользователи -->
      <div v-if="activeTab === 'users'" class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Username</th>
              <th>Email</th>
              <th>Роль</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td class="mono">{{ u.id }}</td>
              <td>{{ u.username }}</td>
              <td>{{ u.email }}</td>
              <td>
                <select
                  :value="u.role"
                  @change="(e) => changeRole(u.id, e.target.value)"
                  class="role-select"
                  :disabled="u.id === auth.user?.id"
                >
                  <option value="employee">employee</option>
                  <option value="manager">manager</option>
                  <option value="admin">admin</option>
                </select>
              </td>
              <td>
                <button
                  class="btn-icon danger"
                  :disabled="u.id === auth.user?.id"
                  @click="deleteUser(u.id)"
                >
                  Удалить
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- проекты -->
      <div v-if="activeTab === 'projects'" class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Название</th>
              <th>Владелец</th>
              <th>Задач</th>
              <th>Создан</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in projects" :key="p.id">
              <td class="mono">{{ p.id }}</td>
              <td>{{ p.title }}</td>
              <td class="mono">{{ p.owner.username }}</td>
              <td class="mono">{{ p.task_count }}</td>
              <td class="mono">{{ formatDate(p.created_at) }}</td>
              <td>
                <button class="btn-icon danger" @click="deleteProject(p.id)">Удалить</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"
import api from "@/api"

const router = useRouter()
const auth = useAuthStore()

const stats = ref(null)
const users = ref([])
const projects = ref([])
const activeTab = ref("users")

const tabs = [
  { key: "users", label: "Пользователи" },
  { key: "projects", label: "Проекты" },
]

onMounted(async () => {
  const [statsRes, usersRes, projectsRes] = await Promise.all([
    api.get("/admin/stats"),
    api.get("/admin/users"),
    api.get("/admin/projects"),
  ])
  stats.value = statsRes.data
  users.value = usersRes.data
  projects.value = projectsRes.data
})

async function changeRole(userId, role) {
  const { data } = await api.patch(`/admin/users/${userId}`, { role })
  const idx = users.value.findIndex((u) => u.id === userId)
  if (idx !== -1) users.value[idx] = data
}

async function deleteUser(userId) {
  if (!confirm("Удалить пользователя?")) return
  await api.delete(`/admin/users/${userId}`)
  users.value = users.value.filter((u) => u.id !== userId)
}

async function deleteProject(projectId) {
  if (!confirm("Удалить проект и все его задачи?")) return
  await api.delete(`/admin/projects/${projectId}`)
  projects.value = projects.value.filter((p) => p.id !== projectId)
}

function formatDate(d) {
  return new Date(d).toLocaleDateString("ru-RU")
}
</script>
