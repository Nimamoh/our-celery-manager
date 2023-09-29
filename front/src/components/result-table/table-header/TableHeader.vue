<script setup lang="ts">
    import Button from 'primevue/button';

    const props = defineProps(['col'])

    /* */
    // @ts-ignore
    const onDisplay = (column) => { column.hidden = false; }
    // @ts-ignore
    const onHide = (column) => { column.hidden = true; }
    /* */
</script>

<template>
    <span class="p-column-title" v-if="!col.disableHideable">
        <Button v-if="col.hidden" @click="onDisplay(col)" icon="pi pi-eye" rounded text size="large"></Button>
        <Button v-else @click="onHide(col)" icon="pi pi-eye-slash" rounded text size="large"></Button>
    </span>
</template>