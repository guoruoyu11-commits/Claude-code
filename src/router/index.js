import HomePage from '../pages/HomePage.vue'
import MachineDetailPage from '../pages/MachineDetailPage.vue'
import FeedbackPage from '../pages/FeedbackPage.vue'

export const routes = [
  { path: '/', component: HomePage },
  { path: '/machine/:id', component: MachineDetailPage },
  { path: '/feedback', component: FeedbackPage },
]
