import { defineStore } from "pinia"
import { ref } from "vue"
import api from "@/api"

export const useTasksStore = defineStore("tasks", () => {
  const tasks = ref([])
  const loading = ref(false)

  async function fetchTasks(params = {}) {
    loading.value = true
    const { data } = await api.get("/tasks/", { params })
    tasks.value = data
    loading.value = false
    return data
  }

  async function createTask(payload) {
    const { data } = await api.post("/tasks/", payload)
    tasks.value.push(data)
    return data
  }

  async function updateTask(id, payload) {
    const { data } = await api.patch(`/tasks/${id}`, payload)
    const idx = tasks.value.findIndex((t) => t.id === id)
    if (idx !== -1) tasks.value[idx] = data
    return data
  }

  async function deleteTask(id) {
    await api.delete(`/tasks/${id}`)
    tasks.value = tasks.value.filter((t) => t.id !== id)
  }

  return { tasks, loading, fetchTasks, createTask, updateTask, deleteTask }
})
