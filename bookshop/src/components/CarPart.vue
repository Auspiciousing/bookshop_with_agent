<template>
  <div class="product-display" @change="">

    <el-empty v-if="books.length===0" style="height: 100vh;" description="购物车为空" />

    <p v-for="(product, index) in books" :key="product.id" type="flex" justify="center" align="middle" class="productitem">
      <el-checkbox :value="product.id"
                   label=" "
                   size="large"
                   style="display: flex;justify-content: center;align-items: center"
                   v-model="product.checked"
                   @change="handleItemChecked"/>
      <el-card v-if="!product.loaded" class="cardclass" shadow="hover">

        <el-skeleton :rows="5" animated style="--el-skeleton-circle-size: 100px;">
          <template #template>
            <el-skeleton-item variant="text" style="width: 30%;margin-left: auto"/>
            <br>&nbsp;
            <div style="display: flex;flex-direction: column;">
              <el-skeleton-item variant="image" style="width: 200px; height: 200px;"/>
              <img :src="product.picture_url"
                   @load="onImageLoad($event, product)"
                   @error="onImageError(product)"
                   alt="" style="display: none"/>
              <el-skeleton-item variant="text" style="width: 40%;margin-top: 20px"/>
            </div>
          </template>
        </el-skeleton>
      </el-card>
      <el-card v-else class="cardclass" shadow="hover">
        <template #header><strong>{{product.title}}</strong></template>
        <div class="card-content">
          <div style="width: 200px;">
            <img :src="product.picture_url"
                 @load="onImageLoad($event, product)"
                 @error="onImageError(product)"
                 style="width: 100%; height: 100%; "/>
          </div>

          <div style="width: 400px">
            <p>卖家：{{product.seller_username}}———价格：{{product.price}}元</p>
            <p>作者：{{product.author}}———出版社：{{product.publisher}}</p>
            <p>描述：{{product.description}}</p>
            <!-- 添加商品数量控制器 -->
            <div class="quantity-control">
              <span>数量：</span>
              <div class="quantity-buttons">
                <el-button
                    size="small"
                    @click="decreaseQuantity(product)"
                    :disabled="product.amount <= 1"
                    circle
                >
                  <el-icon><Minus /></el-icon>
                </el-button>
                <el-input-number
                    v-model="product.amount"
                    :min="1"
                    :max="product.stock"
                    size="small"
                    :controls="false"
                    class="quantity-value"
                    @change="handleQuantityChange(product)"
                    @blur="handleBlur(product)"
                />
                <el-button
                    size="small"
                    @click="increaseQuantity(product)"
                    :disabled="product.amount >= product.stock"
                    circle
                >
                  <el-icon><Plus /></el-icon>
                </el-button>
              </div>
              <div class="subtotal">小计：{{ (product.price * product.amount).toFixed(2) }}元</div>
          </div>


        </div>

        <div class="price-button-container">
          <el-button type="primary" plain @click="orderNew(product)" :disabled="!product.valid">立即下单</el-button>
          <el-button type="danger" plain @click="Delete(product)" :disabled="!product.valid">删除</el-button>
        </div>
      </div>
    </el-card>
  </p>


  </div>
  <el-footer class="footer-div">
    <div class="left">
      <el-checkbox v-model="selectAll" label="全选" size="large" :indeterminate="isIndeterminate" @change="handleSelectAllChange"/>
    </div>
    <div class="right">
      <p style="margin-top: 25px">总计：{{totalMoney}}元</p>
      <el-button type="danger" plain style="margin-top: 20px" @click="DeleteTogether" :disabled="Val">全部删除</el-button>
      <el-button type="primary" plain style="margin-top: 20px" @click="OrderNewTogether" :disabled="Val">一键下单</el-button>
    </div>
  </el-footer>
</template>

<script lang="ts" setup>
import {ref, onMounted,reactive, defineEmits, defineProps, watch, computed, onBeforeUnmount, onUpdated} from 'vue';
import type { CheckboxValueType } from 'element-plus';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Minus } from '@element-plus/icons-vue';
import api from '@/api/index.js';

// 处理数量输入框变化
const handleQuantityChange = (product) => {
  // 确保数量是整数
  product.amount = Math.floor(product.amount);

  // 确保数量在有效范围内
  if (product.amount < 1) product.amount = 1;
  if (product.amount > product.stock) product.amount = product.stock;

  console.log("aa")
};

