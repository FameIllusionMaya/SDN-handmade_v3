import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Home from '../views/Home.vue'
// import Test from '../views/Test.vue'
import Devices from '../views/Devices.vue'
import Initialization from '../views/Initialization.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/device',
    name: 'Device',
    component: Devices
  },
  {
    path: '/init',
    name: 'Initialization',
    component: Initialization
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
