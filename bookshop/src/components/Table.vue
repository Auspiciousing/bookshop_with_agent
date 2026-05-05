<template>
  <el-button type="primary" @click="openDialog">新建售卖</el-button>
  <div class="container">

    <!-- 表格组件 -->
    <el-table
        :data="currentTableData"
        border

        style="width: 100%;"
        :cell-style="{ textAlign: 'center' }"
        :header-cell-style="{ textAlign: 'center' }"
        height="700"

    >
      <template #empty>
        <el-empty description="暂无售卖数据" />
      </template>
      <el-table-column prop="id" label="ID" width="100" />
      <el-table-column prop="title" label="书名" width="120" />
      <el-table-column prop="author" label="作者" width="200" />
      <el-table-column prop="publisher" label="出版社" />
      <el-table-column prop="description" label="描述" width="300" />
      <el-table-column prop="price" label="价格" width="80" />
      <el-table-column prop="stock" label="库存" width="80" />
      <el-table-column label="参考图片" width="200">
        <template #default="scope">
          <img v-if="scope.row.picture_url" :src="scope.row.picture_url" class="avatar-image" />

          <el-icon v-else class="placeholder-icon"><Picture /></el-icon>

        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="scope">
          <el-button size="small" type="primary" @click="editBook(scope.row)">修改</el-button>
          <el-button size="small" type="danger" @click="deleteBook(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新建售卖对话框 -->
    <el-dialog v-model="newBookDialog" title="新建售卖" width="500px">
      <el-form :model="newBookForm" label-width="100px" :rules="rules" ref="formRef">
        <el-form-item label="书名" prop="title">
          <el-input v-model="newBookForm.title" placeholder="请输入书名"></el-input>
        </el-form-item>
        <el-form-item label="作者" prop="author">
          <el-input v-model="newBookForm.author" placeholder="请输入作者"></el-input>
        </el-form-item>
        <el-form-item label="出版社" prop="publisher">
          <el-input v-model="newBookForm.publisher" placeholder="请输入出版社"></el-input>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="newBookForm.description" type="textarea" rows="3" placeholder="请输入图书描述"></el-input>
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="newBookForm.price" :precision="2" :step="0.1" :min="0"></el-input-number>
        </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="newBookForm.stock" :min="0" :step="1"></el-input-number>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelNewBook">取消</el-button>
          <el-button type="primary" @click="submitNewBook">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑售卖对话框 -->
    <el-dialog v-model="editBookDialog" title="编辑售卖" width="500px">
      <el-form :model="editingBookForm" label-width="100px" :rules="rules" ref="editFormRef">
        <el-form-item label="书名" prop="title">
          <el-input v-model="editingBookForm.title" placeholder="请输入书名"></el-input>
        </el-form-item>
        <el-form-item label="作者" prop="author">
          <el-input v-model="editingBookForm.author" placeholder="请输入作者"></el-input>
        </el-form-item>
        <el-form-item label="出版社" prop="publisher">
          <el-input v-model="editingBookForm.publisher" placeholder="请输入出版社"></el-input>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="editingBookForm.description" type="textarea" rows="3" placeholder="请输入图书描述"></el-input>
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="editingBookForm.price" :precision="2" :step="0.1" :min="0"></el-input-number>
        </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="editingBookForm.stock" :min="0" :step="1"></el-input-number>
        </el-form-item>
        <el-form-item label="图片" prop="picture_url">
          <el-upload
              class="avatar-uploader"
              :show-file-list="false"
              :before-upload="beforeEditBookImageUpload"
          >
            <img v-if="editingBookForm.picture_url" :src="editingBookForm.picture_url" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelEdit">取消</el-button>
          <el-button type="primary" @click="submitEdit">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="dialog" title="图片裁剪" width="800">
      <!-- 裁剪器组件 -->
      <vue-cropper
          ref="cropperRef"
          :img="url"
          :outputSize="1"
          :outputType="'jpeg'"
          :info="true"
          :canMove="true"
          :canMoveBox="true"
          :original="true"
          :autoCrop="true"
          :autoCropWidth="200"
          :autoCropHeight="200"
          :fixed="true"
          :fixedNumber="[1, 1]"
          :full="false"
          :fixedBox="true"
          style="height: 400px;width: 400px"
      />
      <div style="display: flex;margin-top: 10px">
        <el-button @click="cancelCrop">取消</el-button>
        <el-button @click="upload">确认上传</el-button>
      </div>
    </el-dialog>

    <el-dialog v-model="dialog2" title="裁剪成功" width="600">
      <img :src="imageurl" alt="">
      <br>
      <el-button @click="uploadImage(imageurl)">确认</el-button>
    </el-dialog>

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
    />
  </div>
