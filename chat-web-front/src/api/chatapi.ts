import request from '@/utils/request'

export function chatbyqwen3(data: any) {
    return request({
        url: 'http://localhost:8000/chatbyqwen3',
        method: 'post',
        data
    })
}
