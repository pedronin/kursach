<template>
  <div class="page">
    <header class="topbar">
      <button class="btn-ghost" @click="router.push('/')">← Назад</button>
      <div class="topbar-center">
        <span class="logo">{{ project?.title }}</span>
        <span class="project-desc">{{ project?.description }}</span>
      </div>
      <div class="topbar-right">
        <input v-model="filterSearch" @input="applyFilters" placeholder="Поиск..." class="search-input search-input-sm" />
        <select v-model="filterStatus" @change="applyFilters" class="filter-select">
          <option value="">Все статусы</option>
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="done">Done</option>
        </select>
        <select v-model="filterPriority" @change="applyFilters" class="filter-select">
          <option value="">Все приоритеты</option>
          <option value="high">Высокий</option>
          <option value="medium">Средний</option>
          <option value="low">Низкий</option>
        </select>
        <select v-model="filterAssignee" @change="applyFilters" class="filter-select">
          <option value="">Все исполнители</option>
          <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
        </select>
        <div class="sort-group">
          <select v-model="sortBy" @change="applyFilters" class="filter-select sort-select">
            <option value="created_at">По дате создания</option>
            <option value="deadline">По дедлайну</option>
            <option value="priority">По приоритету</option>
          </select>
          <button class="sort-dir-btn" @click="toggleSortDir" :title="sortDir === 'desc' ? 'По убыванию' : 'По возрастанию'">
            {{ sortDir === 'desc' ? '↓' : '↑' }}
          </button>
        </div>
        <span class="user-badge">{{ auth.user?.username }}</span>
        <button v-if="auth.isManager" class="btn-ghost" @click="showMembers = true">Участники</button>
        <button v-if="auth.isManager" class="btn-primary" @click="showCreateTask = true">+ Задача</button>
      </div>
    </header>

    <main class="kanban-layout">
      <div class="kanban-board">
        <div
          v-for="col in columns"
          :key="col.status"
          class="kanban-col"
          :class="`col-${col.status}`"
          @dragover.prevent
          @drop="onDrop($event, col.status)"
          @dragenter.prevent="dragOverCol = col.status"
          @dragleave="onDragLeave"
          :data-active="dragOverCol === col.status"
        >
          <div class="col-header">
            <span class="col-title">{{ col.label }}</span>
            <span class="col-count">{{ tasksByStatus(col.status).length }}</span>
          </div>

          <div class="col-cards">
            <div
              v-for="task in tasksByStatus(col.status)"
              :key="task.id"
              class="kanban-card"
              :class="`priority-${task.priority}`"
              draggable="true"
              @dragstart="onDragStart($event, task)"
              @dragend="onDragEnd"
              @click="openTask(task)"
            >
              <div class="card-top">
                <span class="priority-dot" :class="`dot-${task.priority}`"></span>
                <span class="card-id">#{{ task.id }}</span>
              </div>
              <p class="card-title">{{ task.title }}</p>
              <div class="card-meta">
                <span v-if="task.assignee" class="card-assignee">{{ task.assignee.username }}</span>
                <span v-if="task.deadline" class="card-deadline" :class="{ overdue: isOverdue(task.deadline) }">
                  {{ formatDate(task.deadline) }}
                </span>
              </div>
            </div>

            <div v-if="tasksByStatus(col.status).length === 0" class="col-empty">
              Нет задач
            </div>
          </div>
        </div>
      </div>

      <div class="project-chat">
        <div class="chat-header">
          <span>Чат проекта</span>
          <span class="col-count">{{ projectComments.length }}</span>
        </div>
        <div class="chat-messages" ref="chatEl">
          <div v-if="projectComments.length === 0" class="empty-small">Нет сообщений</div>
          <div v-for="c in projectComments" :key="c.id" class="chat-msg">
            <div class="chat-msg-top">
              <span class="chat-author">{{ c.author.username }}</span>
              <span class="chat-time">{{ formatTime(c.created_at) }}</span>
            </div>
            <p>{{ c.text }}</p>
          </div>
        </div>
        <form class="chat-form" @submit.prevent="sendProjectComment">
          <input v-model="chatText" placeholder="Написать сообщение..." required />
          <button type="submit" class="btn-primary">↑</button>
        </form>
      </div>
    </main>

    <!-- модалка создания задачи -->
    <div v-if="showCreateTask" class="modal-overlay" @click.self="showCreateTask = false">
      <div class="modal">
        <h3>Новая задача</h3>
        <form @submit.prevent="handleCreateTask">
          <div class="field">
            <label>Название</label>
            <input v-model="taskForm.title" required placeholder="Что нужно сделать" />
          </div>
          <div class="field">
            <label>Описание</label>
            <textarea v-model="taskForm.description" rows="3" placeholder="Подробности" />
          </div>
          <div class="field-row">
            <div class="field">
              <label>Приоритет</label>
              <select v-model="taskForm.priority">
                <option value="low">Низкий</option>
                <option value="medium">Средний</option>
                <option value="high">Высокий</option>
              </select>
            </div>
            <div class="field">
              <label>Статус</label>
              <select v-model="taskForm.status">
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="done">Done</option>
              </select>
            </div>
          </div>
          <div class="field-row">
            <div class="field">
              <label>Дедлайн <span class="optional">(необязательно)</span></label>
              <input v-model="taskForm.deadline" type="datetime-local" />
            </div>
            <div class="field">
              <label>Исполнитель</label>
              <select v-model="taskForm.assignee_id">
                <option :value="null">Не назначен</option>
                <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
              </select>
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-ghost" @click="showCreateTask = false">Отмена</button>
            <button type="submit" class="btn-primary">Создать</button>
          </div>
        </form>
      </div>
    </div>

    <!-- модалка задачи -->
    <div v-if="activeTask" class="modal-overlay" @click.self="activeTask = null">
      <div class="modal modal-task">
        <div class="task-modal-header">
          <div class="task-modal-id">#{{ activeTask.id }}</div>
          <div class="task-modal-actions" v-if="auth.isManager">
            <button class="btn-ghost btn-sm" @click="startEditTask">Редактировать</button>
            <button class="btn-danger btn-sm" @click="handleDeleteTask(activeTask.id)">Удалить</button>
          </div>
        </div>

        <!-- режим просмотра -->
        <template v-if="!editingActiveTask">
          <h2 class="task-modal-title">{{ activeTask.title }}</h2>
          <p v-if="activeTask.description" class="task-modal-desc">{{ activeTask.description }}</p>

          <div class="task-modal-meta">
            <div class="meta-item">
              <span class="meta-label">Статус</span>
              <StatusBadge :status="activeTask.status" />
            </div>
            <div class="meta-item">
              <span class="meta-label">Приоритет</span>
              <span class="priority-tag" :class="`priority-text-${activeTask.priority}`">
                {{ priorityLabel[activeTask.priority] }}
              </span>
            </div>
            <div class="meta-item" v-if="activeTask.assignee">
              <span class="meta-label">Исполнитель</span>
              <span>{{ activeTask.assignee.username }}</span>
            </div>
            <div class="meta-item" v-if="activeTask.deadline">
              <span class="meta-label">Дедлайн</span>
              <span :class="{ overdue: isOverdue(activeTask.deadline) }">{{ formatDate(activeTask.deadline) }}</span>
            </div>
          </div>

          <!-- смена статуса для сотрудника -->
          <div v-if="!auth.isManager && activeTask.assignee_id === auth.user?.id" class="field" style="margin-top: 16px">
            <label>Сменить статус</label>
            <select :value="activeTask.status" @change="(e) => quickStatusChange(activeTask.id, e.target.value)">
              <option value="todo">To Do</option>
              <option value="in_progress">In Progress</option>
              <option value="done">Done</option>
            </select>
          </div>
        </template>

        <!-- режим редактирования -->
        <template v-else>
          <form @submit.prevent="saveEditTask">
            <div class="field">
              <label>Название</label>
              <input v-model="editTaskForm.title" required />
            </div>
            <div class="field">
              <label>Описание</label>
              <textarea v-model="editTaskForm.description" rows="3" />
            </div>
            <div class="field-row">
              <div class="field">
                <label>Приоритет</label>
                <select v-model="editTaskForm.priority">
                  <option value="low">Низкий</option>
                  <option value="medium">Средний</option>
                  <option value="high">Высокий</option>
                </select>
              </div>
              <div class="field">
                <label>Статус</label>
                <select v-model="editTaskForm.status">
                  <option value="todo">To Do</option>
                  <option value="in_progress">In Progress</option>
                  <option value="done">Done</option>
                </select>
              </div>
            </div>
            <div class="field-row">
              <div class="field">
                <label>Дедлайн</label>
                <input v-model="editTaskForm.deadline" type="datetime-local" />
              </div>
              <div class="field">
                <label>Исполнитель</label>
                <select v-model="editTaskForm.assignee_id">
                  <option :value="null">Не назначен</option>
                  <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
                </select>
              </div>
            </div>
            <div class="modal-actions">
              <button type="button" class="btn-ghost" @click="editingActiveTask = false">Отмена</button>
              <button type="submit" class="btn-primary">Сохранить</button>
            </div>
          </form>
        </template>

        <!-- комментарии к задаче -->
        <div class="task-comments">
          <h4>Комментарии</h4>
          <div class="comments-list">
            <div v-if="taskComments.length === 0" class="empty-small">Нет комментариев</div>
            <div v-for="c in taskComments" :key="c.id" class="comment">
              <div class="comment-top">
                <span class="comment-author">{{ c.author.username }}</span>
                <span class="comment-time">{{ formatTime(c.created_at) }}</span>
              </div>
              <p>{{ c.text }}</p>
            </div>
          </div>
          <form class="comment-form" @submit.prevent="sendTaskComment">
            <input v-model="taskCommentText" placeholder="Написать комментарий..." required />
            <button type="submit" class="btn-primary">↑</button>
          </form>
        </div>
      </div>
    </div>
  </div>
    <!-- модалка участников -->
    <MembersModal
      v-if="showMembers"
      :project-id="parseInt(route.params.id)"
      @close="showMembers = false"
    />
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useAuthStore } from "@/stores/auth"
import { useTasksStore } from "@/stores/tasks"
import api from "@/api"
import StatusBadge from "@/components/StatusBadge.vue"
import MembersModal from "@/components/MembersModal.vue"

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const store = useTasksStore()

