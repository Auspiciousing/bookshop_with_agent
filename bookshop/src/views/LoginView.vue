<template>
  <div class="login-container">
<!--    <video ref="videoRef" src="@/assets/general/talk.mp4" autoplay loop playsinline style="width: 100%;height: 100%;object-fit: fill;position: fixed;top: 0; left: 0; z-index: -2;"/>-->

    <div class="login-box">
      <h2 class="title">校园二手书售卖平台登录</h2>
      <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" label-position="left" label-width="70px">
        <el-form-item label="账户" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名/邮箱"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
      </el-form>
      <el-form-item>
        <el-button type="primary" class="login-btn" :loading="loading" @click="handleLogin">登录</el-button>
      </el-form-item>
      <div class="register-link">
        <router-link to="/register">没有账号？立即注册</router-link>
      </div>
    </div>
  </div>

</template>


<script setup>
import {ref, onMounted, onUnmounted, reactive} from 'vue'
import { ElMessage, ElLink } from 'element-plus'
import router from "@/router/index.js"
import api from "@/api/index.js";
import 'element-plus/dist/index.css';
import { useCounterStore } from '@/stores/counter';  // 引入 Pinia store
const productsStore = useCounterStore();

const loading = ref(false);
const loginForm = ref({
  username: '',
  password: ''
});

const loginRules = {
  username: [{ required: true, message: '请输入用户名或邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
};

const handleLogin = () => {
  // Mock login process
  loading.value = true;
  // console.log(loginForm.value.username)
  console.log("点击登录")
  api.postLogin(loginForm.value.username,loginForm.value.password).then(res => {
    if (res.data.code === 200) {
      productsStore.userInfo.id = res.data.id;
      ElMessage.success("欢迎登陆，"+res.data.id);
      router.push('/home');
      loading.value = false;
    } else {
      ElMessage.error('登录失败，请检查用户名和密码');
      loading.value = false;
    }
  }).catch(err => {
    console.error(err);
    ElMessage.error('登录失败，请稍后再试');
    loading.value = false;
  });

};



const preventBodyScroll = () => {
  document.body.style.overflow = 'hidden';
};

// 恢复页面滚动
const restoreBodyScroll = () => {
  document.body.style.overflow = 'auto';
};

const videoRef = ref(null);
const hasInteracted = ref(false);

// 检测用户交互
const handleUserInteraction = () => {
  if (!hasInteracted.value && videoRef.value) {
    hasInteracted.value = true;
    // 尝试播放视频并取消静音
    videoRef.value.muted = false;
    videoRef.value.play().catch(error => {
      console.warn('用户交互后视频播放失败:', error);
      // 仍然失败则恢复静音并再次尝试播放
      videoRef.value.muted = true;
      videoRef.value.play();
    });

    // 移除事件监听器
    document.removeEventListener('click', handleUserInteraction);
    document.removeEventListener('keydown', handleUserInteraction);
  }
};

onMounted(() => {
  preventBodyScroll();

  // 添加用户交互检测
  document.addEventListener('click', handleUserInteraction);
  document.addEventListener('keydown', handleUserInteraction);

});

onUnmounted(() => {
  restoreBodyScroll();

  document.removeEventListener('click', handleUserInteraction);
  document.removeEventListener('keydown', handleUserInteraction);
});

</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;

  background-image: url("@/assets/images/loginbg.png");
  background-size: 100% 100%;
  z-index: 1;
}



.login-box {
  background: #ffffff;
  padding: 40px;
  border-radius: 8px;

  width: 350px;
  text-align: center;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px); /* 兼容 Safari 浏览器 */
  opacity: 0.8;
}

.title {
  font-size: 24px;
  margin-bottom: 40px;
}

.el-form-item {
  margin-bottom:40px;
}

.login-btn {
  width: 100%;
}

.register-link {
  margin-top: 15px;
  font-size: 14px;
}

a {
  text-decoration: none;
  color: #000;
}
a:hover {
  color: cornflowerblue;
}

</style>
