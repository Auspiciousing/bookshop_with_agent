<template>
  <div class="user-profile-container">
    <!-- 页面标题 -->
<!--    <div class="text-center mb-8">-->
<!--      <h1 class="text-2xl font-bold text-gray-800">个人资料</h1>-->
<!--    </div>-->

    <!-- 基本资料卡片 -->
    <el-card class="mb-6" shadow="hover">
      <el-form :model="userInfo" label-width="120px">
        <!-- 头像上传 -->
        <el-form-item label="头像">
          <div class="flex items-center justify-center">
            <el-avatar
                :size="120"
                :src="userInfo.avatar || 'https://picsum.photos/200/200'"
                shape="circle"
            ></el-avatar>
            <el-upload
                class="ml-6"
                action="#"
                :show-file-list="false"
                :before-upload="beforeAvatarUpload"
                @success="handleAvatarSuccess"
            >
              <el-button size="small" type="primary" >
                更换头像
              </el-button>
            </el-upload>
          </div>
        </el-form-item>

        <!-- 裁剪弹窗 -->
        <el-dialog v-model="showCropper" title="裁剪头像" width="400px">
          <div v-if="imgSrc" class="cropper-container">
            
            <VueCropper
                ref="cropperRef"
                :img="imgSrc"
                :outputSize="1"
                :outputType="'jpeg'"
                :info="true"
                :canMove="true"
                :canMoveBox="false"
                :original="true"
                :autoCrop="true"
                :autoCropWidth="200"
                :autoCropHeight="200"
                :fixed="true"
                :fixedNumber="[1, 1]"
                :full="false"
                :fixedBox="true"
                :mode="'200px'"
                :centerBox="true"
                style="height: 400px;width: auto;align-items: center;display: flex;justify-items: center"
            />
          </div>
          <template #footer>
            <el-button @click="cancelCrop">取消</el-button>
            <el-button type="primary" @click="cropAndUpload">确定</el-button>
          </template>
        </el-dialog>

        <!-- 个人信息 -->
        <el-form-item label="用户名">
          <el-input v-model="userInfo.username" disabled />
        </el-form-item>

        <el-form-item label="昵称">
          <el-input v-model="userInfo.nickname" />
        </el-form-item>

        <el-form-item label="性别">
          <el-radio-group v-model="userInfo.gender">
            <el-radio label="male">男</el-radio>
            <el-radio label="female">女</el-radio>
            <el-radio label="unknown">保密</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="手机号码">
          <el-input v-model="userInfo.phone" placeholder="请输入手机号码" />
        </el-form-item>

        <el-form-item label="邮箱">
          <el-input v-model="userInfo.email" placeholder="请输入邮箱" disabled/>
        </el-form-item>

        <el-form-item label="出生日期">
          <el-date-picker
              v-model="userInfo.birthday"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
          >
          </el-date-picker>
        </el-form-item>

        <el-form-item label="收货地址">
          <el-input v-model="userInfo.address" placeholder="请输入地址" />
        </el-form-item>

        <el-form-item label="个人简介">
          <el-input
              v-model="userInfo.self_statement"
              type="textarea"
              :rows="4"
              placeholder="请输入个人简介"
          ></el-input>
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item class="text-center mt-6">
          <el-button type="primary" @click="saveProfile">
            保存修改
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>


  </div>
</template>

<script setup>
import { ref, reactive, toRefs, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from "@/api/index.js";
import 'element-plus/dist/index.css';
import {VueCropper} from "vue-cropper";
const showCropper = ref(false)
const imgSrc = ref('')

const cancelCrop = () => {
  showCropper.value = false
  imgSrc.value = ''
}

const cropAndUpload = () => {
  if (!cropperRef.value) {
    ElMessage.warning('裁剪器未初始化')
    return
  }

  // 获取裁剪后的图片blob
  cropperRef.value.getCropBlob(blob => {
    // 更新头像URL
    userInfo.avatar = URL.createObjectURL(blob)

    // 这里可以将裁剪后的图片上传到服务器
    // 可以使用FormData来发送blob数据
    const formData = new FormData()
    formData.append('avatar', blob, 'avatar.png')

    // 模拟上传成功
    ElMessage.success('头像已裁剪并更新')
    showCropper.value = false

    // 实际项目中这里应该调用上传API
    // api.uploadAvatar(formData).then(...)
    api.postAvatar(formData).then(res => {
      if (res.data.code === 200) {
        ElMessage.success('头像上传成功')
      } else {
        ElMessage.error('头像上传失败，请稍后再试')
      }
    }).catch(err => {
      console.error(err)
      ElMessage.error('网络错误，头像上传失败，请稍后再试')
    })
  })
}

const cropperRef = ref(null)

// 用户信息
const userInfo = reactive({
  username: '',
  nickname: '',
  avatar: '',
  gender: '',
  phone: '',
  email: '',
  birthday: '',
  address:'',
  self_statement: '这是一个用户的个人简介',
})


// 表单原始数据（用于重置）
const originalUserInfo = JSON.parse(JSON.stringify(userInfo))

// 保存个人资料
const saveProfile = () => {
  // 这里可以添加表单验证逻辑
  api.postSelf(userInfo).then(res => {
    if (res.data.code === 200) {
      ElMessage.success('个人资料更新成功')
    } else {
      ElMessage.error('个人资料更新失败，请稍后再试')
    }
  }).catch(err => {
    console.error(err)
    ElMessage.error('网络错误，个人资料更新失败，请稍后再试')
  })
  // 实际项目中这里应该调用API保存数据
}

// 重置个人资料表单
const resetProfile = () => {
  Object.assign(userInfo, originalUserInfo)
}

// 上传头像
const beforeAvatarUpload = (file) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
  if (!isJPG) {
    ElMessage.error('请上传JPG/PNG格式的图片')
    return false
  }
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过2MB')
    return false
  }
  // 设置裁剪图片源并显示裁剪弹窗
  imgSrc.value = URL.createObjectURL(file)
  showCropper.value = true

  // 返回false阻止默认上传行为
  return false
}

// 处理头像上传成功
const handleAvatarSuccess = (response, file, fileList) => {
  // 实际项目中这里应该处理上传成功后的响应
  ElMessage.success('头像更新成功')
  userInfo.avatar = URL.createObjectURL(file.raw)
}


onMounted(() => {
  api.getSelf().then(res => {
    if (res.data.code === 200) {
      userInfo.username = res.data.username
      userInfo.nickname = res.data.nickname
      userInfo.avatar = res.data.avatar_url
      userInfo.gender = res.data.gender
      userInfo.phone = res.data.phone
      userInfo.email = res.data.email
      userInfo.birthday = res.data.birthday
      userInfo.address = res.data.address
      userInfo.self_statement = res.data.self_statement
      ElMessage.success('获取用户信息成功')
    }else {
      ElMessage.error('获取用户信息失败，请稍后再试')
    }
  }).catch(err => {
    console.error(err)
    ElMessage.error('获取用户信息失败，请稍后再试')
  })
})
</script>

<style scoped>
.circle-mask {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 200px;
  height: 200px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 0 400px rgba(0, 0, 0, 0.5); /* 修改遮罩范围 */
  z-index: 100;
  pointer-events: none;
}

.user-profile-container {
  max-width: 800px;
  margin: 0;
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

.cropper-container {
  position: relative;
  width: auto;
  height: 400px;
  overflow: hidden; /* 限制遮罩效果在容器内 */
}
</style>
