<template>
  <p style="display: flex;align-items: center;text-align: center;font-size: 30px;font-family: 华文行楷">订单页面</p>
  <div class="product-display" @change="">
    <div class="products-container">
      <el-table
          v-if="category==='payment'"
          :data="currentTableData"
          style="width: 100%;"
          :row-class-name="tableRowClassName"
          :cell-style="{ textAlign: 'center' }"
          :header-cell-style="{ textAlign: 'center' }"
          height="700"
      >
        <template #empty>
          <el-empty description="暂无售卖数据" />
        </template>
        <el-table-column prop="order_id" label="订单编号" width="180" />
        <el-table-column prop="total_price" label="需支付金额" width="180" />
        <el-table-column prop="created_at" label="订单创建时间" />
        <el-table-column label="订单支付倒计时" >
          <template #default="scope">
            <span v-if="scope.row.remaining_seconds">{{ Math.floor(parseInt(scope.row.remaining_seconds)/60) }}:{{ parseInt(scope.row.remaining_seconds)%60 }}</span>
            <span v-else></span>
          </template>
        </el-table-column>
        <el-table-column label="状态">
          <template #default="scope">
            <span v-if="scope.row.status === 'pending_payment'">待支付</span>
            <span v-else-if="scope.row.status === 'expired'">已超时</span>
            <span v-else-if="scope.row.status === 'cancelled'">已取消</span>
            <span v-else-if="scope.row.status === 'paid'">已支付</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220">
          <template #default="scope">
            <el-button size="small" type="primary" @click="showOrderDetails(scope.row)">详情</el-button>
            <el-button v-if="scope.row.status==='pending_payment'" size="small" type="warning" @click="pay(scope.row)">支付</el-button>
            <el-button v-if="scope.row.status==='pending_payment'" size="small" type="danger" @click="deleteOrders(scope.row)">取消</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-table
          v-else
          :data="currentTableData"
          style="width: 100%;"
          :cell-style="{ textAlign: 'center' }"
          :header-cell-style="{ textAlign: 'center' }"
          height="700"
      >
        <template #empty>
          <el-empty description="暂无售卖数据" />
        </template>
        <el-table-column label="书名" prop="book_title"></el-table-column>
        <el-table-column label="单价" prop="book_price"></el-table-column>
        <el-table-column label="数量" prop="book_amount"></el-table-column>
        <el-table-column label="小计" prop="total_price"></el-table-column>
        <el-table-column label="状态">
          <template #default="scope">
            <span v-if="scope.row.status==='shipped'">待收货</span>
            <span v-else-if="scope.row.status==='completed'">已到货</span>
          </template>
        </el-table-column>
        <el-table-column label="详情">
          <template #default="scope">
            <el-button type="primary" @click="showShippingBookDetail(scope.row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页组件 -->
      <el-pagination
          class="pagination"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[5, 10, 20, 50]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          :pager-count="7"
          prev-text="上一页"
          next-text="下一页"
      />
    </div>
  </div>

  <!-- 订单详情对话框 -->
  <el-dialog
      v-model="dialogVisible"
      title="订单详情"
      width="70%"
      :before-close="handleClose"
  >
    <div v-if="selectedOrder" class="order-details">
      <el-descriptions title="订单基本信息" :column="2" border>
        <el-descriptions-item label="订单编号">{{ selectedOrder.order_id }}</el-descriptions-item>
        <el-descriptions-item label="订单总金额">
          <span class="price-text">¥{{ selectedOrder.total_price }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ selectedOrder.created_at }}</el-descriptions-item>
        <el-descriptions-item label="支付死期">{{ selectedOrder.payment_deadline }}</el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="center">商品详情</el-divider>

      <el-table :data="selectedOrder.order_items" border stripe>
        <el-table-column prop="book_title" label="书名" />
        <el-table-column prop="book_author" label="作者" />
        <el-table-column prop="book_price" label="单价">
          <template #default="scope">
            ¥{{ scope.row.book_price }}
          </template>
        </el-table-column>
        <el-table-column prop="book_amount" label="数量" />
        <el-table-column label="小计">
          <template #default="scope">
            ¥{{ (scope.row.book_price * scope.row.book_amount).toFixed(2) }}
          </template>
        </el-table-column>
      </el-table>

      <el-divider content-position="center">卖家信息</el-divider>

      <div v-for="(item, index) in selectedOrder.order_items" :key="index" class="seller-section">
        <el-descriptions :title="`卖家信息 ${index + 1}`" :column="1" border>
          <el-descriptions-item label="卖家" :span="2">{{ item.seller_username }}</el-descriptions-item>
          <el-descriptions-item label="卖家地址" :span="10">{{ item.seller_address }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </div>

    <template #footer>
    <span class="dialog-footer">
      <el-button @click="dialogVisible = false">关闭</el-button>
    </span>
    </template>
  </el-dialog>

  <!-- 待收货详情对话框 -->
  <el-dialog
      v-model="shippingDialogVisible"
      title="收货详情"
      width="70%"
      :before-close="handleShippingClose"
  >
    <div v-if="selectedShippingOrder" class="order-details">
      <el-descriptions title="订单基本信息" :column="2" border>
        <el-descriptions-item label="书名">{{ selectedShippingOrder.book_title }}</el-descriptions-item>
        <el-descriptions-item label="作者">{{ selectedShippingOrder.book_author }}</el-descriptions-item>
        <el-descriptions-item label="单价">
          <span class="price-text">¥{{ selectedShippingOrder.book_price }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="数量">{{ selectedShippingOrder.book_amount }}</el-descriptions-item>
        <el-descriptions-item label="小计">
          <span class="price-text">¥{{ (selectedShippingOrder.book_price * selectedShippingOrder.book_amount).toFixed(2) }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="状态">{{selectedShippingOrder.status==='shipped'?'待收货':'已到货'}}</el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="center">卖家信息</el-divider>

      <el-descriptions :column="1" border>
        <el-descriptions-item label="卖家" :span="2">{{ selectedShippingOrder.seller_username }}</el-descriptions-item>
        <el-descriptions-item label="卖家地址" :span="10">{{ selectedShippingOrder.seller_address }}</el-descriptions-item>
      </el-descriptions>

<!--      <el-divider content-position="center">物流信息</el-divider>-->

<!--      <el-timeline>-->
<!--        <el-timeline-item-->
<!--            v-for="(activity, index) in selectedShippingOrder.logistics || [{content: '商品已发出', timestamp: '2023-01-01 12:00:00'}]"-->
<!--            :key="index"-->
<!--            :timestamp="activity.timestamp"-->
<!--        >-->
<!--          {{ activity.content }}-->
<!--        </el-timeline-item>-->
<!--      </el-timeline>-->
    </div>

    <template #footer>
    <span class="dialog-footer">
      <el-button @click="shippingDialogVisible = false">关闭</el-button>
      <el-button type="primary" @click="confirmReceipt(selectedShippingOrder)">确认收货</el-button>
    </span>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted,computed,defineEmits, defineProps, watch, reactive } from 'vue';
import { useCounterStore } from '@/stores/counter';  // 引入 Pinia store
import api from "@/api/index.js";
import {ElMessage, ElMessageBox} from "element-plus";

// 确认收货的方法
const confirmReceipt = (order) => {
  // 调用确认收货的API
  ElMessageBox.confirm('确认已收到商品?', '提示', {
    confirmButtonText: '确认收货',
    cancelButtonText: '再等等',
    type: 'warning',
    // 自定义按钮点击事件处理
    distinguishCancelAndClose: true, // 区分取消和关闭事件
    callback: (action) => {
      if (action === 'confirm') {
        // 确认按钮点击事件
        handleConfirmReceipt(order);
      } else if (action === 'cancel') {
        // 取消按钮点击事件
        handleCancelReceipt();
      }
    }
  });
};

// 确认收货的处理函数
const handleConfirmReceipt = (order) => {
  // 调用确认收货API
  // console.log("order:",order)
  api.postConfirmReceipt(order.id).then(res => {
    if (res.data.code === 200) {
      ElMessage.success('确认收货成功');
      // 将订单状态改为已完成，而不是从列表中移除
      products.value = products.value.filter(item => item.id != order.id);
      total.value = products.value.length;
      shippingDialogVisible.value = false;
    } else {
      ElMessage.error(res.data.message || '确认收货失败');
    }
  }).catch(err => {
    console.error(err);
    ElMessage.error('网络问题，确认收货失败');
  });
};

// 取消收货的处理函数
const handleCancelReceipt = () => {
  ElMessage({
    type: 'info',
    message: '您已取消确认收货操作'
  });
  shippingDialogVisible.value = false;
};

// 待收货书籍详情对话框
const shippingDialogVisible = ref(false);
const selectedShippingOrder = ref(null);

const showShippingBookDetail = (order) => {
  selectedShippingOrder.value = order;
  shippingDialogVisible.value = true;
};

// 处理收货对话框关闭
const handleShippingClose = () => {
  shippingDialogVisible.value = false;
};

const pay = (order) => {
  api.postPay(order.order_id).then((res) => {
    if(res.data.code === 200){
      ElMessage.success("订单支付成功");
      const orderIndex = products.value.findIndex(item => item.order_id === order.order_id);
      products.value[orderIndex].status = 'paid';
      products.value[orderIndex].remaining_seconds = null;
    }else{
      ElMessage.error(res.data.message);
    }
  }).catch((err) => {
    console.log(err)
    ElMessage.error("网络问题，订单支付失败");
  })
}

const deleteOrders = (order) => {
  api.deleteOrder(order.order_id).then((res) => {
    if(res.data.code === 200){
      ElMessage.success("订单删除成功");
      const orderIndex = products.value.findIndex(item => item.order_id === order.order_id);
      products.value[orderIndex].status = 'cancelled';
      products.value[orderIndex].remaining_seconds = null;

      // total.value = products.value.length;
    }else{
      ElMessage.error("订单删除失败");
    }
  }).catch((err) => {
    console.log(err)
    ElMessage.error("网络问题，订单删除失败");
  })
}

const dialogVisible = ref(false)
const selectedOrder = ref(null)

// 显示订单详情
const showOrderDetails = (order) => {
  selectedOrder.value = order;
  dialogVisible.value = true;
};

// 处理对话框关闭
const handleClose = () => {
  dialogVisible.value = false;
};

const products = ref([])

const handleSizeChange = (newSize) => {
  pageSize.value = newSize;
  currentPage.value = 1; // 重置页码为第一页
};

// 当前页码变化时的回调
const handleCurrentChange = (newPage) => {
  currentPage.value = newPage;
};

// 分页相关参数
const currentPage = ref(1); // 当前页码
const pageSize = ref(10);    // 每页显示数量
const total = ref(products.value.length); // 数据总数

// 计算当前页要显示的数据
const currentTableData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return products.value.slice(start, end);
});


