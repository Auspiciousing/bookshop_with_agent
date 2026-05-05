import axios, {Axios} from "axios"
import qs from "querystring"

const instance = axios.create({
    timeout:5000
})

const errorHandle = (status,info) => {
    switch(status){
        case 400:
            console.log("400：语义有误，服务器无法理解请求。");
            break;
        case 401:
            console.log("401：服务器认证失败，未授权。");
            break;
        case 403:
            console.log("403：服务器拒绝访问，权限不足。");
            break;
        case 404:
            console.log("404：请求地址不存在。");
            break;
        case 405:
            console.log("405：请求方法不被允许。");
            break;
        case 408:
            console.log("408：请求超时。");
            break;
        case 409:
            console.log("409：请求冲突。");
            break;
        case 415:
            console.log("415：不支持的媒体类型。");
            break;
        case 429:
            console.log("429：请求过于频繁，请稍后再试。");
            break;
        case 500:
            console.log("500：服务器遇到意外错误。");
            break;
        case 502:
            console.log("502：网关错误，服务器无响应。");
            break;
        case 503:
            console.log("503：服务不可用，服务器暂时过载或维护。");
            break;
        case 504:
            console.log("504：网关超时。");
            break;
        default:
            console.log(status + "：" + info);
            break;
    }
}

instance.interceptors.request.use(
    config =>{
        if(config.method === "post" && !(config.data instanceof FormData) && !(Array.isArray(config.data))){
            config.data = qs.stringify(config.data)
        }
        return config;
    },
    error => Promise.reject(error)
)
instance.interceptors.response.use(
    response => response.status === 200 ?
        Promise.resolve(response) :
        Promise.reject(response),
    error =>{
        const { response } = error;
        errorHandle(response.status,response.info)
    }
)
export default instance;
