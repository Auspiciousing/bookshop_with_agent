<template>
  <el-container class="header-container">
    <el-main>
      <el-input
          v-model="input"
          style="width: 800px;margin-top: -20px"
          placeholder="请输入书名、作者或者描述"
          class="input-with-select"
          @keydown.enter="handleClick"
      >
        <template #prepend>
          <el-select v-model="select" placeholder="Select" style="width: 115px">
            <el-option label="全文搜索" value="1" />
            <el-option label="模糊搜索" value="2" />
          </el-select>
        </template>

        <template #append >
          <el-button :icon="Search" @click="handleClick"/>
        </template>
      </el-input>
    </el-main>
    <el-aside class="right-space">
        <el-menu class="platform_avatar" menu-trigger="hover" @select="handleSelect" :default-active="activeIndex" mode="horizontal" popper-effect="0">
          <el-sub-menu>
            <template #title>
              <el-avatar :size="40" :src="src" />
              &nbsp;用户名
            </template>
            <router-link to="/self"><el-menu-item>个人空间</el-menu-item></router-link>
            <router-link to="/account"><el-menu-item>账户信息</el-menu-item></router-link>
            <el-menu-item @click="recharge">我的钱包:{{money}}元</el-menu-item>
            <router-link to="/"><el-menu-item>退出登录</el-menu-item></router-link>
          </el-sub-menu>
        </el-menu>
    </el-aside>
  </el-container>
</template>

<script lang="ts" setup>
import {ref, reactive, defineProps,onMounted} from 'vue'
  import {ElMessage, ElMessageBox} from "element-plus";
  import 'element-plus/dist/index.css';
  import { Search } from '@element-plus/icons-vue'
  import api from "@/api/index.js";
  import router from '@/router';
  const src = ref();
  const props = defineProps({
    type: String,
  });
  const handleClick = () => {
    if (input.value.trim() === '') {
      ElMessage({
        type: 'warning',
        message: '请输入查询内容'
      });
      return;
    }
    if (select.value === '1') {
      api.postBookSearch(input.value).then((response) => {
        if (response.data.code === 200) {
          ElMessage({
            type: 'success',
            message: '查询成功'
          });
          console.log(props)
          // 这里可以添加查询逻辑
          console.log('查询内容:', input.value);
          if (props.type === "shop")
          {
            const refreshEvent = new CustomEvent('refresh-table');
            window.dispatchEvent(refreshEvent);
          }else{
            console.log("跳转")
            router.push('/shop')
          }

        } else {
          ElMessage({
            type: 'error',
            message: '查询失败'
          });
        }
      }).catch((error) => {
        console.error('查询错误:', error);
        ElMessage({
          type: 'error',
          message: '查询发生错误'
        });
      });
    }else if (select.value === '2') {
      api.postBookBlurSearch(input.value).then((response) => {
        if (response.data.code === 200) {
          ElMessage({
            type: 'success',
            message: '查询成功'
          });
          console.log(props)
          // 这里可以添加查询逻辑
          console.log('查询内容:', input.value);
          if (props.type === "shop")
          {
            const refreshEvent = new CustomEvent('refresh-table');
            window.dispatchEvent(refreshEvent);
          }else{
            console.log("跳转")
            router.push('/shop')
          }

        } else {
          ElMessage({
            type: 'error',
            message: '查询失败'
          });
        }
      }).catch((error) => {
        console.error('查询错误:', error);
        ElMessage({
          type: 'error',
          message: '查询发生错误'
        });
      });
    }


  }

  const money = ref();

  onMounted(() => {
    // 这里可以添加组件加载时的逻辑
    api.getMoney().then((response) => {
      if (response.data.code === 200) {
        money.value = response.data.balance;
        src.value = response.data.avatar;
        // ElMessage({
        //   type: 'success',
        //   message: '余额获取成功'
        // });
      } else {
        ElMessage({
          type: 'error',
          message: '余额获取失败'
        });
      }
    }).catch((error) => {
      console.error('余额获取错误:', error);
      ElMessage({
        type: 'error',
        message: '余额获取发生错误'
      });
    });
  });

  const select = ref('1');

  const activeIndex = ref('1')
  const handleSelect = (key: string, keyPath: string[]) => {
    console.log(key, keyPath)
  }
  const user=reactive({
    username:"牛魔"
  })
  const input = ref('')

  const recharge = () => {
    ElMessageBox.prompt('是否充值？', '提示', {
      confirmButtonText: '确认充值',
      cancelButtonText: '取消',
      inputPattern: /^[1-9]\d*(\.\d{1,2})?$|^0\.\d{1,2}$/,
      inputErrorMessage: '请输入有效金额（正数，最多两位小数）',
      inputType: 'text',
      inputPlaceholder: '请输入充值金额',
      roundButton: true
    }).then(({ value }) => {
      const amount = parseFloat(value);
      if (isNaN(amount) || amount <= 0) {
        ElMessage.error('请输入有效的充值金额');
        return;
      }
      api.postRecharge(amount).then((response) => {
        if (response.data.code === 200) {
          money.value = response.data.balance;
          ElMessage({
            type: 'success',
            message: '充值成功'
          });
        } else {
          ElMessage({
            type: 'error',
            message: '充值失败'
          });
        }
      }).catch((error) => {
        console.error('充值错误:', error);
        ElMessage({
          type: 'error',
          message: '充值发生错误'
        });
      });
      ElMessage({
        type: 'success',
        message: '充值成功'
      })
    }).catch(() => {
      ElMessage({
        type: 'info',
        message: '已取消充值'
      })
    })
  }
</script>

<style scoped>
  .header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 0px;

  }

  .right-space {

    display: flex;
    align-items: center;
  }
  .el-sub-menu__icon-arrow {
    display: none;
  }
  .platform_avatar{
    width: 230px;
    height: auto;
    background-color: white;
    margin-left: auto;
    margin-top: -8px;

    padding: 0;
  }
  a {
    text-decoration: none;
    color: #000;
  }
  a:hover {
    color: cornflowerblue;
  }
</style>
