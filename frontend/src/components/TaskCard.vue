<template>
  <div class="task-card" :class="`priority-${task.priority}`">
    <div class="task-card-top">
      <StatusBadge :status="task.status" />
      <span class="priority-tag">{{ priorityLabel[task.priority] }}</span>
    </div>

    <h4>{{ task.title }}</h4>
    <p v-if="task.description" class="task-desc">{{ task.description }}</p>

    <div class="task-meta">
      <span v-if="task.assignee">👤 {{ task.assignee.username }}</span>
      <span v-if="task.deadline">📅 {{ formatDate(task.deadline) }}</span>
    </div>

    <div class="task-card-actions">
      <select :value="task.status" @change="(e) => $emit('status-change', e.target.value)" class="status-select">
        <option value="todo">To Do</option>
        <option value="in_progress">In Progress</option>
        <option value="done">Done</option>
      </select>
      <div v-if="isManager" class="task-btns">
        <button class="btn-icon" @click="$emit('edit')">✏️</button>
        <button class="btn-icon danger" @click="$emit('delete')">🗑</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import StatusBadge from "@/components/StatusBadge.vue"
import { useAuthStore } from "@/stores/auth"

const auth = useAuthStore()
const isManager = auth.isManager

defineProps({ task: Object })
defineEmits(["edit", "delete", "status-change"])

const priorityLabel = { low: "Низкий", medium: "Средний", high: "Высокий" }

function formatDate(d) {
  return new Date(d).toLocaleDateString("ru-RU")
}
</script>
