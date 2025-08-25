import { defineStore } from 'pinia'
import { ref } from 'vue'


export interface UserState {
    id:number
    name: string
    isLogin: boolean
}

export const useUserStore = defineStore('user', () => {
    const userState = ref<UserState>({
        id: 0,
        name: '',
        isLogin: false
    })

    const login = (user: UserState) => {
        userState.value = user
        userState.value.isLogin = true
    }

    const logout = () => {
        userState.value = {
            id: 0,
            name: '',
            isLogin: false
        }
    }
    const updateUser = (user: UserState) => {
        userState.value = user
    }

    return {
        userState,
        login,
        logout,
        updateUser
    }
}, {
    persist: true
})
