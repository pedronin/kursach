<template>
  <div class="analytics-content">
    <div v-if="loading" class="empty" style="padding: 60px">Загрузка...</div>
    <div v-else-if="error" class="error" style="padding: 24px">{{ error }}</div>
    <template v-else>

      <!-- Коэффициенты -->
      <div class="coeff-row">
        <div class="coeff-card">
          <div class="coeff-label">Индекс риска проекта</div>
          <div class="coeff-value" :style="{ color: riskColor }">{{ summary.risk_index ?? 0 }}<span class="coeff-unit">%</span></div>
          <div class="coeff-desc">{{ riskLabel }}</div>
        </div>
        <div class="coeff-card">
          <div class="coeff-label">Выполнено задач</div>
          <div class="coeff-value" style="color: var(--green)">{{ summary.completion_rate ?? 0 }}<span class="coeff-unit">%</span></div>
          <div class="coeff-desc">{{ summary.by_status?.done ?? 0 }} из {{ summary.total ?? 0 }}</div>
        </div>
        <div class="coeff-card">
          <div class="coeff-label">Просрочено</div>
          <div class="coeff-value" :style="{ color: summary.overdue > 0 ? 'var(--red)' : 'var(--green)' }">{{ summary.overdue ?? 0 }}</div>
          <div class="coeff-desc">незакрытых задач с истёкшим дедлайном</div>
        </div>
        <div class="coeff-card">
          <div class="coeff-label">В работе</div>
          <div class="coeff-value" style="color: var(--blue)">{{ summary.by_status?.in_progress ?? 0 }}</div>
          <div class="coeff-desc">из {{ summary.total ?? 0 }} всего задач</div>
        </div>
      </div>

      <!-- Графики -->
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

      <!-- Индекс нагрузки по сотрудникам -->
      <div class="risks-section" style="margin-bottom: 16px">
        <div class="chart-title">Индекс нагрузки сотрудников</div>
        <div class="coeff-note">Взвешенная сумма активных задач: высокий приоритет × 3, средний × 2, низкий × 1</div>
        <div v-if="workload.length === 0" class="empty-small" style="margin-top: 12px">Нет данных</div>
        <div v-else class="admin-table-wrap" style="margin-top: 12px">
          <table class="admin-table">
            <thead>
              <tr>
                <th>Сотрудник</th>
                <th>Индекс нагрузки</th>
                <th>В работе</th>
                <th>Готово</th>
                <th>Просрочено</th>
                <th>Статус</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="w in workload" :key="w.user_id">
                <td>{{ w.username }}</td>
                <td class="mono" :style="{ color: workloadLevel(w.workload_index).color, fontWeight: 600 }">
                  {{ w.workload_index }}%
                </td>
                <td class="mono">{{ w.in_progress }}</td>
                <td class="mono" style="color: var(--green)">{{ w.done }}</td>
                <td class="mono" :style="{ color: w.overdue > 0 ? 'var(--red)' : 'var(--text-muted)' }">{{ w.overdue }}</td>
                <td>
                  <span class="workload-badge" :style="{ background: workloadLevel(w.workload_index).bg, color: workloadLevel(w.workload_index).color }">
                    {{ workloadLevel(w.workload_index).label }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Факт нарушений: уже просроченные задачи -->
      <div class="risks-section" style="margin-bottom: 16px">
        <div class="chart-title">
          Просроченные задачи
          <span class="section-tag section-tag--fact">Факт нарушения</span>
        </div>
        <div class="coeff-note">Дедлайн уже истёк — это зафиксированное нарушение сроков, не прогноз</div>
        <div v-if="overdueRisks.length === 0" class="empty-small" style="margin-top: 12px; color: var(--green)">
          Нет просроченных задач
        </div>
        <div v-else class="admin-table-wrap" style="margin-top: 12px">
          <table class="admin-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Задача</th>
                <th>Дедлайн истёк</th>
                <th>Статус</th>
                <th>Приоритет</th>
                <th>Исполнитель</th>
                <th>Нагрузка исп.</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in overdueRisks" :key="t.id">
                <td class="mono">{{ t.id }}</td>
                <td>{{ t.title }}</td>
                <td class="mono" style="color: var(--red)">{{ formatDate(t.deadline) }}</td>
                <td><StatusBadge :status="t.status" /></td>
                <td>
                  <span class="priority-dot risk-dot" :class="`dot-${t.priority}`"></span>
                  {{ priorityLabel[t.priority] }}
                </td>
                <td class="mono">{{ t.assignee ?? '—' }}</td>
                <td class="mono" :style="{ color: workloadLevel(t.assignee_workload).color, fontWeight: 600 }">
                  {{ t.assignee_workload }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Прогноз рисков: ближайшие 7 дней -->
      <div class="risks-section">
        <div class="chart-title">
          Прогнозные риски срыва сроков
          <span class="section-tag section-tag--risk">Прогноз · 7 дней</span>
        </div>
        <div class="coeff-note">
          Риск задачи R = min(100, D × Kp × Kw), где D — срочность дедлайна, Kp — коэффициент приоритета, Kw — коэффициент загруженности исполнителя
        </div>
        <div v-if="upcomingRisks.length === 0" class="empty-small" style="margin-top: 12px">
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
                <th>Нагрузка исп.</th>
                <th>Риск задачи</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in upcomingRisks" :key="t.id">
                <td class="mono">{{ t.id }}</td>
                <td>{{ t.title }}</td>
                <td class="mono" style="color: var(--orange)">{{ formatDate(t.deadline) }}</td>
                <td><StatusBadge :status="t.status" /></td>
                <td>
                  <span class="priority-dot risk-dot" :class="`dot-${t.priority}`"></span>
                  {{ priorityLabel[t.priority] }}
                </td>
                <td class="mono">{{ t.assignee ?? '—' }}</td>
                <td class="mono" :style="{ color: workloadLevel(t.assignee_workload).color, fontWeight: 600 }">
                  {{ t.assignee_workload }}%
                </td>
                <td>
                  <span class="task-risk-badge" :style="{ color: taskRiskLevel(t.task_risk).color, background: taskRiskLevel(t.task_risk).bg }">
                    {{ t.task_risk }}%
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from "vue"
import Chart from "chart.js/auto"
import api from "@/api"
import StatusBadge from "@/components/StatusBadge.vue"
import { useTheme } from "@/composables/useTheme"

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

const { isDark } = useTheme()

const priorityLabel = { low: "Низкий", medium: "Средний", high: "Высокий" }

const chartColors = computed(() => isDark.value
  ? { text: "#6b6b6b", grid: "#2a2a2a" }
  : { text: "#888888", grid: "#e0e0da" }
)

const riskColor = computed(() => {
  const r = summary.value.risk_index ?? 0
  if (r >= 60) return "var(--red)"
  if (r >= 30) return "var(--orange)"
  return "var(--green)"
})

const riskLabel = computed(() => {
  const r = summary.value.risk_index ?? 0
  if (r >= 60) return "Высокий риск срыва сроков"
  if (r >= 30) return "Умеренный риск — требует внимания"
  return "Проект идёт в штатном режиме"
})

function taskRiskLevel(risk) {
  if (risk >= 70) return { color: "var(--red)",    bg: "rgba(255,77,77,0.12)" }
  if (risk >= 40) return { color: "var(--orange)", bg: "rgba(255,148,77,0.12)" }
  return                 { color: "var(--green)",  bg: "rgba(77,255,145,0.12)" }
}

function workloadLevel(index) {
  if (index >= 10) return { color: "var(--red)",    bg: "rgba(255,77,77,0.12)",   label: "Перегружен" }
  if (index >= 5)  return { color: "var(--orange)", bg: "rgba(255,148,77,0.12)",  label: "Умеренно" }
  return                   { color: "var(--green)", bg: "rgba(77,255,145,0.12)",  label: "Свободен" }
}

// Факты нарушений — уже просрочены, сортируем по дедлайну (сначала старейшие)
const overdueRisks = computed(() =>
  risks.value
    .filter(r => r.is_overdue)
    .sort((a, b) => new Date(a.deadline) - new Date(b.deadline))
)

// Прогнозные риски — дедлайн ещё не наступил, сортируем по task_risk (самые рискованные сверху)
const upcomingRisks = computed(() =>
  risks.value
    .filter(r => !r.is_overdue)
    .sort((a, b) => b.task_risk - a.task_risk)
)

const timelineData = ref([])

function initCharts() {
  timelineChart?.destroy()
  workloadChart?.destroy()
  timelineChart = null
  workloadChart = null

  const c = chartColors.value

  if (timelineCanvas.value) {
    timelineChart = new Chart(timelineCanvas.value, {
      type: "line",
      data: {
        labels: timelineData.value.map((d) => d.date.slice(5)),
        datasets: [{
          label: "Создано задач",
          data: timelineData.value.map((d) => d.count),
          borderColor: "#e8ff47",
          backgroundColor: "rgba(232, 255, 71, 0.07)",
          borderWidth: 2,
          pointRadius: 3,
          pointBackgroundColor: "#e8ff47",
          fill: true,
          tension: 0.35,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: c.grid }, ticks: { color: c.text, maxTicksLimit: 10 } },
          y: { grid: { color: c.grid }, ticks: { color: c.text, precision: 0 }, beginAtZero: true },
        },
      },
    })
  }

  if (workload.value.length > 0 && workloadCanvas.value) {
    const todoBg = isDark.value ? "#3a3a3a" : "#d0d0cc"
    workloadChart = new Chart(workloadCanvas.value, {
      type: "bar",
      data: {
        labels: workload.value.map((w) => w.username),
        datasets: [
          { label: "To Do",    data: workload.value.map((w) => w.todo),        backgroundColor: todoBg,    borderRadius: 3 },
          { label: "В работе", data: workload.value.map((w) => w.in_progress), backgroundColor: "#4d9fff", borderRadius: 3 },
          { label: "Готово",   data: workload.value.map((w) => w.done),        backgroundColor: "#4dff91", borderRadius: 3 },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { labels: { color: c.text, boxWidth: 12, font: { size: 11 } } } },
        scales: {
          x: { grid: { color: c.grid }, ticks: { color: c.text }, stacked: true },
          y: { grid: { color: c.grid }, ticks: { color: c.text, precision: 0 }, beginAtZero: true, stacked: true },
        },
      },
    })
  }
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
    timelineData.value = tlRes.data

    loading.value = false
    await nextTick()
    initCharts()
  } catch (e) {
    error.value = "Не удалось загрузить аналитику"
    loading.value = false
  }
})

watch(isDark, async () => {
  await nextTick()
  initCharts()
})

onUnmounted(() => {
  timelineChart?.destroy()
  workloadChart?.destroy()
})

function formatDate(d) {
  const date = new Date(d.endsWith("Z") ? d : d + "Z")
  return date.toLocaleString("ru-RU", {
    day: "2-digit", month: "2-digit", year: "2-digit",
    hour: "2-digit", minute: "2-digit",
  })
}
</script>