const handleBlur = (product) => {
  // 确保数量是整数
  product.amount = Math.floor(product.amount);

  // 确保数量在有效范围内
  if (product.amount < 1) product.amount = 1;
  if (product.amount > product.stock) product.amount = product.stock;

  console.log(`失去焦点后数量为: ${product.amount}`);
};

const totalMoney = computed(() => {
  let total = 0;
  books.value.forEach((product) => {
    if (product.checked) {
      total += product.price * product.amount;
    }
  });
  return total.toFixed(2);
});
const books = ref([])
const selectAll = ref(false);  // 全选状态
const isIndeterminate = ref(false);  // 半选状态

const Val = computed(() => {
  console.log("11111111")
  return books.value.filter(item => item.valid).length === 0;
});

const DeleteTogether = () => {
  const selectedBooks = books.value.filter(item => item.checked);
  if (selectedBooks.length === 0) {
    ElMessage.warning('请至少选择一个商品');
    return;
  }

  const id_list = selectedBooks.map(item => item.item_id);
  api.deleteBookCarDelete(id_list).then(res => {
    if (res.data.code === 200) {
      ElMessage.success('删除成功');
      books.value = books.value.filter(item => !item.checked);
      updateSelectAllStatus();
    } else {
      ElMessage.error('删除失败');
    }
  }).catch(error => {
    console.error('删除商品失败:', error);
    ElMessage.error('网络问题，删除商品失败');
  });
};

const OrderNewTogether = () => {
  const selectedBooks = books.value.filter(item => item.checked);
  if (selectedBooks.length === 0) {
    ElMessage.warning('请至少选择一个商品');
    return;
  }
  console.log("要下单了")
  const list = selectedBooks.map(item => ({item_id: item.item_id, amount: item.amount}));
  api.postOrderNew(list).then(res => {
    if (res.data.code === 200) {
      ElMessage.success('下单成功');
      books.value = books.value.filter(item => !item.checked);
      updateSelectAllStatus();
    } else {
      ElMessage.error('下单失败');
    }
  }).catch(error => {
    console.error('下单失败:', error);
    ElMessage.error('网络问题，下单失败');
  });
};

// 全选/取消全选处理
const handleSelectAllChange = () => {
  // 将所有商品的选中状态设置为全选框的状态
  books.value.forEach(item => {
    item.checked = selectAll.value;
  });
  isIndeterminate.value = false;
};

// 更新全选状态
const updateSelectAllStatus = () => {
  if (books.value.length === 0) {
    selectAll.value = false;
    isIndeterminate.value = false;
    return;
  }

  const checkedCount = books.value.filter(item => item.checked).length;

  // 全选状态
  if (checkedCount === books.value.length) {
    selectAll.value = true;
    isIndeterminate.value = false;
  }
  // 部分选中状态
  else if (checkedCount > 0) {
    selectAll.value = false;
    isIndeterminate.value = true;
  }
  // 全不选状态
  else {
    selectAll.value = false;
    isIndeterminate.value = false;
  }
};

// 处理单个商品选中状态变化
const handleItemChecked = () => {
  updateSelectAllStatus();
};

// 增加商品数量
const increaseQuantity = (product) => {
  product.amount++;
  updateCartQuantity(product);
};

// 减少商品数量
const decreaseQuantity = (product) => {
  if (product.amount > 1) {
    product.amount--;
    updateCartQuantity(product);
  }
};

// 更新购物车商品数量
const updateCartQuantity = (product) => {
  // 调用API更新购物车商品数量
  api.updateCartQuantity(product.id, product.amount)
      .then(res => {
        if (res && res.data && res.data.code === 200) {
          console.log(`商品 ${product.name} 数量更新为 ${product.amount}`);
        } else {
          ElMessage.error('更新商品数量失败');
        }
      })
      .catch(error => {
        console.error('更新商品数量失败:', error);
        ElMessage.error('网络问题，更新商品数量失败');
      });
};

const Delete = (product) => {
  console.log("123456",product.item_id)
  const id_list = reactive([product.item_id])
  console.log("1232,",id_list)
  api.deleteBookCarDelete(id_list).then(res => {
    console.log(res.data.code)
    if (res.data.code === 200) {
      ElMessage.success('删除成功');
      books.value = books.value.filter(item => item.id !== product.id);
      updateSelectAllStatus();
    } else {
      ElMessage.error('删除失败');
    }
  }).catch(error => {
    console.error('删除商品失败:', error);
    ElMessage.error('网络问题，删除商品失败');
  });
};

