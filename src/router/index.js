import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import MachineDetailPage from '../pages/MachineDetailPage.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomePage },
    { path: '/machine/:id', component: MachineDetailPage },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
