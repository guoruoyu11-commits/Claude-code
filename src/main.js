import { ViteSSG } from 'vite-ssg'
import App from './App.vue'
import { routes } from './router/index.js'
import { MACHINES } from './data/machines.js'
import '@fontsource/rajdhani/600.css'
import '@fontsource/rajdhani/700.css'
import './styles/global.css'

export const createApp = ViteSSG(
  App,
  { routes, scrollBehavior: () => ({ top: 0 }) },
)

export function includedRoutes(paths) {
  return paths.flatMap(path =>
    path === '/machine/:id'
      ? MACHINES.map(m => `/machine/${m.id}`)
      : [path]
  )
}
