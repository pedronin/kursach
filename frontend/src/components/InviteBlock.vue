<template>
  <div v-if="invites.length > 0" class="invite-block">
    <h3>Приглашения</h3>
    <div v-for="inv in invites" :key="inv.id" class="invite-card">
      <div class="invite-info">
        <span class="invite-project">{{ inv.project_title }}</span>
        <span class="invite-from">от {{ inv.inviter.username }}</span>
      </div>
      <div class="invite-actions">
        <button class="btn-accept" @click="accept(inv.id)">Принять</button>
        <button class="btn-decline" @click="decline(inv.id)">Отклонить</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import api from "@/api"

const emit = defineEmits(["accepted"])

const invites = ref([])

onMounted(async () => {
  const { data } = await api.get("/invites/my")
  invites.value = data
})

async function accept(id) {
  await api.post(`/invites/${id}/accept`)
  invites.value = invites.value.filter((i) => i.id !== id)
  emit("accepted")
}

async function decline(id) {
  await api.post(`/invites/${id}/decline`)
  invites.value = invites.value.filter((i) => i.id !== id)
}
</script>
