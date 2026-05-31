<template>
  <div class="comments">
    <h4>Комментарии</h4>

    <div v-if="comments.length === 0" class="empty-small">Комментариев нет</div>

    <div v-for="c in comments" :key="c.id" class="comment">
      <span class="comment-author">{{ c.author.username }}</span>
      <span class="comment-date">{{ formatDate(c.created_at) }}</span>
      <p>{{ c.text }}</p>
    </div>

    <form @submit.prevent="submit" class="comment-form">
      <input v-model="text" placeholder="Написать комментарий..." required />
      <button type="submit" class="btn-primary">Отправить</button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import api from "@/api"

const props = defineProps({ taskId: Number })

const comments = ref([])
const text = ref("")

onMounted(async () => {
  const { data } = await api.get(`/tasks/${props.taskId}/comments`)
  comments.value = data
})

async function submit() {
  const { data } = await api.post(`/tasks/${props.taskId}/comments`, { text: text.value })
  comments.value.push(data)
  text.value = ""
}

function formatDate(d) {
  return new Date(d).toLocaleString("ru-RU")
}
</script>
