<template>
  <div class="page">
    <header class="topbar">
      <span class="logo">TaskFlow</span>
      <div class="topbar-right">
        <button v-if="auth.isAdmin" class="btn-ghost" @click="router.push('/admin')">⚙ Админ</button>
        <span class="user-badge">{{ auth.user?.username }} · {{ auth.user?.role }}</span>
        <button class="btn-ghost" @click="handleLogout">Выйти</button>
      </div>
    </header>

    <main class="content">
      <InviteBlock @accepted="loadAll" />

      <div class="stats-row">
        <div class="stat-card">
          <span class="stat-num">{{ counts.todo }}</span>
          <span class="stat-label">To Do</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">{{ counts.in_progress }}</span>
          <span class="stat-label">In Progress</span>
        </div>
        <div class="stat-card">
          <span class="stat-num">{{ counts.done }}</span>
          <span class="stat-label">Done</span>
        </div>
      </div>

      <div class="section-header">
        <h2>Проекты</h2>
        <div class="section-header-right">
          <input
            v-model="projectSearch"
            placeholder="Поиск по названию..."
            class="search-input"
          />
          <select v-model="projectSort" class="filter-select">
            <option value="desc">Сначала новые</option>
            <option value="asc">Сначала старые</option>
          </select>
          <button v-if="auth.isManager" class="btn-primary" @click="showCreateProject = true">
            + Новый проект
          </button>
        </div>
      </div>

      <div v-if="store.loading" class="empty">Загрузка...</div>

      <div v-else-if="filteredProjects.length === 0" class="empty">
        {{ auth.isManager ? "Создайте первый проект" : "Нет доступных проектов" }}
      </div>

      <div v-else class="projects-grid">
        <ProjectCard
          v-for="p in filteredProjects"
          :key="p.id"
          :project="p"
          @click="router.push(`/projects/${p.id}`)"
          @delete="handleDeleteProject(p.id)"
          @edit="openEditProject(p)"
        />
      </div>
    </main>

    <!-- модалка создания проекта -->
    <div v-if="showCreateProject" class="modal-overlay" @click.self="showCreateProject = false">
      <div class="modal">
        <h3>Новый проект</h3>
        <form @submit.prevent="handleCreateProject">
          <div class="field">
            <label>Название</label>
            <input v-model="projectForm.title" required placeholder="Название проекта" />
          </div>
          <div class="field">
            <label>Описание</label>
            <textarea v-model="projectForm.description" placeholder="Описание" rows="3" />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-ghost" @click="showCreateProject = false">Отмена</button>
            <button type="submit" class="btn-primary">Создать</button>
          </div>
        </form>
      </div>
    </div>

    <!-- модалка редактирования проекта -->
    <div v-if="editingProject" class="modal-overlay" @click.self="editingProject = null">
      <div class="modal">
        <h3>Редактировать проект</h3>
        <form @submit.prevent="handleUpdateProject">
          <div class="field">
            <label>Название</label>
            <input v-model="editForm.title" required />
          </div>
          <div class="field">
            <label>Описание</label>
            <textarea v-model="editForm.description" rows="3" />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-ghost" @click="editingProject = null">Отмена</button>
            <button type="submit" class="btn-primary">Сохранить</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"
import { useProjectsStore } from "@/stores/projects"
import { useTasksStore } from "@/stores/tasks"
import ProjectCard from "@/components/ProjectCard.vue"
import InviteBlock from "@/components/InviteBlock.vue"

const router = useRouter()
const auth = useAuthStore()
const store = useProjectsStore()
const tasksStore = useTasksStore()

const showCreateProject = ref(false)
const projectForm = ref({ title: "", description: "" })
const editingProject = ref(null)
const editForm = ref({ title: "", description: "" })
const projectSearch = ref("")
const projectSort = ref("desc")

const counts = computed(() => ({
  todo: tasksStore.tasks.filter((t) => t.status === "todo").length,
  in_progress: tasksStore.tasks.filter((t) => t.status === "in_progress").length,
  done: tasksStore.tasks.filter((t) => t.status === "done").length,
}))

const filteredProjects = computed(() => {
  let list = [...store.projects]
  if (projectSearch.value.trim()) {
    const q = projectSearch.value.toLowerCase()
    list = list.filter((p) => p.title.toLowerCase().includes(q))
  }
  list.sort((a, b) => {
    const diff = new Date(a.created_at) - new Date(b.created_at)
    return projectSort.value === "desc" ? -diff : diff
  })
  return list
})

onMounted(loadAll)

async function loadAll() {
  await store.fetchProjects()
  // статистика только по задачам своих проектов
  await tasksStore.fetchTasks()
}

async function handleCreateProject() {
  await store.createProject(projectForm.value.title, projectForm.value.description)
  projectForm.value = { title: "", description: "" }
  showCreateProject.value = false
}

function openEditProject(project) {
  editingProject.value = project
  editForm.value = { title: project.title, description: project.description }
}

async function handleUpdateProject() {
  await store.updateProject(editingProject.value.id, editForm.value)
  editingProject.value = null
}

async function handleDeleteProject(id) {
  if (confirm("Удалить проект? Все задачи тоже удалятся.")) {
    await store.deleteProject(id)
  }
}

function handleLogout() {
  auth.logout()
  router.push("/login")
}
</script>
