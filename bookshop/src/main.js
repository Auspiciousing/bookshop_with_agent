// import './assets/main.css'

import { createApp } from 'vue'
// import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import * as ElementPlusIconsVue from '@element-plus/icons-vue';
import {createPinia} from 'pinia'
import VueCropper from 'vue-cropper';
import 'vue-cropper/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import api from "@/api/index.js"
import ElementPlus from 'element-plus'

const pinia = createPinia()
import axios from "axios"
const app = createApp(App)


app.config.globalProperties.$axios = axios

if (process.env.NODE_ENV === 'production') {
    // 在生产环境中禁用 Vue DevTools
    app.config.devtools = false
}
// app.use(createPinia())
app.use(router)
app.use(pinia)
app.use(ElementPlus, {
    locale: zhCn,
})
app.use(VueCropper)
// 在 createApp 之后，mount 之前添加
app.config.devtools = false
// app.config.globalProperties.$axios = axios
// 全局注册 ElementPlus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component);
}

app.mount('#app')