const project = ref(null)
const users = ref([])
const projectComments = ref([])
const chatText = ref("")
const chatEl = ref(null)

const activeTask = ref(null)
const taskComments = ref([])
const taskCommentText = ref("")
const editingActiveTask = ref(false)
const editTaskForm = ref({})

const showCreateTask = ref(false)
const showMembers = ref(false)
const taskForm = ref({ title: "", description: "", priority: "medium", status: "todo", deadline: null, assignee_id: null })

const filterSearch = ref('')
const filterStatus = ref('')
const filterPriority = ref('')
const filterAssignee = ref(auth.user?.role === 'employee' ? auth.user.id : '')
const sortBy = ref('created_at')
const sortDir = ref('desc')
const draggedTask = ref(null)
const dragOverCol = ref(null)

const priorityLabel = { low: "Низкий", medium: "Средний", high: "Высокий" }

const columns = [
  { status: "todo", label: "To Do" },
  { status: "in_progress", label: "In Progress" },
  { status: "done", label: "Done" },
]

const tasksByStatus = (status) => store.tasks.filter((t) => t.status === status)

onMounted(async () => {
  const [projectRes, usersRes] = await Promise.all([
    api.get(`/projects/${route.params.id}`),
    api.get("/users/"),
  ])
  project.value = projectRes.data
  users.value = usersRes.data

  await store.fetchTasks({ project_id: route.params.id })
  await loadProjectComments()
})

