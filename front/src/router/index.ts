import { createRouter, createWebHashHistory } from 'vue-router'
import ResultTable from '@/components/result-table/ResultTable.vue'

const router = createRouter({
  history: createWebHashHistory(), // XXX: important lorsque l'on sert depuis le back python
  routes: [
    {
      path: '/',
      name: 'home',
      redirect: '/result-backend',
    },
    {
      path: '/result-backend',
      component: ResultTable,
    },
  ]
})

export default router
