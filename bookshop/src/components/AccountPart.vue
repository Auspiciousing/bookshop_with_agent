<script setup>
import { ref, reactive, toRefs, onMounted,computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from "@/api/index.js";
import 'element-plus/dist/index.css';
import { useCounterStore } from '@/stores/counter';  // 引入 Pinia store
const productsStore = useCounterStore();
const userInfo = reactive({
  passwordLastModified:null,
  phone:null,
  email:null
})

// 倒计时
const countdown = ref(0)

// 表单数据
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const phoneForm = reactive({
  phone: '',
  code: ''
})

const emailForm = reactive({
  email: '',
  code: ''
})

const verifyForm = reactive({
  realName: '',
  idNumber: ''
})

// 弹窗状态
const passwordDialogVisible = ref(false)
const phoneDialogVisible = ref(false)
const emailDialogVisible = ref(false)
const verifyDialogVisible = ref(false)
  // 修改密码
  const changePassword = () => {
    passwordDialogVisible.value = true
    //console.log(passwordDialogVisible.value)
  }

  // 提交修改密码
  const submitPassword = () => {
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      ElMessage.error('两次输入的密码不一致')
      return
    }
    console.log(userInfo.id)
    // 实际项目中这里应该调用API修改密码
    api.postChange_password(userInfo.id,passwordForm.oldPassword,passwordForm.newPassword).then(res => {
      if (res.data.code === 200) {
        ElMessage.success('密码修改成功')
        passwordDialogVisible.value = false
      } else {
        ElMessage.error('密码修改失败，请检查旧密码')
      }
    }).catch(err => {
      console.error(err)
      ElMessage.error('密码修改失败，请稍后再试')
    })

    userInfo.passwordLastModified = new Date().toISOString().split('T')[0]
    resetPasswordForm()
  }

  // 重置密码表单
  const resetPasswordForm = () => {
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  }

  // 绑定/更换手机
  const bindPhone = () => {
    phoneDialogVisible.value = true
    if (userInfo.phone) {
      phoneForm.phone = userInfo.phone
    }
  }

  // 提交绑定手机
  const submitPhone = () => {
    // 实际项目中这里应该调用API绑定手机
    userInfo.phone = phoneForm.phone
    phoneDialogVisible.value = false
    ElMessage.success(`${userInfo.phone ? '更换' : '绑定'}手机成功`)
    resetPhoneForm()
  }

  // 重置手机表单
  const resetPhoneForm = () => {
    phoneForm.phone = ''
    phoneForm.code = ''
  }

  // 发送手机验证码
  const sendPhoneCode = () => {
    if (!phoneForm.phone) {
      ElMessage.error('请输入手机号码')
      return
    }

    // 实际项目中这里应该调用API发送验证码
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)

    ElMessage.success('验证码已发送，请注意查收')
  }

  // 绑定/更换邮箱
  const bindEmail = () => {
    emailDialogVisible.value = true
    if (userInfo.email) {
      emailForm.email = userInfo.email
    }
  }

  // 提交绑定邮箱
  const submitEmail = () => {

    api.postEmailVerify(emailForm.email,emailForm.code).then(res => {
      if (res.data.code === 200) {
        ElMessage.success('邮箱绑定成功')
        // 实际项目中这里应该调用API提交实名认证
        userInfo.email = emailForm.email
        emailDialogVisible.value = false
        ElMessage.success(`${userInfo.email ? '更换' : '绑定'}邮箱成功`)
        resetEmailForm()
      } else {
        ElMessage.error('邮箱绑定失败，请稍后再试')
      }
    }).catch(err => {
      console.error(err)
      ElMessage.error('网络问题，邮箱绑定失败，请稍后再试')
    })
    // 实际项目中这里应该调用API绑定邮箱

  }

  // 重置邮箱表单
  const resetEmailForm = () => {
    emailForm.email = ''
    emailForm.code = ''
  }

  // 发送邮箱验证码
  const sendEmailCode = () => {
    if (!emailForm.email) {
      ElMessage.error('请输入邮箱地址')
      return
    }

    // 实际项目中这里应该调用API发送验证码
    countdown.value = 60
    api.postEmail(emailForm.email).then(res => {
      console.log(emailForm.email)
      if (res.data.code === 200) {
        ElMessage.success('验证码已发送，请注意查收')
      } else {
        ElMessage.error('验证码发送失败，请稍后再试')
      }
    }).catch(err => {
      console.error(err)
      ElMessage.error('网络问题，验证码发送失败，请稍后再试')
    })
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)


  }


  const emailDialogTitle = computed(() => {
    return userInfo.email? '更换邮箱' : '绑定邮箱'
  })

  onMounted(() => {
    console.log('组件加载完成')
    console.log(userInfo)
    api.getAccount().then(res => {
      if (res.data.code === 200) {
        userInfo.passwordLastModified = res.data.change_password_at;
        userInfo.phone = res.data.phone;
        userInfo.email = res.data.email;
        ElMessage.success('获取用户信息成功')
      }
      else {
        ElMessage.error('获取用户信息失败，请稍后再试')
      }
    }).catch(err => {
      console.error(err)
      ElMessage.error('获取用户信息失败，请稍后再试')
    })

  })
