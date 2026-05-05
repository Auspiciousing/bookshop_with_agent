<template>
  <div>
    <h2>商品列表</h2>
    <el-card v-for="product in products" :key="product.id" :body-style="{ padding: '10px' }">
      <template #header>
        <div>{{ product.name }}</div>
      </template>
      <p>价格: ${{ product.price }}</p>
      <el-button @click="addToCart(product)">加入购物车</el-button>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useCart } from '@/composables/useCart'

const products = ref([
  {id: 1, name: '商品1', price: 10},
  {id: 2, name: '商品2', price: 20},
  {id: 3, name: '商品3', price: 30},
  {id: 4, name: '商品4', price: 40},
  {id: 5, name: '商品5', price: 50},
])

const {addToCart} = useCart()
</script>
