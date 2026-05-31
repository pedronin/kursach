<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h3>Редактировать задачу</h3>
      <form @submit.prevent="submit">
        <div class="field">
          <label>Название</label>
          <input v-model="form.title" required />
        </div>
        <div class="field">
          <label>Описание</label>
          <textarea v-model="form.description" rows="3" />
        </div>
        <div class="field-row">
          <div class="field">
            <label>Приоритет</label>
            <select v-model="form.priority">
              <option value="low">Низкий</option>
              <option value="medium">Средний</option>
              <option value="high">Высокий</option>
            </select>
          </div>
          <div class="field">
            <label>Статус</label>
            <select v-model="form.status">
              <option value="todo">To Do</option>
              <option value="in_progress">In Progress</option>
              <option value="done">Done</option>
            </select>
          </div>
        </div>
        <div class="field-row">
          <div class="field">
            <label>Дедлайн</label>
            <input v-model="form.deadline" type="datetime-local" />
          </div>
          <div class="field">
            <label>Исполнитель</label>
            <select v-model="form.assignee_id">
              <option :value="null">Не назначен</option>
              <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
            </select>
          </div>
        </div>

        <CommentList :task-id="task.id" />

        <div class="modal-actions">
          <button type="button" class="btn-ghost" @click="$emit('close')">Отмена</button>
          <button type="submit" class="btn-primary">Сохранить</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import CommentList from "@/components/CommentList.vue"

const props = defineProps({ task: Object, users: Array })
const emit = defineEmits(["save", "close"])

const form = ref({
  title: props.task.title,
  description: props.task.description,
  priority: props.task.priority,
  status: props.task.status,
  deadline: props.task.deadline ? props.task.deadline.slice(0, 16) : null,
  assignee_id: props.task.assignee_id,
})

function submit() {
  emit("save", { ...form.value, deadline: form.value.deadline || null })
}
</script>
