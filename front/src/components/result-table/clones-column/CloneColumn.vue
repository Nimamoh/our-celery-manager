<script setup lang="ts">

import { type ListResultRow } from '@/generated/api/models';

const props = defineProps(['clones'])

const suffix = (clones: ListResultRow[]) => {
    const successed = clones.filter(clone => clone.status == 'SUCCESS')
    return `(with ${successed.length} succeeded)`
}

</script>

<template>

<div v-if="clones.length == 0">
ø
</div>
<div v-else>
    {{ `${clones.length} ${suffix(clones)}` }}
</div>

</template>