<template>
  <div class="project-card" @click="$emit('click')">
    <div class="project-card-body">
      <h3>{{ project.title }}</h3>
      <p v-if="project.description">{{ project.description }}</p>
      <span class="meta">{{ project.owner?.username }} · {{ formatDate(project.created_at) }}</span>
    </div>
    <div v-if="isManager" class="project-card-actions" @click.stop>
      <button class="btn-icon" @click="$emit('edit')">✏️</button>
      <button class="btn-icon danger" @click="$emit('delete')">🗑</button>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from "@/stores/auth"

const auth = useAuthStore()
const isManager = auth.isManager

defineProps({ project: Object })
defineEmits(["click", "edit", "delete"])

function formatDate(d) {
  return new Date(d).toLocaleDateString("ru-RU")
}
</script>
