<template>
  <div class="analytics-content">
    <div v-if="loading" class="empty" style="padding: 60px">Загрузка...</div>
    <div v-else-if="error" class="error" style="padding: 24px">{{ error }}</div>
    <template v-else>
      <div class="stats-row">
        <div class="stat-card">
          <span class="stat-num">{{ summary.total ?? 0 }}</span>
          <span class="stat-label">Всего задач</span>
        </div>
        <div class="stat-card">
          <span class="stat-num stat-muted">{{ summary.by_status?.todo ?? 0 }}</span>
          <span class="stat-label">To Do</span>
        </div>
        <div class="stat-card">
          <span class="stat-num stat-blue">{{ summary.by_status?.in_progress ?? 0 }}</span>
          <span class="stat-label">В работе</span>
        </div>
        <div class="stat-card">
          <span class="stat-num stat-green">{{ summary.by_status?.done ?? 0 }}</span>
          <span class="stat-label">Выполнено</span>
        </div>
        <div class="stat-card">
          <span class="stat-num stat-red">{{ summary.overdue ?? 0 }}</span>
          <span class="stat-label">Просрочено</span>
        </div>
      </div>

      <div class="analytics-charts">
        <div class="chart-card">
          <div class="chart-title">Динамика создания задач (30 дней)</div>
          <canvas ref="timelineCanvas"></canvas>
        </div>
        <div class="chart-card">
          <div class="chart-title">Загрузка команды</div>
          <div v-if="workload.length === 0" class="empty-small" style="padding: 40px 0; text-align: center">
            Нет назначенных задач
          </div>
          <canvas v-else ref="workloadCanvas"></canvas>
        </div>
      </div>

      <div class="risks-section">
        <div class="chart-title">Задачи с риском срыва дедлайна (ближайшие 7 дней)</div>
        <div v-if="risks.length === 0" class="empty-small" style="margin-top: 12px">
          Нет задач с горящими дедлайнами
        </div>
        <div v-else class="admin-table-wrap" style="margin-top: 12px">
          <table class="admin-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Задача</th>
                <th>Дедлайн</th>
                <th>Статус</th>
                <th>Приоритет</th>
                <th>Исполнитель</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in risks" :key="t.id">
                <td class="mono">{{ t.id }}</td>
                <td>{{ t.title }}</td>
                <td class="mono" :style="{ color: t.is_overdue ? 'var(--red)' : 'var(--orange)' }">
                  {{ formatDate(t.deadline) }}
                  <span v-if="t.is_overdue" style="font-size: 10px; opacity: 0.8"> просрочена</span>
                </td>
                <td><StatusBadge :status="t.status" /></td>
                <td>
                  <span class="priority-dot risk-dot" :class="`dot-${t.priority}`"></span>
                  {{ priorityLabel[t.priority] }}
                </td>
                <td class="mono">{{ t.assignee ?? '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from "vue"
import Chart from "chart.js/auto"
import api from "@/api"
import StatusBadge from "@/components/StatusBadge.vue"

const props = defineProps({ projectId: Number })

const loading = ref(true)
const error = ref(null)
const summary = ref({})
const risks = ref([])
const workload = ref([])
const timelineCanvas = ref(null)
const workloadCanvas = ref(null)
let timelineChart = null
let workloadChart = null

const priorityLabel = { low: "Низкий", medium: "Средний", high: "Высокий" }

const chartColors = {
  text: "#6b6b6b",
  border: "#2e2e2e",
  grid: "#1e1e1e",
}

onMounted(async () => {
  try {
    const [sumRes, tlRes, wlRes, riskRes] = await Promise.all([
      api.get(`/analytics/${props.projectId}/summary`),
      api.get(`/analytics/${props.projectId}/timeline`),
      api.get(`/analytics/${props.projectId}/workload`),
      api.get(`/analytics/${props.projectId}/risks`),
    ])

    summary.value = sumRes.data
    risks.value = riskRes.data
    workload.value = wlRes.data

    const timeline = tlRes.data

    loading.value = false
    await nextTick()

    timelineChart = new Chart(timelineCanvas.value, {
      type: "line",
      data: {
        labels: timeline.map((d) => d.date.slice(5)),
        datasets: [
          {
            label: "Создано задач",
            data: timeline.map((d) => d.count),
            borderColor: "#e8ff47",
            backgroundColor: "rgba(232, 255, 71, 0.07)",
            borderWidth: 2,
            pointRadius: 3,
            pointBackgroundColor: "#e8ff47",
            fill: true,
            tension: 0.35,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
        },
        scales: {
          x: {
            grid: { color: chartColors.grid },
            ticks: { color: chartColors.text, maxTicksLimit: 10 },
          },
          y: {
            grid: { color: chartColors.grid },
            ticks: { color: chartColors.text, stepSize: 1 },
            beginAtZero: true,
          },
        },
      },
    })

    if (wlRes.data.length > 0) {
      workloadChart = new Chart(workloadCanvas.value, {
        type: "bar",
        data: {
          labels: wlRes.data.map((w) => w.username),
          datasets: [
            {
              label: "To Do",
              data: wlRes.data.map((w) => w.todo),
              backgroundColor: "#3a3a3a",
              borderRadius: 3,
            },
            {
              label: "В работе",
              data: wlRes.data.map((w) => w.in_progress),
              backgroundColor: "#4d9fff",
              borderRadius: 3,
            },
            {
              label: "Готово",
              data: wlRes.data.map((w) => w.done),
              backgroundColor: "#4dff91",
              borderRadius: 3,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              labels: { color: chartColors.text, boxWidth: 12, font: { size: 11 } },
            },
          },
          scales: {
            x: {
              grid: { color: chartColors.grid },
              ticks: { color: chartColors.text },
              stacked: true,
            },
            y: {
              grid: { color: chartColors.grid },
              ticks: { color: chartColors.text, stepSize: 1 },
              beginAtZero: true,
              stacked: true,
            },
          },
        },
      })
    }
  } catch (e) {
    error.value = "Не удалось загрузить аналитику"
    loading.value = false
  }
})

onUnmounted(() => {
  timelineChart?.destroy()
  workloadChart?.destroy()
})

function formatDate(d) {
  return new Date(d).toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  })
}
</script>
