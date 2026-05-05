<template>
  <!-- 给商品展示容器添加 ref -->
  <el-main>
    <div
        class="product-display"
        ref="productDisplay"
        v-infinite-scroll="loadMore"
        :infinite-scroll-distance="10"
        :infinite-scroll-delay="100"
    >
      <el-row :gutter="gutter" justify="start">
        <el-backtop :bottom="100" :right="100" :visibility-height="1" target=".product-display" style="position: fixed">
          <div class="a"><el-icon :size="30" style="color:green;"><ArrowUpBold /></el-icon></div>
        </el-backtop>
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="(product, index) in visibleProducts" :key="index">
          <el-card class="product-card" shadow="hover">
            <template #header>
              <div class="product-title">
                <!-- 标题骨架屏 -->
                <el-skeleton v-if="!product.loaded" :rows="1" animated />
                <span v-else><strong>{{ product.title }}</strong></span>
              </div>
            </template>
            <div class="product-image-container">
              <!-- 图片骨架屏 -->
              <el-skeleton v-if="!product.loaded" :rows="0" animated>
                <template #template>
                  <el-skeleton-item variant="image" style="width: 100%; height: 200px;" />
                </template>
              </el-skeleton>
              <div v-if="product.loaded && hasPicture(product)" class="product-image-wrapper">
                <img 
                    :src="product.picture_url"
                    alt="Product Image"
                    class="product-image"
                    @load="onImageLoad($event, product)"
                    @error="onImageError(product)"
                    :key="product.imageKey || product.id"
                />
              </div>
              <div v-else-if="product.loaded" class="product-image-placeholder">
                <span>暂无图片</span>
              </div>
            </div>
            <div class="product-price">
              <!-- 价格骨架屏 -->
              <el-skeleton v-if="!product.loaded" :rows="2" animated />
              <div v-else>
                <span>价格: ${{ product.price }}&nbsp;库存:{{product.stock}}</span>
                <br>
                <div class="button-group">
                  <el-button style="margin-top: 10px" type="primary" plain @click="addToCart(product)">加入购物车</el-button>
                  <!-- 新增详情按钮 -->
                  <el-button style="margin-top: 10px" type="info" plain @click="showProductDetail(product)">查看详情</el-button>
                </div>
              </div>
            </div>
          </el-card>

        </el-col>


      </el-row>

<!--      <div  v-if="hasLoadedAll===true"  style="height: 150px;display: flex;align-items: center;justify-items: center;margin: auto;font-size: 30px;font-family:'KaiTi'">-->
<!--        <p>-&#45;&#45;&#45;&#45;&nbsp;已&nbsp;经&nbsp;到&nbsp;底&nbsp;啦&nbsp;！-&#45;&#45;&#45;&#45; 总数：{{visibleProducts.length}}</p>-->
<!--      </div>-->
    </div>

  </el-main>

  <!-- 商品详情对话框 -->
  <el-dialog
      v-model="detailDialogVisible"
      :title="selectedProduct?.name || '商品详情'"
      width="50%"
      center
  >
    <div class="product-detail" v-if="selectedProduct">
      <div class="product-detail-image">
        <img
            v-if="hasPicture(selectedProduct)"
            :src="selectedProduct.picture_url"
            alt="商品图片"
            class="detail-image"
        />
        <div v-else class="detail-image-placeholder">
          <span>暂无图片</span>
        </div>
      </div>
      <div class="product-detail-info">
        <h2>{{ selectedProduct.name }}</h2>
        <el-divider />
        <p><strong>名称:</strong> {{selectedProduct.title}}</p>
        <p><strong>价格:</strong> ${{ selectedProduct.price }}</p>
        <p><strong>库存:</strong> {{ selectedProduct.stock || '暂无库存信息' }}</p>
        <p><strong>作者:</strong> {{selectedProduct.author}}</p>
        <p><strong>出版社:</strong> {{selectedProduct.publisher}}</p>
        <p><strong>商品描述:</strong> {{ selectedProduct.description || '暂无商品描述' }}</p>
        <p><strong>卖家:</strong> {{selectedProduct.seller_username}}</p>
      </div>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="addToCart(selectedProduct)">加入购物车</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, onUnmounted,computed } from 'vue';
