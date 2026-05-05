<script setup>

import TopMenu from "@/components/TopMenu.vue";
import LeftMenu from "@/components/LeftMenu.vue";
import {onMounted, onUnmounted} from "vue";
import Part from "@/components/BuyPart.vue";

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

<template>
  <div class="common-layout">
    <el-container>
      <el-aside width="200px"><LeftMenu/></el-aside>
      <el-container>
        <el-header style="border-bottom: 1px solid"><TopMenu/></el-header>
        <el-main class="mainclass">
          <Part category="delivered"/>
        </el-main>

      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
.common-layout {
  height: 100vh;
}
.mainclass{
  background-image : url('@/assets/images/bodybg.jpg');
  background-size: cover;
  background-position: center;
}
</style>
