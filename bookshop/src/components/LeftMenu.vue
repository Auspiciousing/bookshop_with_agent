<script setup>
  import { useCounterStore } from "@/stores/counter";

  const mainStore = useCounterStore();


  // 👇 自己管理 openeds
  function handleOpen(index) {
    console.log(index);
    if(index==='4')
      mainStore.openeds=['4'];
  }

  function handleClose(index) {
    mainStore.openeds=[''];

  }


</script>

<template>
    <el-col class="custom-width-col">
        <img  src="@/assets/general/logo.png" style="text-align: center;width: 200px" alt=""/>
        <h5 style="text-align: center;font-size: larger;color: white">&nbsp;校园二手书售卖平台</h5>
  <!--    <h5 class="mb-2">这里放logo</h5>-->
  <!--    <h5></h5>-->

      <el-menu
          background-color="green"
          class="custom-menu"
          default-active="1"
          text-color="#fff"
          @open="handleOpen"
          @close="handleClose"
          :default-openeds="mainStore.openeds"

      >
        <router-link to="/home">
          <el-menu-item index="1">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
        </router-link>
        <router-link to="/shop">
          <el-menu-item index="2">
            <el-icon><img src="@/assets/images/商城.svg" style="height: 20px;filter: brightness(0) invert(1);" alt=""></el-icon>
            <span>商城</span>
          </el-menu-item>
        </router-link>
        <router-link to="/shoppingcar">
          <el-menu-item index="3">
            <el-icon><img src="@/assets/images/购物车.svg" style="height: 20px;filter: brightness(0) invert(1);" alt=""></el-icon>
            <span>购物车</span>
          </el-menu-item>
        </router-link>
        <router-link to="/order/payment" :key="31">
          <el-menu-item index="4">
            <el-icon><MessageBox /></el-icon>
            <span>全部订单</span>
          </el-menu-item>
        </router-link>
        <el-sub-menu index="4" style="color:white;"  >
          <template #title>
            <el-icon><document /></el-icon>
            <span >我的购买</span>
          </template>
          <router-link to="/order/delivering" :key="32"><el-menu-item index="5-1">待收货</el-menu-item></router-link>
          <router-link to="/order/delivered" :key="33"><el-menu-item index="5-2">已收货</el-menu-item></router-link>
        </el-sub-menu>
        <router-link to="/sell">
          <el-menu-item index="6">
            <el-icon><Edit /></el-icon>
            <span>我的出售</span>
          </el-menu-item>
        </router-link>
      </el-menu>

    </el-col>
</template>

<style scoped>
  .custom-width-col {
    width: 200px;
    /* 移除 flex 布局影响，确保自定义宽度生效 */
    flex: none;
    background-color: green;
    height: 100vh;
  }

  .custom-menu {
    background-color: green;
  }

  .el-menu .el-menu-item {
    color: #fff;
  }

  .el-menu .el-sub-menu .el-menu-item {
    color: #fff;
  }

  a{
    text-decoration: none;
  }
  .router-link-active {
    text-decoration: none;
  }


</style>
