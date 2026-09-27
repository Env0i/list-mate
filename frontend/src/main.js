import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'
import { initTheme } from './utils/theme'

// 挂载前应用主题，避免暗色用户首帧闪白
initTheme()

const app = createApp(App)
app.use(router)
app.mount('#app')
