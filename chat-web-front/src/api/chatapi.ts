import request from '@/utils/request'

export function chatbyqwen3(data: any) {
    return request({
        url: 'http://localhost:8000/chatbyqwen3',
        method: 'post',
        data
    })
}

export function getchatlist(data: any) {
    const userId = data.userId
    const sessionId = data.sessionId
    return request({
        url: 'http://localhost:8080/chat/getChats',
        method: 'get',
        params: {
            userId: userId,
            sessionId: sessionId
        }
    })
}

export function addchat(data: any) {
    return request({
        url: 'http://localhost:8080/chat/addChat',
        method: 'post',
        data
    })
}

export function deletechat(data: any) {
    return request({
        url: 'http://localhost:8080/chat/deleteChat',
        method: 'delete',
        params: {
            sessionId: data.session_id
        }
    })
}

export function updatechat(data: any) {
    return request({
        url: 'http://localhost:8080/chat/updateChat',
        method: 'put',
        data
    })
}