</template>

<script lang="ts" setup>
import {ref, computed, reactive, onMounted} from 'vue'
import { ElIcon, ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Picture } from '@element-plus/icons-vue'
import type { UploadProps, FormInstance, FormRules } from 'element-plus'
import { VueCropper } from "vue-cropper"
import 'element-plus/dist/index.css'
import api from "@/api/index.js";

// 表格相关数据
const fileLists = reactive([]);
const cropperRef = ref(null);
const cropper_width = ref(0); // 真实的输出图片宽度
const cropper_height = ref(0); // 真实的输出图片高度
const imageurl = ref();
const formRef = ref<FormInstance>();
const editFormRef = ref<FormInstance>();

// 新建图书相关
const newBookDialog = ref(false);
const newBookForm = reactive({
  title: '',
  author: '',
  publisher: '',
  description: '',
  price: 0,
  stock: 0,
  imageurl: ''
});

// 编辑图书相关
const editBookDialog = ref(false);
const editingBookForm = reactive({
  id: 0,
  title: '',
  author: '',
  publisher: '',
  description: '',
  price: 0,
  stock: 0,
  imageurl: ''
});
const editingIndex = ref(-1);
const id = ref();

// 图片上传状态标记
const isNewBookImage = ref(false);
const isEditBookImage = ref(false);

// 表单验证规则
const rules = reactive<FormRules>({
  title: [{ required: true, message: '请输入书名', trigger: 'blur' }],
  author: [{ required: true, message: '请输入作者', trigger: 'blur' }],
  publisher: [{ required: true, message: '请输入出版社', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  stock: [{ required: true, message: '请输入库存', trigger: 'blur' }]
});

// 打开新建售卖对话框
const openDialog = () => {
  id.value=null;
  newBookDialog.value = true;
};

// 取消新建售卖
const cancelNewBook = () => {
  resetForm();
  newBookDialog.value = false;
};

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields();
  }
  newBookForm.imageurl = '';
};

// 提交新建售卖
const submitNewBook = async () => {
  if (!formRef.value) return;

  await formRef.value.validate((valid) => {
    if (valid) {

      // 创建新的书籍对象
      const newBook = {
        title: newBookForm.title,
        author: newBookForm.author,
        publisher: newBookForm.publisher,
        description: newBookForm.description,
        price: newBookForm.price,
        stock: newBookForm.stock,
        imageurl: newBookForm.imageurl,
      };

      api.postBookNew(newBook).then(res => {
        if (res.data.code === 200) {
          console.log("新书添加成功", res.data);

          api.getSellBookSelf().then(res => {
            if (res.data.code === 200) {
              allTableData.value = res.data.books_data;
              total.value = allTableData.value.length;
              ElMessage.success('新书添加成功');
              newBookDialog.value = false;
              resetForm();
            }
          })

        } else {
          ElMessage.error('新书添加失败，请稍后再试');
          return;
        }
      }).catch(err => {
        console.error(err);
        ElMessage.error('网络问题，新书添加失败，请稍后再试');
      });
    } else {
      ElMessage.error('请填写必填字段');
      return false;
    }
  });
};

// 编辑图书
const editBook = (row) => {
  // 深拷贝要编辑的图书对象
  Object.assign(editingBookForm, JSON.parse(JSON.stringify(row)));
  id.value = row.id;
  editBookDialog.value = true;

  // 找出当前图书在数组中的索引，用于后续更新
  editingIndex.value = allTableData.value.findIndex(item => item.id === row.id);
};

// 取消编辑
const cancelEdit = () => {
  editBookDialog.value = false;
  if (editFormRef.value) {
    editFormRef.value.resetFields();
  }
};

