<script setup>

import TopMenu from "@/components/TopMenu.vue";
import LeftMenu from "@/components/LeftMenu.vue";
import { ref,onMounted, onUnmounted } from 'vue';
import Table from "@/components/Table.vue";
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

<template>
  <div class="common-layout">
    <el-container>
      <el-aside width="200px"><LeftMenu/></el-aside>
      <el-container>
        <el-header style="border-bottom: 1px solid"><TopMenu/></el-header>
        <el-main class="mainclass">

          <Table/>

        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
.app-container::-webkit-scrollbar {
  display: none; /* Chrome, Safari 和 Opera */
}
.common-layout {
  height: 100vh;
}
.el-carousel__item h3 {
  color: #475669;
  opacity: 0.75;
  line-height: 200px;
  margin: 0;
  text-align: center;
}

.el-carousel__item:nth-child(2n) {
  background-color: #99a9bf;
}

.el-carousel__item:nth-child(2n + 1) {
  background-color: #d3dce6;
}

.mainclass{
  background-image : url('@/assets/images/bodybg.jpg');
  background-size: cover;
  background-position: center;
  overflow: hidden;
}
</style>
