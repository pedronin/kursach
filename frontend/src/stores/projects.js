import { defineStore } from "pinia"
import { ref } from "vue"
import api from "@/api"

export const useProjectsStore = defineStore("projects", () => {
  const projects = ref([])
  const loading = ref(false)

  async function fetchProjects() {
    loading.value = true
    const { data } = await api.get("/projects/")
    projects.value = data
    loading.value = false
  }

  async function createProject(title, description) {
    const { data } = await api.post("/projects/", { title, description })
    projects.value.push(data)
    return data
  }

  async function updateProject(id, payload) {
    const { data } = await api.put(`/projects/${id}`, payload)
    const idx = projects.value.findIndex((p) => p.id === id)
    if (idx !== -1) projects.value[idx] = data
    return data
  }

  async function deleteProject(id) {
    await api.delete(`/projects/${id}`)
    projects.value = projects.value.filter((p) => p.id !== id)
  }

  return { projects, loading, fetchProjects, createProject, updateProject, deleteProject }
})
