import { ref, watch } from "vue"

const isDark = ref(localStorage.getItem("theme") !== "light")

function applyTheme(dark) {
  document.documentElement.setAttribute("data-theme", dark ? "dark" : "light")
  localStorage.setItem("theme", dark ? "dark" : "light")
}

applyTheme(isDark.value)

watch(isDark, applyTheme)

export function useTheme() {
  return {
    isDark,
    toggleTheme: () => { isDark.value = !isDark.value },
  }
}