import { ElBacktop, ElMessage } from "element-plus";
import { useCounterStore } from '@/stores/counter';
import { ArrowUpBold } from '@element-plus/icons-vue';
import api from "@/api/index.js";
import 'element-plus/dist/index.css'

const gutter = computed(() => {
  if (visibleProducts.value.length === 2)
    return 400
  else if (visibleProducts.value.length === 3)
    return 180
  else return 20
});

// 商品详情相关
const detailDialogVisible = ref(false);
const selectedProduct = ref(null);

const hasPicture = (product) => {
  const pictureUrl = product?.picture_url;
  return typeof pictureUrl === 'string' && pictureUrl.trim().length > 0 && !product?.usePlaceholder;
};

const normalizeProducts = (products = []) => {
  return products.map((product, index) => {
    const pictureUrl = typeof product.picture_url === 'string' ? product.picture_url.trim() : '';
    const hasImage = pictureUrl.length > 0;

    return {
      ...product,
      picture_url: pictureUrl,
      loaded: !hasImage,
      usePlaceholder: !hasImage,
      imageKey: `${Date.now()}-${index}`,
    };
  });
};

// 显示商品详情
const showProductDetail = (product) => {
  selectedProduct.value = product;
  detailDialogVisible.value = true;
};

// 加入购物车
const addToCart = (product) => {
  if (!product) return;
  api.postBookAddToCar(product.id,1).then(res => {
    if (res.data.code === 200) {
      ElMessage.success(`已将 ${product.title} 添加到购物车`);
    } else {
      ElMessage.error(res.data.message);
    }
  }).catch(error => {
    console.error('加入购物车失败:', error);
    ElMessage.error('网络问题，加入购物车失败');
  });

};

// 图片加载成功处理函数
const onImageLoad = (event, product) => {
  product.loaded = true;
  product.usePlaceholder = false;

};

// 图片加载失败处理函数
const onImageError = (product) => {
  console.error(`图片加载失败: ${product.picture_url}`);
  product.loaded = true;
  product.usePlaceholder = true;
};

onMounted(() => {
  window.addEventListener('refresh-table', handleRefresh);
  api.getBookShop().then(res => {
    if (res.data.code === 200) {
      console.log("前",visibleProducts.value)
      visibleProducts.value = normalizeProducts(res.data.data);
      console.log("后",visibleProducts.value)
      loadedCount.value = res.data.append_length;
      if(loadedCount.value<8)
        hasLoadedAll.value=true;
      ElMessage.success('获取商品列表成功');
      first.value = false;
    }else {
      ElMessage.error('获取商品列表失败');
    }
  }).catch(error => {
    console.error('获取商品列表失败:', error);
    ElMessage.error('网络问题，获取商品列表失败');
  });
});

onUnmounted(() => {
  // 移除事件监听器，避免内存泄漏
  window.removeEventListener('refresh-table', handleRefresh);
});

const handleRefresh = () => {
  loadTableData(); // 重新加载表格数据的函数
};

// 封装加载数据的函数
const loadTableData = () => {
  api.getBookShop().then(res => {

    if (res.data.code === 200) {
      console.log("------------------开始搜索----------------------")
      loading.value = false;
      hasLoadedAll.value = false;
      first.value = true
      productDisplay.value = null;
      console.log("前",visibleProducts.value)
      visibleProducts.value = normalizeProducts(res.data.data);
      console.log("后",visibleProducts.value)

      loadedCount.value = res.data.append_length;
      if(loadedCount.value<8)
        hasLoadedAll.value=true;
      console.log(loadedCount.value)
      ElMessage.success('获取商品列表成功');
      first.value = false;
    }else {
      ElMessage.error('获取商品列表失败');
    }
  }).catch(error => {
    console.error('获取商品列表失败:', error);
    ElMessage.error('网络问题，获取商品列表失败');
  });
};

