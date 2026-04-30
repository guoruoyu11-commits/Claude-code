import HomePage from '../pages/HomePage.vue'
import MachineDetailPage from '../pages/MachineDetailPage.vue'

export const routes = [
  { path: '/', component: HomePage },
  { path: '/machine/:id', component: MachineDetailPage },
]
