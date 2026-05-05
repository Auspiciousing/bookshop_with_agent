<template>
  <div class="common-layout">
    <el-container>
      <el-aside width="200px"><LeftMenu/></el-aside>
      <el-container>
        <el-header style="border-bottom: 1px solid"><TopMenu type="shop"/></el-header>
        <el-main class="mainclass"><GoodsShow /></el-main>

      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

import TopMenu from "@/components/TopMenu.vue";
import LeftMenu from "@/components/LeftMenu.vue";
import GoodsShow from "@/components/GoodsShow.vue";

// 禁止页面滚动
const preventBodyScroll = () => {
  document.body.style.overflow = 'hidden';
};

// 恢复页面滚动
const restoreBodyScroll = () => {
  document.body.style.overflow = 'auto';
};

onMounted(() => {
  preventBodyScroll();
});

onUnmounted(() => {
  restoreBodyScroll();
});
</script>

<style scoped>

.common-layout {
  height: 100vh;
}

.mainclass{
  background-image : url('@/assets/images/bodybg.jpg');
  background-size: cover;
  background-position: center;
  overflow: hidden;
}
</style>