</script>

<template>
  <!-- 账号安全卡片 -->
  <el-card shadow="hover">
    <template #header>
      <div class="flex justify-between items-center">
        <span>账号安全</span>
        <el-button type="text" size="small" @click="changePassword">
          修改密码
        </el-button>
      </div>
    </template>

    <div class="space-y-4">
      <div class="flex items-center p-4 border-b border-gray-100">
        <i class="fa-solid fa-lock text-primary mr-4"></i>
        <div class="flex-1">
          <div class="font-medium">密码</div>
          <div class="text-sm text-gray-500">上次修改: {{ userInfo.passwordLastModified }}</div>
        </div>
        <el-tag type="success">已设置</el-tag>
      </div>

      <div class="flex items-center p-4 border-b border-gray-100">
        <i class="fa-solid fa-envelope text-primary mr-4"></i>
        <div class="flex-1">
          <div class="font-medium">邮箱验证</div>
          <div class="text-sm text-gray-500">
            {{ userInfo.email ? userInfo.email.replace(/^(.{2}).+(@.+)$/, '$1****$2') : '未绑定' }}
          </div>
        </div>
        <el-button
            size="mini"
            type="text"
            @click="bindEmail"
        >
          {{ userInfo.email ? '更换' : '绑定' }}
        </el-button>
      </div>

    </div>
  </el-card>

  <!-- 修改密码弹窗 -->
  <el-dialog
      title="修改密码"
      v-model="passwordDialogVisible"
      width="30%"
      @close="resetPasswordForm"
  >
    <el-form :model="passwordForm" label-width="100px">
      <el-form-item label="当前密码" prop="oldPassword">
        <el-input v-model="passwordForm.oldPassword" type="password" />
      </el-form-item>
      <el-form-item label="新密码" prop="newPassword">
        <el-input v-model="passwordForm.newPassword" type="password" />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input v-model="passwordForm.confirmPassword" type="password" />
      </el-form-item>
    </el-form>

    <template #footer>
        <span class="dialog-footer">
          <el-button @click="passwordDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitPassword">确认修改</el-button>
        </span>
    </template>
  </el-dialog>


  <!-- 绑定邮箱弹窗 -->
  <el-dialog
      :title="emailDialogTitle"
      v-model="emailDialogVisible"
      width="30%"
      @close="resetEmailForm"
  >
    <el-form :model="emailForm" label-width="100px">
      <el-form-item label="邮箱地址" prop="email">
        <el-input v-model="emailForm.email" placeholder="请输入邮箱地址" />
      </el-form-item>
      <el-form-item label="验证码" prop="code">
        <el-input
            v-model="emailForm.code"
            placeholder="请输入验证码"
            suffix-icon="el-icon-message"
            style="width: 70%"
        >
        </el-input>
        <el-button
            size="small"
            @click="sendEmailCode"
            :disabled="countdown > 0"
            style="margin: auto"
        >
          {{ countdown > 0 ? `${countdown}s后重试` : '获取验证码' }}
        </el-button>
      </el-form-item>
    </el-form>
    <template #footer>
        <span class="dialog-footer">
          <el-button @click="emailDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEmail">确认{{ userInfo.email ? '更换' : '绑定' }}</el-button>
        </span>
    </template>
  </el-dialog>

</template>

<style scoped>
.user-profile-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.el-avatar {
  border: 2px solid #EBEEF5;
}

.el-card {
  margin-bottom: 20px;
}

.el-form-item {
  margin-bottom: 16px;
}

.el-dialog__body {
  padding: 20px 30px;
}

/* 自定义样式 */
.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.avatar-uploader .el-upload:hover {
  border-color: #409EFF;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  line-height: 178px;
  text-align: center;
}

.avatar {
  width: 178px;
  height: 178px;
  display: block;
}
</style>