async function applyFilters() {
  const params = { project_id: route.params.id, sort_by: sortBy.value, sort_dir: sortDir.value }
  if (filterSearch.value) params.search = filterSearch.value
  if (filterStatus.value) params.status = filterStatus.value
  if (filterPriority.value) params.priority = filterPriority.value
  if (filterAssignee.value) params.assignee_id = filterAssignee.value
  await store.fetchTasks(params)
}

function toggleSortDir() {
  sortDir.value = sortDir.value === 'desc' ? 'asc' : 'desc'
  applyFilters()
}

async function loadProjectComments() {
  const { data } = await api.get(`/projects/${route.params.id}/comments`)
  projectComments.value = data
  await nextTick()
  if (chatEl.value) chatEl.value.scrollTop = chatEl.value.scrollHeight
}

async function sendProjectComment() {
  const { data } = await api.post(`/projects/${route.params.id}/comments`, { text: chatText.value })
  projectComments.value.push(data)
  chatText.value = ""
  await nextTick()
  if (chatEl.value) chatEl.value.scrollTop = chatEl.value.scrollHeight
}

async function openTask(task) {
  activeTask.value = task
  editingActiveTask.value = false
  const { data } = await api.get(`/tasks/${task.id}/comments`)
  taskComments.value = data
}

