<template>
  <span class="status-badge" :class="`status-${status}`">{{ labels[status] }}</span>
</template>

<script setup>
defineProps({ status: String })

const labels = { todo: "To Do", in_progress: "In Progress", done: "Done" }
</script>