// 滚动加载
const productDisplay = ref(null);
const loading = ref(false);
const hasLoadedAll = ref(false);
const initialItemsPerPage = 8;
const nextItemsPerPage = ref(0);
const loadedCount = ref(initialItemsPerPage);
const first = ref(true);

// 计算当前可见的商品列表
const visibleProducts = ref([])

const loadMore = () => {
  if (loading.value || hasLoadedAll.value || first.value){
    ElMessage.warning("已经到底了")
    return;
  }
  loading.value = true;

  // 只对新添加的商品进行图片加载检查
  api.getBookShopAppend().then(res => {

    if (res.data.code === 200) {
      console.log("收到",res.data.data)
      console.log("收到",res.data.data)
      console.log("长度",res.data.data.length)
      nextItemsPerPage.value=res.data.append_length;
      console.log("新增数量",nextItemsPerPage.value)
      console.log("前",visibleProducts.value)
      if (nextItemsPerPage.value>1)
        visibleProducts.value.push(...normalizeProducts(res.data.data))
      else
        visibleProducts.value.push(normalizeProducts([res.data.data[0]])[0])
      console.log("后",visibleProducts.value)

      console.log("多的数目",nextItemsPerPage.value)
      const totalProducts = visibleProducts.value.length;
      const nextCount = loadedCount.value + nextItemsPerPage.value;
      console.log("next",nextCount)
      hasLoadedAll.value = res.data.end

      if (hasLoadedAll.value) {
        console.log("total",totalProducts)
        loadedCount.value = nextCount;
      } else {
        loadedCount.value = nextCount;
      }
      console.log(loadedCount.value)
      loading.value = false;
    }else {
      ElMessage.error('获取商品列表失败');
    }
  }).catch(error => {
    console.error('获取商品列表失败:', error);
    ElMessage.error('网络问题，获取商品列表失败');
  });



};
</script>

<style scoped>
.a {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background-color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 5px 10px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  opacity: 0.8;
}

.product-display {
  display: flex;
  flex-wrap: wrap;
  width: 99%;
  overflow-x: clip;
  overflow-y: scroll;
  max-height: 800px;
  padding-right: 10px;
}

.product-card {
  width: 300px;
  margin-bottom: 20px;
  margin-left: 20px;
}

.product-title {
  margin-bottom: 10px;
}

.product-image-container {
  margin-bottom: 15px;
}

.product-image-wrapper,
.product-image-placeholder,
.detail-image-placeholder {
  width: 100%;
  height: 200px;
  border-radius: 8px;
  overflow: hidden;
}

.product-image-placeholder,
.detail-image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #d9d9d9 0%, #efefef 100%);
  color: #8c8c8c;
  font-size: 14px;
}

.detail-image-placeholder {
  height: 400px;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.product-price {
  margin-bottom: 15px;
}

/* 按钮组的样式 */
.button-group {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
}

.button-group .el-button {
  margin-left: 0;
}

/* 商品详情对话框样式 */
.product-detail {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.product-detail-image {
  flex: 1;
  min-width: 200px;
  text-align: center;
}

.detail-image {
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
}

.product-detail-info {
  flex: 1;
  min-width: 300px;
}

.product-detail-info h2 {
  margin-top: 0;
  color: #303133;
}

.product-detail-info p {
  margin: 10px 0;
  font-size: 14px;
  line-height: 1.5;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .product-detail {
    flex-direction: column;
  }

  .button-group .el-button {
    flex-basis: 100%;
    margin-top: 5px;
  }
}

@media (min-width: 1200px) {
  .product-card {
    width: 300px !important;
    margin-left: auto;
    margin-right: auto;
  }
}

/* 确保骨架屏与卡片内容宽度一致 */
.el-skeleton {
  width: 100%;
}

/* 调整骨架屏图片区域的高宽比 */
.el-skeleton-item.el-skeleton-item--image {
  width: 100%;
  aspect-ratio: 1/1; /* 根据实际图片比例调整 */
}
</style>
