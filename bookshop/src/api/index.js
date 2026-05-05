import path from "./path"
import axios from "../utils/request"
export default {
    postLogin(username,password){
        console.log("方法调用")
        return axios.post(path.baseUrl +path.login,{username:username,password:password})
    },

    postRegister(username,password){
        return axios.post(path.baseUrl +path.register,{username:username,password:password})
    },

    postChange_password(userid,old_password,new_password){
        return axios.post(path.baseUrl+path.change_password,{userid:userid,old_password:old_password,new_password:new_password})
    },

    getAccount(){
        return axios.get(path.baseUrl+path.account)
    },

    getSelf(){
        return axios.get(path.baseUrl+path.self)
    },

    postSelf(userInfo){
        return axios.post(path.baseUrl+path.self,{
            username:userInfo.username,
            nickname:userInfo.nickname,
            avatar_url:userInfo.avatar,
            gender:userInfo.gender,
            birthday:userInfo.birthday,
            phone:userInfo.phone,
            email:userInfo.email,
            address:userInfo.address,
            self_statement:userInfo.self_statement,
        })
    },

    postEmail(email){
        return axios.post(path.baseUrl+path.email,{email})
    },

    postEmailVerify(email,verify_code){
        return axios.post(path.baseUrl+path.emailVerify,{email:email,verification_code:verify_code})
    },

    postBookNew(book){
        return axios.post(path.baseUrl+path.bookNew,{
            title: book.title,
            author:book.author,
            publisher: book.publisher,
            description: book.description,
            price: book.price,
            stock: book.stock,
            picture_url: book.imageurl,
        })
    },

    postBookModify(book){
        return axios.post(path.baseUrl+path.bookModify,{
            id: book.id,
            title: book.title,
            author: book.author,
            publisher: book.publisher,
            description: book.description,
            price: book.price,
            stock: book.stock,
            picture_url: book.picture_url
        })
    },

    getSellBookSelf(){
        return axios.get(path.baseUrl+path.sellBookSelf)
    },

    postBookUpload(formData){
        console.log("上传图片")
        console.log("方法内",formData)
        console.log("方法外",formData.get('id'))
        console.log("方法外",formData.get('file'))
        return axios.post(path.baseUrl+path.bookUpload, formData)
    },

    deleteBookDelete(id){
        console.log("id:",id)
        return axios.delete(path.baseUrl+path.bookDelete,{params:{id:id}})
    },

    getBookShop(){
        console.log("getbookshop")
        return axios.get(path.baseUrl+path.bookShop)
    },

    getBookShopAppend(){
        return axios.get(path.baseUrl+path.bookShopAppend)
    },

    postBookAddToCar(bookId,bookNum){
        return axios.post(path.baseUrl+path.bookAddToCar,{
            book_id:bookId,
            book_num:bookNum
        })
    },

    getBookCar(){
        return axios.get(path.baseUrl+path.bookCar)
    },

    postReturnBookCar(books){
        console.log("方法内：",books)
        return axios.post(path.baseUrl+path.returnBookCar,books)
    },

    deleteBookCarDelete(id_list){
        console.log("id:",id_list)
        return axios.post(path.baseUrl+path.bookCarDelete,id_list)
    },

    postOrderNew(list){
        console.log("你好啊啊")
        return axios.post(path.baseUrl+path.orderNew,list)
    },

    getOrderUnpaid(){
        return axios.get(path.baseUrl+path.orderUnpaid)
    },

    deleteOrder(id){
        console.log("id:",id)
        return axios.delete(path.baseUrl+path.orderDelete,{params:{id:id}})
    },

    postBookSearch(search){
        return axios.post(path.baseUrl+path.bookSearch,{search:search})
    },

    postBookBlurSearch(search){
        return axios.post(path.baseUrl+path.bookBlurSearch,{search:search})
    },

    getMoney(){
        return axios.get(path.baseUrl+path.Money)
    },

    postRecharge(money){
        return axios.post(path.baseUrl+path.recharge,{money:money})
    },

    postPay(order_id){
        return axios.post(path.baseUrl+path.pay,{order_id:order_id})
    },

    getShippingBook(){
        return axios.get(path.baseUrl+path.shippingBook)
    },

    postConfirmReceipt(order_id){
        return axios.post(path.baseUrl+path.confirmReceipt,{id:order_id})
    },

    getCompletedBook(){
        return axios.get(path.baseUrl+path.completedBook)
    },

    postAvatar(formData){
        return axios.post(path.baseUrl+path.postAvatar, formData)
    }
}