async function sendTaskComment() {
  const { data } = await api.post(`/tasks/${activeTask.value.id}/comments`, { text: taskCommentText.value })
  taskComments.value.push(data)
  taskCommentText.value = ""
}

function startEditTask() {
  editTaskForm.value = {
    title: activeTask.value.title,
    description: activeTask.value.description,
    priority: activeTask.value.priority,
    status: activeTask.value.status,
    deadline: activeTask.value.deadline ? activeTask.value.deadline.slice(0, 16) : null,
    assignee_id: activeTask.value.assignee_id,
  }
  editingActiveTask.value = true
}

async function saveEditTask() {
  const updated = await store.updateTask(activeTask.value.id, {
    ...editTaskForm.value,
    deadline: editTaskForm.value.deadline || null,
  })
  activeTask.value = updated
  editingActiveTask.value = false
}

async function handleDeleteTask(id) {
  if (confirm("Удалить задачу?")) {
    await store.deleteTask(id)
    activeTask.value = null
  }
}

async function quickStatusChange(id, status) {
  const updated = await store.updateTask(id, { status })
  activeTask.value = updated
}

async function handleCreateTask() {
  await store.createTask({
    ...taskForm.value,
    project_id: parseInt(route.params.id),
    deadline: taskForm.value.deadline || null,
  })
  taskForm.value = { title: "", description: "", priority: "medium", status: "todo", deadline: null, assignee_id: null }
  showCreateTask.value = false
}

function onDragStart(e, task) {
  draggedTask.value = task
  e.dataTransfer.effectAllowed = "move"
}

function onDragEnd() {
  draggedTask.value = null
  dragOverCol.value = null
}

function onDragLeave(e) {
  // убираем подсветку только если вышли за пределы колонки
  if (!e.currentTarget.contains(e.relatedTarget)) {
    dragOverCol.value = null
  }
}

async function onDrop(e, newStatus) {
  dragOverCol.value = null
  if (!draggedTask.value || draggedTask.value.status === newStatus) return
  await store.updateTask(draggedTask.value.id, { status: newStatus })
  draggedTask.value = null
}

function formatDate(d) {
  return new Date(d).toLocaleDateString("ru-RU")
}

function formatTime(d) {
  return new Date(d).toLocaleString("ru-RU", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" })
}

function isOverdue(d) {
  return new Date(d) < new Date()
}
</script>