// 提交编辑
const submitEdit = async () => {
  if (!editFormRef.value) return;

  if (editingIndex.value > -1) {
    console.log("编辑的图书ID", editingBookForm);
    api.postBookModify(editingBookForm).then(res => {
      if (res.data.code === 200) {
        console.log("图书修改成功", res.data);
        api.getSellBookSelf().then(res => {
          if (res.data.code === 200) {
            allTableData.value = res.data.books_data;
            total.value = allTableData.value.length;
            ElMessage.success('图书修改成功');
            editBookDialog.value = false;
            resetForm();
          }
        })
      } else {
        ElMessage.error('图书修改失败，请稍后再试');
        return;
      }
    }).catch(err => {
      console.error(err);
      ElMessage.error('网络问题，图书修改失败，请稍后再试');
    });

  } else {
    ElMessage.error('请填写必填字段');
    return false;
  }

  await editFormRef.value.validate((valid) => {

  });
};

// 删除图书
const deleteBook = (row) => {
  api.deleteBookDelete(row.id).then(res => {
    if (res.data.code === 200) {
      console.log("图书删除成功", res.data);
      api.getSellBookSelf().then(res => {
        if (res.data.code === 200) {
          allTableData.value = res.data.books_data;
          total.value = allTableData.value.length;
          ElMessage.success('图书删除成功');
        }
      })
    } else {
      console.log(res.data.code)
      console.log(res.data.message)
      ElMessage.error('图书删除失败，请稍后再试');
      return;
    }
  }).catch(err => {
    console.error(err);
    ElMessage.error('网络问题，图书删除失败，请稍后再试');
  });
  // ElMessageBox.confirm('确定要删除这本书吗?', '提示', {
  //   confirmButtonText: '确定',
  //   cancelButtonText: '取消',
  //   type: 'warning'
  // }).then(() => {
  //   // 在数组中找到并删除
  //   const index = allTableData.value.findIndex(item => item.id === row.id);
  //   if (index > -1) {
  //     allTableData.value.splice(index, 1);
  //     total.value = allTableData.value.length;
  //     ElMessage.success('删除成功');
  //   }
  // }).catch(() => {
  //   // 取消删除操作
  // });
};

// 新书图片上传前的处理
const beforeNewBookImageUpload: UploadProps['beforeUpload'] = (rawFile) => {
  if (rawFile.type !== 'image/jpeg' && rawFile.type !== 'image/png') {
    ElMessage.error('图片必须是JPG或PNG格式!')
    return false
  } else if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error('图片大小不能超过2MB!')
    return false
  }

  // 将文件转换为Base64
  const reader = new FileReader();
  reader.onload = (e) => {
    url.value = e.target.result;
    isNewBookImage.value = true;
    isEditBookImage.value = false;
  };
  reader.readAsDataURL(rawFile);
  dialog.value = true;

  return false; // 阻止自动上传
};

// 编辑时上传图片处理
const beforeEditBookImageUpload: UploadProps['beforeUpload'] = (rawFile) => {
  if (rawFile.type !== 'image/jpeg' && rawFile.type !== 'image/png') {
    ElMessage.error('图片必须是JPG或PNG格式!')
    return false
  } else if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error('图片大小不能超过2MB!')
    return false
  }

  // 将文件转换为Base64
  const reader = new FileReader();
  reader.onload = (e) => {
    url.value = e.target.result;
    isNewBookImage.value = false;
    isEditBookImage.value = true;
  };
  reader.readAsDataURL(rawFile);
  dialog.value = true;

  return false; // 阻止自动上传
};

// 取消裁剪
const cancelCrop = () => {
  dialog.value = false;
  isNewBookImage.value = false;
  isEditBookImage.value = false;
};

const state = reactive({
  croppedImageUrl: ""
});

const upload = () => {
  getCropImg();
};

const getCropImg = () => {
  if (!cropperRef.value) {
    console.error('Cropper组件未正确加载')
    return
  }
  // 使用ref获取cropper实例并调用getCropImage方法
  cropperRef.value.getCropData(async (data) => {
    // 获取真实输出的图片宽高
    const img = new Image();
    img.onload = () => {
      cropper_width.value = img.width;
      cropper_height.value = img.height;
    };
    img.src = data;
    imageurl.value = data;
    setTimeout(() => {
      dialog.value = false;
      dialog2.value = true;
    }, 300);
  });
};

