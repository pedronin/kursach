<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h3>Участники проекта</h3>

      <div class="members-list">
        <div v-if="members.length === 0" class="empty-small">Нет участников</div>
        <div v-for="m in members" :key="m.id" class="member-row">
          <span class="member-name">{{ m.user.username }}</span>
          <span class="member-role">{{ m.user.role }}</span>
          <button class="btn-icon danger" @click="removeMember(m.user_id)">✕</button>
        </div>
      </div>

      <div class="member-add">
        <h4>Пригласить по нику</h4>
        <div class="field-row">
          <div class="field">
            <input v-model="inviteUsername" placeholder="username" @keyup.enter="sendInvite" />
          </div>
          <button class="btn-primary" :disabled="!inviteUsername.trim()" @click="sendInvite">
            Отправить
          </button>
        </div>
        <p v-if="inviteError" class="error">{{ inviteError }}</p>
        <p v-if="inviteSuccess" class="success">{{ inviteSuccess }}</p>
      </div>

      <div class="modal-actions">
        <button class="btn-ghost" @click="$emit('close')">Закрыть</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import api from "@/api"

const props = defineProps({ projectId: Number })
defineEmits(["close"])

const members = ref([])
const inviteUsername = ref("")
const inviteError = ref("")
const inviteSuccess = ref("")

onMounted(async () => {
  const { data } = await api.get(`/projects/${props.projectId}/members`)
  members.value = data
})

async function sendInvite() {
  inviteError.value = ""
  inviteSuccess.value = ""
  try {
    await api.post(`/projects/${props.projectId}/invites`, { username: inviteUsername.value.trim() })
    inviteSuccess.value = `Приглашение отправлено пользователю ${inviteUsername.value}`
    inviteUsername.value = ""
  } catch (e) {
    inviteError.value = e.response?.data?.detail || "Ошибка"
  }
}

async function removeMember(userId) {
  await api.delete(`/projects/${props.projectId}/members/${userId}`)
  members.value = members.value.filter((m) => m.user_id !== userId)
}
</script>