interface products {
  order_id: number;
  total_price: number;
  created_at: string;
  payment_deadline: string;
  remaining_seconds: string;
  status:string,
  order_items: {
    seller_id: number,
    seller_username: string,
    seller_address: string,
    book_price: number,
    book_amount: number,
    book_title: string,
    book_author: string
  }[];
}
const tableRowClassName = ({
                             row,
                             rowIndex,
                           }: {
  row: products
  rowIndex: number
}) => {

  const remainingSeconds = parseInt(row.remaining_seconds);
  console.log("判断中")
  if (row.status === "pending_payment"){
    if (remainingSeconds < 300)
      return 'error-row'
    else
      return 'success-row'
  }else if(row.status === "expired"){
    return 'warning-row'
  }else if(row.status === "cancelled"){
    return 'info-row'
  }else{
    return ''
  }

}

const props = defineProps({
  category: String,
});

// 获取 Pinia store
const productsStore = useCounterStore();

// 声明计时器变量和管理对象
const timers = ref({});

// 启动计时器方法
const startCountdown = () => {
  // 清除现有计时器
  Object.values(timers.value).forEach(timer => clearInterval(timer));
  timers.value = {};

  // 为每个订单创建计时器
  products.value.forEach(order => {
    if (order.remaining_seconds && parseInt(order.remaining_seconds) > 0) {
      timers.value[order.order_id] = setInterval(() => {
        // 每秒减一
        const seconds = parseInt(order.remaining_seconds);
        if (seconds > 0) {
          order.remaining_seconds = (seconds - 1).toString();
        } else {
          // 时间到，清除计时器
          clearInterval(timers.value[order.order_id]);
          delete timers.value[order.order_id];
          order.remaining_seconds = "0";
          order.remaining_seconds = null;
          if(order.status!="cancelled" && order.status!="paid")order.status = "expired";
        }
      }, 1000);
    }
  });
};

