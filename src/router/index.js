import HomePage from '../pages/HomePage.vue'
import MachineDetailPage from '../pages/MachineDetailPage.vue'
import SupportPage from '../pages/SupportPage.vue'

export const routes = [
  { path: '/', component: HomePage },
  { path: '/machine/:id', component: MachineDetailPage },
  { path: '/support', component: SupportPage },
]
