<script setup lang="ts">

import { inject, reactive, ref, type Ref } from 'vue';

import type {
    DefaultApi,
    TaskResultPageResultsPageGetRequest as PageGetRequest,
    ListResultRow,
} from '@/generated/api';

import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import DataTable, { type DataTableSortMeta } from 'primevue/datatable';
import InputText from 'primevue/inputtext';
import Column from 'primevue/column';
import Button from 'primevue/button';

import TableHeaderVue from '@/components/result-table/table-header/TableHeader.vue'
import TableBodyVue from '@/components/result-table/table-body/TableBody.vue'

const toast = useToast();
const confirm = useConfirm();

const makeMetaRows = (except: string[] = []) => {
    let rows = [
        { field: 'task_id', header: 'Task ID', hidden: false, sortable: true },
        { field: 'name', header: 'Name', hidden: false, sortable: true, disableHideable: true },
        { field: 'args', header: 'args', sortable: true, hidden: true },
        { field: 'kwargs', header: 'kwargs', sortable: true, hidden: true },
        { field: 'date_done', header: 'Ended in', sortable: true, hidden: false },
        { field: 'traceback', header: 'Traceback', sortable: true, hidden: false, disableHideable: true },
        { field: 'result', header: 'Result', sortable: true, hidden: true },
        { field: 'status', header: 'Status', sortable: true, hidden: false },
        { field: 'clones', header: 'Number of clones', hidden: false, disableHideable: true },
    ]

    rows = rows.filter(row => !except.includes(row.field))

    return reactive(rows)
}

const filters = ref({
    'task_id': '',
    'name': '',
    // 'args': '',
    // 'kwargs': '',
    // 'date_done': '',
    'traceback': '',
    // 'result': '',
    'status': '',
});

/* Objets et callback pour les requêtes */
const page_get_request: Ref<PageGetRequest> = ref({ n: 0, size: 10 })

const replayable = (task: ListResultRow) => {
    return task.name != null;
}
const currently_cloning_and_sending = ref(false);

const onCloneAndSend = async (task: ListResultRow) => {
    confirm.require({
        message: `Do you really want to replay task ${task.task_id} ?`,
        accept: () => _cloneAndReplay(task),
        reject: () => { },
    })
}
const _cloneAndReplay = async (task: ListResultRow) => {

    currently_cloning_and_sending.value = true;
    try {
        await api.cloneAndSendCloneAndSendIdPost({ id: task.task_id })
        toast.add({
            severity: 'success',
            summary: 'Task replayed',
            detail: `Task ${task.task_id} replayed`,
            life: 10000
        })
        await load();
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Erreur',
            detail: `Impossible to replay task ${task.task_id}`,
            life: 10000
        })
    } finally {
        currently_cloning_and_sending.value = false;
    }
}

//@ts-ignore
const onPage = async (event) => {
    console.log(event)

    const n = event.page;

    page_get_request.value = {
        ...page_get_request.value,
        n
    }

    await load();
}

//@ts-ignore
const onSort = async (event) => {
    console.log(event)

    //@ts-ignore
    const sort = event.multiSortMeta.map((sort) => { return `${sort.field} ${sort.order > 0 ? 'DESC' : 'ASC'}` })
    page_get_request.value = {
        ...page_get_request.value,
        sort,
    }

    await load();
}

//@ts-ignore
const onFilter = async (event) => {
    console.log(event)

    let search = []
    for (const key in event.filters) {
        const v = event.filters[key].value
        if (!v) continue;

        search.push(`${key}:${v}`)
    }

    //@ts-ignore
    page_get_request.value = {
        ...page_get_request.value,
        search,
    }

    await load();
}

//@ts-ignore
const onRowExpand = async (event) => {
    const task: ListResultRow = event.data;
    expandedRows.value = [task];
}

/* Objets de résultats */
const loading_results = ref(false);
const totalRecords = ref(0);
let rows: Ref<ListResultRow[]> = ref([]);
let expandedRows: Ref<ListResultRow[]> = ref([]);

const api: DefaultApi = inject('api')!

async function load() {

    loading_results.value = true;
    const req = page_get_request.value

    const page = await api.taskResultPageResultsPageGet(req)

    rows.value = page.data;
    totalRecords.value = page.total;

    loading_results.value = false;
    console.log(page)
}

const multiSortMeta: DataTableSortMeta[] = [{ 'field': 'date_done', 'order': 1 }]
await onSort({ multiSortMeta }) // XXX: we initially sort on date_done
</script>

<template>
    <div class="card flex flex-wrap justify-content-center w-100">
        <DataTable showGridlines stripedRows :value="rows" v-model:expanded-rows="expandedRows"
            lazy paginator :rows="page_get_request.size"
            v-model:filters="filters" :totalRecords="totalRecords" :loading="loading_results" @page="onPage($event)"
            @sort="onSort($event)" @filter="onFilter($event)" filterDisplay="row"
            @row-expand="onRowExpand"
            :globalFilterFields="['task_id', 'name', 'args', 'kwargs', 'date_done', 'traceback', 'result', 'status']"
            :multi-sort-meta="multiSortMeta" sortMode="multiple" removableSort>
            <template #header>
                <div class="flex flex-wrap align-items-center justify-content-between gap-2">
                    <span>Total: {{ totalRecords }} tasks</span>
                    <Button @click="load()" icon="pi pi-refresh" rounded raised />
                </div>
            </template>

            <Column expander style="width: 2rem" />

            <Column v-for="col of makeMetaRows()" :field="col.field" :header="col.header" :showFilterMenu="false"
                filterMatchMode="contains" :sortable="col.sortable">

                <template #header>
                    <TableHeaderVue :col="col"></TableHeaderVue>
                </template>

                <template #filter="{ filterModel, filterCallback }">
                    <InputText v-if="filterModel" type="text" v-model="filterModel.value" @keydown.enter="filterCallback()"
                        class="p-column-filter" placeholder="Search" />
                </template>

                <template #body="{ data }">
                    <TableBodyVue :col="col" :data="data"></TableBodyVue>
                </template>

            </Column>

            <Column>
                <template #body="{ data }">
                    <Button v-bind:disabled="!replayable(data) || currently_cloning_and_sending"
                        @click="onCloneAndSend(data)">
                        Clone and send
                    </Button>
                </template>
            </Column>

            <template #expansion="task">
                <div class="p-3">

                    <h5>Clones</h5>

                    <DataTable :value="task.data.clones">
                        <Column v-for="col of makeMetaRows(['args', 'kwargs', 'name', 'clones'])" :field="col.field" :header="col.header">

                            <template #header>
                                <TableHeaderVue :col="col"></TableHeaderVue>
                            </template>

                            <template #body="{ data }">
                                <TableBodyVue :col="col" :data="data"></TableBodyVue>
                            </template>
                        </Column>
                    </DataTable>

                </div>
            </template>

        </DataTable>
    </div>
</template>