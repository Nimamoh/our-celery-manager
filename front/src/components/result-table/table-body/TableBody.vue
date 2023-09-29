<script setup lang="ts">

import TracebackVue from '@/components/result-table/traceback/Traceback.vue'
import CloneColumnVue from '@/components/result-table/clones-column/CloneColumn.vue'

const props = defineProps(['col', 'data'])

const format_date = (date: string) => {
    return new Date(date).toLocaleString()
}

</script>

<template>
    <!-- COLONNE CACHEE -->
    <template v-if="col.hidden">
        <template v-if="data[col.field]"> — </template>
        <template v-else="data[col.field]"> ø </template>
    </template>
    <!-- STATUS -->
    <template v-else-if="col.field == 'status'">
        <template v-if="data[col.field] == 'SUCCESS'">
            <span class="green">
                {{ data[col.field] }}
            </span>
        </template>

        <template v-else-if="data[col.field] == 'FAILURE'">
            <span class="red">
                {{ data[col.field] }}
            </span>
        </template>

        <template v-else>
            {{ data[col.field] }}
        </template>
    </template>

    <!-- DATE -->
    <template v-else-if="col.field == 'date_done'">
        {{ format_date(data[col.field]) }}
    </template>

    <!-- TRACEBACK -->

    <template v-else-if="col.field == 'traceback' || col.field == 'result'">
        <TracebackVue :traceback="data[col.field]" />
    </template>

    <template v-else-if="col.field == 'clones'">
        <CloneColumnVue :clones="data[col.field]" />
    </template>

    <!-- OTHERS -->
    <template v-else>
        {{ data[col.field] }}
    </template>
</template>