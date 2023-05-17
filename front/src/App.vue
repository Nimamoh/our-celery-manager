<script setup lang="ts">
import { inject, ref, type Ref, Suspense } from 'vue';
import TabMenu from 'primevue/tabmenu';
import Toast from 'primevue/toast';
import ConfirmDialog from 'primevue/confirmdialog';
import type { Settings } from './models/settings.model';

const items = ref([
  {
    label: "Result backend",
    icon: "pi pi-fw pi-home",
    to: '/result-backend',
  }
])

const info = inject('info') as Ref<Settings | null>

</script>

<template>
    <div class="card">

      <Toast />
      <ConfirmDialog />

      <h1>{{ info?.application_name }}</h1>

      <h2>{{ info?.broker }}</h2>
      <h2>{{ info?.backend }}</h2>

      <TabMenu :model="items" />

      <Suspense>
        <RouterView />
        <template #fallback>
          <div class="card">
            <h1>Loading...</h1>
          </div>
        </template>
      </Suspense>
    </div>

</template>
