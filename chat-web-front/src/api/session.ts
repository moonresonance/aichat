import request from "@/utils/request";

export async function getSessionList(params: { userId: number }) {
    return request({
        url: "http://localhost:8080/session/getSessions",
        method: "get",
        params: params
    });
}

export async function createSession(data:any){
    return request({
        url: "http://localhost:8080/session/add",
        method: "post",
        data,
    });
}
