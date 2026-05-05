import { ref, computed } from 'vue'

export function useCart() {
    const cartItems = ref([])

    const addToCart = (product) => {
        const existingItem = cartItems.value.find(item => item.id === product.id)
        if (existingItem) {
            existingItem.quantity++
        } else {
            cartItems.value.push({ ...product, quantity: 1 })
        }
    }

    const removeFromCart = (item) => {
        const index = cartItems.value.findIndex(cartItem => cartItem.id === item.id)
        if (index!== -1) {
            cartItems.value.splice(index, 1)
        }
    }

    const totalPrice = computed(() => {
        return cartItems.value.reduce((total, item) => {
            return total + item.price * item.quantity
        }, 0)
    })

    return {
        cartItems,
        addToCart,
        removeFromCart,
        totalPrice
    }
}
