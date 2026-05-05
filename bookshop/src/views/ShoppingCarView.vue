<script setup>

import TopMenu from "@/components/TopMenu.vue";
import LeftMenu from "@/components/LeftMenu.vue";
import Part from "@/components/CarPart.vue";
import {onMounted, onUnmounted,ref} from "vue";
import {ElBacktop} from "element-plus";
import { useCounterStore } from '@/stores/counter';

// 获取 Pinia store
const productsStore = useCounterStore();

onMounted(() => {
  // 你可以在这里处理初始化逻辑，例如从 API 加载商品数据等
  console.log(productsStore.carproducts);
});

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
        <el-header style="border-bottom: 1px solid;display: flex;padding: 0"><TopMenu /></el-header>
        <el-main class="mainclass">
          <Part/>

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