const preview = (img) => {
  const html = `<div><img src="${img}" alt=""/>
 <div class="cropper_img_size">${cropper_width.value}x${cropper_height.value}</div></div>`
  ElMessageBox.alert(html,
      "截图成功",
      {
        dangerouslyUseHTMLString: true,
        confirmButtonText: "确定",
      }
  ).then((action) => {
    // 当点击确定按钮时，action 的值为 'confirm'
    if (action === 'confirm') {
      // 执行你想要的操作，例如上传图片
      uploadImage(img);
    }
  }).catch(() => {
    // 点击取消或关闭弹窗时执行
  });
};

// 将DataURL转换为Blob对象
const dataURLtoBlob = (dataURL) => {
  const arr = dataURL.split(',');
  const mime = arr[0].match(/:(.*?);/)[1];
  const bstr = atob(arr[1]);
  let n = bstr.length;
  const u8arr = new Uint8Array(n);

  while (n--) {
    u8arr[n] = bstr.charCodeAt(n);
  }

  return new Blob([u8arr], { type: mime });
};

// 创建FormData并上传
const uploadImage = async (imageUrl) => {

    // 转换为Blob
    const imageBlob = dataURLtoBlob(imageUrl);

    console.log("你好",imageBlob)
    // 创建FormData，字段名必须为"file"（与后端API一致）
    const formData = new FormData();
    formData.append('id', id.value);
    formData.append('file', imageBlob, 'cropped_image.jpg');

    console.log("方法外",formData.get('id'))
    console.log("方法外",formData.get('file'))
    console.log("发送请求")
    // 发送请求到后端
    api.postBookUpload(formData).then(res => {
      console.log("进入方法发送")
      if (res.data.code === 200) {
        console.log("url", res.data.url);
        // 处理不同上传场景
        if (isNewBookImage.value) {
          newBookForm.picture_url = res.data.data.url;
          isNewBookImage.value = false;
        } else if (isEditBookImage.value) {
          editingBookForm.picture_url = res.data.data.url;
          isEditBookImage.value = false;
        }
        // console.log(id.value)
        // allTableData.value.find(item => item.id === id.value).picture_url = res.data.url;
        // console.log("啊啊啊啊啊啊啊",allTableData.value)

        dialog2.value = false;
        ElMessage({
          showClose: true,
          message: '上传成功',
          type: 'success',
        })
        console.log("上传成功")
      } else {
        ElMessage.error('上传失败')
      }
    }).catch(err => {
      console.error(err);
      ElMessage.error('网络问题，图片上传失败，请稍后再试');
    });


};

// 模拟全部数据
const allTableData = ref([

]);

const url = ref();
const dialog = ref(false);
const dialog2 = ref(false);

// 分页相关参数
const currentPage = ref(1); // 当前页码
const pageSize = ref(5);    // 每页显示数量
const total = ref(allTableData.value.length); // 数据总数

// 计算当前页要显示的数据
const currentTableData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return allTableData.value.slice(start, end);
});

// 每页数量变化时的回调
const handleSizeChange = (newSize) => {
  pageSize.value = newSize;
  currentPage.value = 1; // 重置页码为第一页
};

// 当前页码变化时的回调
const handleCurrentChange = (newPage) => {
  currentPage.value = newPage;
};

onMounted(() => {
  api.getSellBookSelf().then(res => {
    if (res.data.code === 200) {
      allTableData.value = res.data.books_data;
      console.log(allTableData.value)
      total.value = allTableData.value.length;
      ElMessage.success('获取数据成功');
    } else {
      ElMessage.error('获取数据失败，请稍后再试');
    }
  }).catch(err => {
    console.error(err);
    ElMessage.error('网络问题，获取数据失败，请稍后再试');
  });
});
</script>

<style scoped>
.container {
  overflow-y: auto;
  height: 800px;
  margin: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.avatar-uploader .avatar {
  width: 178px;
  height: 178px;
  display: block;
}
.image-container {
  width: 100%;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.avatar-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.avatar-image:hover {
  transform: scale(1.1);
}
</style>

<style>
.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.el-icon.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
}
.placeholder-icon {
  font-size: 36px;
  color: #909399;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 200px;
}
</style>


