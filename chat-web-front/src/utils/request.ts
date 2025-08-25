import axios, { AxiosRequestConfig, AxiosResponse } from "axios";
import { ElMessage } from "element-plus";

// 创建 Axios 实例
const service = axios.create({ // 添加基础URL
    timeout: 120000, // 设置为120秒，更适合大模型请求
    headers: { "Content-Type": "application/json" },
});

// 请求拦截器
service.interceptors.request.use(
    (config) => {
        // 可在这里统一添加 token
        // const token = localStorage.getItem('token');
        // if (token) config.headers['Authorization'] = `Bearer ${token}`;

        // 添加请求日志，便于调试
        console.log(`发起请求: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
    },
    (error) => {
        console.error('请求拦截器错误:', error);
        return Promise.reject(error);
    }
);

// 响应拦截器
service.interceptors.response.use(
    (response: AxiosResponse) => {
        console.log('响应成功:', response.status, response.data);

        // 根据你的后端实际返回结构调整
        // 如果后端直接返回数据内容，没有code字段
        if (response.data !== null && response.data !== undefined) {
            return response.data;
        }

        // 如果后端有统一的响应格式 { code: number, data: any, msg: string }
        const res = response.data;
        if (res.code && res.code !== 200) {
            const errorMsg = res.msg || res.message || "请求错误";
            ElMessage({
                message: errorMsg,
                type: "error",
                duration: 3000,
            });
            return Promise.reject(new Error(errorMsg));
        }

        return res.data || res;
    },
    (error) => {
        console.error('响应错误详情:', error);

        let message = "网络错误";

        if (error.response) {
            // 服务器返回了错误状态码 (4xx, 5xx)
            const status = error.response.status;
            const data = error.response.data;

            console.error(`后端错误: ${status}`, data);

            switch (status) {
                case 400:
                    message = data?.msg || data?.message || "请求参数错误";
                    break;
                case 401:
                    message = "未授权，请重新登录";
                    // 可以在这里跳转到登录页
                    break;
                case 403:
                    message = "拒绝访问";
                    break;
                case 404:
                    message = `请求地址不存在: ${error.config?.url}`;
                    break;
                case 405:
                    message = "请求方法不被允许，请检查CORS配置";
                    break;
                case 408:
                    message = "请求超时";
                    break;
                case 500:
                    message = data?.msg || data?.message || "服务器内部错误";
                    break;
                case 502:
                    message = "网关错误";
                    break;
                case 503:
                    message = "服务不可用";
                    break;
                case 504:
                    message = "网关超时";
                    break;
                default:
                    message = data?.msg || data?.message || `请求错误: ${status}`;
            }
        } else if (error.code === 'ECONNABORTED') {
            message = "请求超时，可能是模型处理时间过长";
        } else if (error.request) {
            // 请求已发出但没有收到响应
            message = "网络连接异常，请检查网络或后端服务是否启动";
            console.error('无响应 received:', error.request);
        } else {
            // 其他错误
            message = error.message || "未知错误";
        }

        ElMessage({
            message: message,
            type: "error",
            duration: 5000, // 错误消息显示时间长一些
        });

        return Promise.reject(new Error(message));
    }
);

export default service;