<script setup>

import TopMenu from "@/components/TopMenu.vue";
import LeftMenu from "@/components/LeftMenu.vue";
import { ref,onMounted, onUnmounted } from 'vue';
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
        <el-main class="mainclass" style="height: 100%; padding: 0; overflow: hidden;">
          <el-carousel
              style="height: 100%; width: 100%;"
              motion-blur
              arrow="never"
              interval="2000"
          >
            <el-carousel-item
                style="height: 875px; width: 100%;margin: 0; display: flex; align-items: center; justify-content: center;"
            >
              <img src="@/assets/general/1.jpg" alt="Image 1" style="width: 100%; height: 100%; object-fit: fill;">
            </el-carousel-item>
            <el-carousel-item
                style="height: 875px; width: 100%;margin: 0; display: flex; align-items: center; justify-content: center;"
            >
              <img src="@/assets/general/2.jpg" alt="Image 1" style="width: 100%; height: 100%; object-fit: fill;">
            </el-carousel-item>
            <el-carousel-item
                style="height: 875px; width: 100%;margin: 0; display: flex; align-items: center; justify-content: center;"
            >
              <img src="@/assets/general/3.jpg" alt="Image 1" style="width: 100%; height: 100%; object-fit: fill;">
            </el-carousel-item>
            <el-carousel-item
                style="height: 875px; width: 100%;margin: 0; display: flex; align-items: center; justify-content: center;"
            >
              <img src="@/assets/general/4.jpg" alt="Image 1" style="width: 100%; height: 100%; object-fit: fill;">
            </el-carousel-item>
          </el-carousel>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
.demonstration {
  color: var(--el-text-color-secondary);
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
.app-container::-webkit-scrollbar {
  display: none; /* Chrome, Safari 和 Opera */
}
.common-layout {
  height: 100vh;
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
}
</style>