const orderNew = (product) => {
  console.log("下单",product)
  product.valid = false
  const list = ([{item_id:product.item_id, amount:product.amount}])
  api.postOrderNew(list).then(res => {
    if (res.data.code === 200) {
      ElMessage.success('下单成功');
      books.value = books.value.filter(item => item.id !== product.id);
      updateSelectAllStatus();
    } else {
      product.valid = true
      ElMessage.error('下单失败');
    }
  }).catch(error => {
    product.valid = true
    console.error('下单失败:', error);
    ElMessage.error('网络问题，下单失败');
  });
};

// 图片加载成功处理函数
const onImageLoad = (event, product) => {
  console.log(product.id, "图片加载中");
  product.loaded = true;
};

// 图片加载失败处理函数
const onImageError = (product) => {
  console.error(`图片加载失败: ${product.picture_url}`);
  product.picture_url = 'https://via.placeholder.com/200x200';
  product.loaded = true;
};



onMounted(() => {
  api.getBookCar().then(res => {
    if (res.data.code === 200) {
      books.value = res.data.data;
      console.log("books:",books.value)
      ElMessage.success('获取商品列表成功');
    }else {
      ElMessage.error('获取商品列表失败');
    }
  }).catch(error => {
    console.error('获取商品列表失败:', error);
    ElMessage.error('网络问题，获取商品列表失败');
  });
});


onBeforeUnmount(() => {
  api.postReturnBookCar(books.value).then(res => {
    if (res.data.code === 200) {
      ElMessage.success('返回购物车成功');
    }else {
      ElMessage.error('返回购物车失败');
    }
  }).catch(error => {
    console.error('返回购物车失败:', error);
  });
});
</script>

<style scoped>
.productitem {
  display: flex;
  align-items: center;
  width: auto;
  margin-bottom: 20px;
  gap: 10px; /* 多选框和卡片之间留点空隙 */
}

.cardclass {
  width: 800px;
  height: auto;
  min-height: 35vh;
  margin-bottom: 20px;
  margin-left: 30px;
}

.app-container::-webkit-scrollbar {
  display: none; /* Chrome, Safari 和 Opera */
}

.product-display {
  max-height: 800px;
  display: flex;
  flex-direction: column;
  align-items: center; /* 水平居中 */
  overflow-y: auto;
  position: relative; /* 确保 el-backtop 定位基于此容器 */

  /* 下面是隐藏滚动条的关键 */
  scrollbar-width: none; /* Firefox 隐藏滚动条 */
  -ms-overflow-style: none; /* IE/Edge 隐藏滚动条 */
}

.product-display::-webkit-scrollbar {
  display: none; /* Chrome, Safari 和 Opera */
}

.card-content {
  display: flex;
  flex-direction: row;
  gap: 15px;
  height: calc(100% - 40px);
  text-align: left;
}

/* 数量控制器样式 */
.quantity-control {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin: 10px 0;
}

.quantity-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quantity-value {
  min-width: 20px;
  text-align: center;
  font-size: 16px;
}

.subtotal {
  margin-left: 20px;
  font-weight: bold;
  color: #f56c6c;
}

.price-button-container {
  display: flex;
  gap: 10px; /* 控制按钮之间的间距 */
  flex-direction: column-reverse;
  justify-content: right; /* 让按钮靠右对齐 */
  margin-top: 100px;
}

.price-button-container .el-button {
  margin-left: 0; /* 让按钮靠右 */
}

/* 底部结算栏样式 */
.cart-footer {
  position: sticky;
  bottom: 0;
  width: 780px;
  background-color: #fff;
  padding: 15px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  margin-top: 20px;
  border-radius: 4px;
  z-index: 10;
}

.cart-total {
  font-size: 16px;
  font-weight: bold;
  color: #f56c6c;
}

.selected-count {
  font-size: 12px;
  color: #909399;
  margin-left: 5px;
}

.footer-div{
  border-top: 1px solid;
  height: 50px;
  display: flex;
  justify-content: space-between; /* 左右分开 */
  align-items: center; /* 上下居中，可选 */
}

.left, .right {
  display: flex;
  gap: 10px; /* 两个按钮之间有间距 */
}
</style>
