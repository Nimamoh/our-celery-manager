<script setup lang="ts">


import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { useToast } from 'primevue/usetoast';
import { ref } from 'vue';

const toast = useToast()

const props = defineProps(['traceback'])

const visible = ref(false)
const openDialogForTraceback = () => {
    visible.value = true
}
const closeDialog = () => {
    visible.value = false
}

const copyTracebackOnClipBoard = () => {
    navigator.clipboard.writeText(props.traceback)
    toast.add({
        severity: 'success',
        summary: 'Successfully copied',
        detail: `Traceback successfully copied to clipboard.`,
        life: 5000
    });
    closeDialog()
}


</script>

<template>

<div v-if="traceback">
    <Button icon="pi pi-eye" @click="openDialogForTraceback()" severity="info" text></Button>
    <Button icon="pi pi-copy" @click="copyTracebackOnClipBoard()" severity="info" text></Button>
</div>
<div v-else>
    <Button icon="pi pi-eye-slash" disabled severity="info" text></Button>
    <Button icon="pi pi-copy" disabled severity="info" text></Button>
</div>

<Dialog v-model:visible="visible" modal>
    <pre>
        {{ traceback }}
    </pre>

    <br>

    <Button @click="copyTracebackOnClipBoard()" icon="pi pi-copy" severity="secondary"></Button>
</Dialog>

</template>