<script setup lang="ts">

const props = defineProps(['clones'])

</script>

<template>

<div v-if="clones.length == 0">
ø
</div>
<div v-else>
    {{ clones.length }}
</div>

</template>