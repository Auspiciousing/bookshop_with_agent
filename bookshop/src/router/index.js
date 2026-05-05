import {createRouter, createWebHashHistory, createWebHistory} from 'vue-router'
import Null from "@/components/null.vue";


const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path:"/",
      name:"null",
      redirect:"/login",
    },
    {
      path:"/login",
      name:"login",
      component:() => import('@/views/LoginView.vue')
    },
    {
      path:"/register",
      name:"register",
      component:() => import('@/views/RegisterView.vue')
    },
    {
      path:"/home",
      name:"home",
      component:() => import('@/views/HomeView.vue')
    },
    {
      path:"/shop",
      name:"shop",
      component:() => import('@/views/ShopView.vue')
    },
    {
      path:"/shoppingcar",
      name:"shoppingcar",
      component:() => import('@/views/ShoppingCarView.vue')
    },
    {
      path:"/self",
      name:"self",
      component:() => import('@/views/MyView.vue')
    },
    {
      path:"/account",
      name:"account",
      component:() => import('@/views/AccountView.vue')
    },
    {
      path:"/order",
      name:"order",
      children:[
        {
          path:""
        },
        {
          path:"payment",
          name:"payment",
          component:() => import('@/views/PaymentView.vue')
        },
        {
          path:"delivering",
          name:"delivering",
          component:() => import('@/views/DeliveringView.vue')
        },
        {
          path:"delivered",
          name:"delivered",
          component:() => import('@/views/DeliveredView.vue')
        },
      ]
    },
    {
      path:"/sell",
      name:"sell",
      component:() => import('@/views/SellingView.vue')
    }
  ],
})

export default router
