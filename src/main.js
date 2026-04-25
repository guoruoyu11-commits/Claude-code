import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.js'
import '@fontsource/rajdhani/600.css'
import '@fontsource/rajdhani/700.css'
import './styles/global.css'

createApp(App).use(router).mount('#app')
