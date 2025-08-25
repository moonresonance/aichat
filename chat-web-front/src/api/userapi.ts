import request from "@/utils/request";

export async function login(data: any) {
    return request({
        url: "http://localhost:8080/user/login",
        method: "post",
        data,
    });
}

export async function register(data: any) {
    return request({
        url: "http://localhost:8080/user/register",
        method: "post",
        data,
    });
}

