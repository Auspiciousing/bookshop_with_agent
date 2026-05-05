import {ref, computed, reactive} from 'vue'
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)

  let openeds=reactive([''])

  const userInfo = reactive({
    id: null,
    username: '',
    nickname: '',
    avatar: '',
    gender: '',
    phone: '',
    email: '',
    birthday: '',
    bio: '',
    passwordLastModified: '',
  })
  const doubleCount = computed(() => count.value * 2)
  const carproducts = reactive([
    { id: 1, name: '商品1', price: 10, imageUrl: 'https://picsum.photos/200/200?random=11', loaded: false, checked: false },
    { id: 2, name: '商品2', price: 20, imageUrl: 'https://picsum.photos/200/200?random=12', loaded: false, checked: false }
  ]);

  const payproducts = reactive([
    { id: 1, name: '商品1', price: 10, imageUrl: 'https://picsum.photos/200/200?random=11', loaded: false, checked: false,time:"10" },
    { id: 2, name: '商品2', price: 20, imageUrl: 'https://picsum.photos/200/200?random=12', loaded: false, checked: false,time:10 },
    { id: 3, name: '商品3', price: 10, imageUrl: 'https://picsum.photos/200/200?random=11', loaded: false, checked: false,time:10 },
    { id: 4, name: '商品2', price: 20, imageUrl: 'https://picsum.photos/200/200?random=12', loaded: false, checked: false,time:10 },
  ]);

  const deliveringproducts = reactive([
    { id: 1, name: '商品1', price: 10, imageUrl: 'https://picsum.photos/200/200?random=11', loaded: false, checked: false },
    { id: 2, name: '商品2', price: 20, imageUrl: 'https://picsum.photos/200/200?random=12', loaded: false, checked: false },
    { id: 3, name: '商品4', price: 10, imageUrl: 'https://picsum.photos/200/200?random=11', loaded: false, checked: false },
    { id: 4, name: '商品2', price: 20, imageUrl: 'https://picsum.photos/200/200?random=12', loaded: false, checked: false },
  ]);

  const deliveredproducts = reactive([
    { id: 1, name: '商品1', price: 10, imageUrl: 'https://picsum.photos/200/200?random=11', loaded: false, checked: false },
    { id: 2, name: '商品2', price: 20, imageUrl: 'https://picsum.photos/200/200?random=12', loaded: false, checked: false },
    { id: 3, name: '商品5', price: 10, imageUrl: 'https://picsum.photos/200/200?random=11', loaded: false, checked: false },
    { id: 4, name: '商品2', price: 20, imageUrl: 'https://picsum.photos/200/200?random=12', loaded: false, checked: false },
  ]);

  const products = ref([
    {id: 1, name: '商品1', imageUrl: 'https://picsum.photos/200/200?random=1', price: 10, loaded: false},
    {id: 2, name: '商品2', imageUrl: 'https://picsum.photos/200/200?random=2', price: 20, loaded: false},
    {id: 3, name: '商品3', imageUrl: 'https://picsum.photos/200/200?random=3', price: 30, loaded: false},
    {id: 4, name: '商品4', imageUrl: 'https://picsum.photos/200/200?random=4', price: 40, loaded: false},
    {id: 5, name: '商品5', imageUrl: 'https://picsum.photos/200/200?random=5', price: 50, loaded: false},
    {id: 6, name: '商品6', imageUrl: 'https://picsum.photos/200/200?random=6', price: 60, loaded: false},
    {id: 7, name: '商品7', imageUrl: 'https://picsum.photos/200/200?random=7', price: 70, loaded: false},
    {id: 8, name: '商品8', imageUrl: 'https://picsum.photos/200/200?random=8', price: 80, loaded: false},
    {id: 9, name: '商品5', imageUrl: 'https://picsum.photos/200/200?random=9', price: 50, loaded: false},
    {id: 10, name: '商品6', imageUrl: 'https://picsum.photos/200/200?random=10', price: 60, loaded: false},
    {id: 11, name: '商品7', imageUrl: 'https://picsum.photos/200/200?random=11', price: 70, loaded: false},
    {id: 12, name: '商品8', imageUrl: 'https://picsum.photos/200/200?random=12', price: 80, loaded: false},
    {id: 13, name: '商品5', imageUrl: 'https://picsum.photos/200/200?random=13', price: 50, loaded: false},
    {id: 14, name: '商品6', imageUrl: 'https://picsum.photos/200/200?random=14', price: 60, loaded: false},
    {id: 15, name: '商品7', imageUrl: 'https://picsum.photos/200/200?random=15', price: 70, loaded: false},
    {id: 16, name: '商品8', imageUrl: 'https://picsum.photos/200/200?random=16', price: 80, loaded: false},
    {id: 17, name: '商品5', imageUrl: 'https://picsum.photos/200/200?random=17', price: 50, loaded: false},
    {id: 18, name: '商品6', imageUrl: 'https://picsum.photos/200/200?random=18', price: 60, loaded: false},
    {id: 19, name: '商品7', imageUrl: 'https://picsum.photos/200/200?random=19', price: 70, loaded: false},
    {id: 20, name: '商品8', imageUrl: 'https://picsum.photos/200/200?random=20', price: 80, loaded: false},
    {id: 21, name: '商品5', imageUrl: 'https://picsum.photos/200/200?random=21', price: 50, loaded: false},
    {id: 22, name: '商品6', imageUrl: 'https://picsum.photos/200/200?random=22', price: 60, loaded: false},
    {id: 23, name: '商品7', imageUrl: 'https://picsum.photos/200/200?random=23', price: 70, loaded: false},
    {id: 24, name: '商品8', imageUrl: 'https://picsum.photos/200/200?random=24', price: 80, loaded: false},
    {id: 25, name: '商品5', imageUrl: 'https://picsum.photos/200/200?random=25', price: 50, loaded: false},
    {id: 26, name: '商品6', imageUrl: 'https://picsum.photos/200/200?random=26', price: 60, loaded: false},
    {id: 27, name: '商品7', imageUrl: 'https://picsum.photos/200/200?random=27', price: 70, loaded: false},
    {id: 28, name: '商品8', imageUrl: 'https://picsum.photos/200/200?random=28', price: 80, loaded: false}
  ]);

  // 更新商品选中状态
  const updateProductSelection = (updatedProducts) => {
    products.value = updatedProducts;
  };

  function increment() {
    count.value++
  }
  function modifyopends(){
    if (openeds === ['4'])
      openeds=[''];
    else
      openeds=['4'];
  }

  return { count, userInfo, doubleCount,openeds, carproducts,payproducts,deliveringproducts,deliveredproducts,products,updateProductSelection,increment, modifyopends}
})