onMounted(() => {
  if (props.category == "payment") {
    api.getOrderUnpaid().then((res) => {
      if(res.data.code === 200){
        products.value = res.data.data;
        total.value = products.value.length;
        startCountdown(); // 启动计时器
        console.log("订单信息:",products.value)
        ElMessage.success("订单获取成功");
      }else{
        ElMessage.error("订单获取失败");
      }
    }).catch((err) => {
      console.log(err)
      ElMessage.error("网络问题，订单获取失败");
    })
  } else if (props.category === "delivering") {
    api.getShippingBook().then((res) => {
      console.log(res.data.code)
      if(res.data.code === 200){
        products.value = res.data.data;
        total.value = products.value.length;
        console.log("订单信息:",products.value)
        ElMessage.success("订单获取成功");
      }else{
        ElMessage.error("订单获取失败");
      }
    }).catch((err) => {
      console.log(err)
      ElMessage.error("网络问题，订单获取失败");
    })
  } else {
    api.getCompletedBook().then((res) => {
      if(res.data.code === 200){
        products.value = res.data.data;
        total.value = products.value.length;
        console.log("订单信息:",products.value)
        ElMessage.success("订单获取成功");
      }else{
        ElMessage.error("订单获取失败");
      }
    }).catch((err) => {
      console.log(err)
      ElMessage.error("网络问题，订单获取失败");
    })
  }
})

// 组件卸载时清除所有计时器避免内存泄漏
onUnmounted(() => {
  Object.values(timers.value).forEach(timer => clearInterval(timer));
});

</script>

<style scoped>
/* 其他已有样式保持不变 */

.seller-section {
  margin-bottom: 20px;
}

/* 控制描述列表中标签的宽度 */
:deep(.el-descriptions__cell) {
  min-width: 100px;
}

:deep(.el-descriptions__label) {
  width: 60px;
}
</style>

<style scoped>
.product-display {
  max-height: 800px;
  width: 100%;
  overflow-y: auto;
  position: relative;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.product-display::-webkit-scrollbar {
  display: none;
}

.products-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}



</style>

<style type="scss">
.el-table .error-row {
  --el-table-tr-bg-color: var(--el-color-error-light-9);
}
.el-table .warning-row {
  --el-table-tr-bg-color: var(--el-color-warning-light-9);
}
.el-table .success-row {
  --el-table-tr-bg-color: var(--el-color-success-light-9);
}
.el-table .info-row {
  --el-table-tr-bg-color: var(--el-color-info-light-9);
}
</style>
