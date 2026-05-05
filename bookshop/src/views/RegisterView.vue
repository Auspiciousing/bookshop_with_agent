<template>
  <div class="register-container">
    <div class="register-box">
      <h2 class="title">校园二手书售卖平台注册</h2>
      <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" label-position="left" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请确认密码"></el-input>
        </el-form-item>
      </el-form>
      <el-form-item>
        <el-button type="primary" class="register-btn" :loading="loading" @click="handleRegister">注册</el-button>
      </el-form-item>
      <div class="login-link">
        <router-link to="/login">已有账号？立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import {onMounted, onUnmounted, ref} from 'vue';
import { ElMessage, ElLink } from 'element-plus';
import api from "@/api/index.js"
import router from "@/router/index.js";

const loading = ref(false);
const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: ''
});

const registerRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不少于6位', trigger: 'blur' }
  ],
  confirmPassword: [{ required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value === "") {
          callback(new Error("请确认密码"));
        } else if (value!== registerForm.value.password) {
          callback(new Error("两次输入的密码不一致"));
        } else {
          callback();
        }
      },
      trigger: "blur",
    }]
};

const handleRegister = () => {
  // Mock registration process
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    ElMessage.error('两次密码输入不一致');
    return;
  }

  loading.value = true;
  api.postRegister(registerForm.value.username, registerForm.value.password).then(res => {
    console.log(res);
    if (res.data.code === 200) {
      ElMessage.success('注册成功');
      goToLogin();
      loading.value = false;
    } else {
      ElMessage.error('注册失败，请稍后再试');
      loading.value = false;
    }
  }).catch(err => {
    console.error(err);
    ElMessage.error('注册失败，请稍后再试');
    loading.value = false;
  });

};

const goToLogin = () => {
  // Redirect to login page (this is just a mock for now)
  console.log('Redirect to login page');
  router.push('/login');
};

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
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;

  background-image: url("@/assets/images/loginbg.png");
  background-size: 100% 100%;
  z-index: 1;
}

.register-box {
  background: #ffffff;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  width: 350px;
  text-align: center;
}

.title {
  font-size: 24px;
  margin-bottom: 40px;
}

.el-form-item {
  margin-bottom:40px;
}

.register-btn {
  width: 100%;
}

.login-link {
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
.app-container::-webkit-scrollbar {
  display: none; /* Chrome, Safari 和 Opera */
}
</style>
