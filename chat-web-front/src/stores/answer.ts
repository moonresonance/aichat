import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAnswerStore = defineStore('answer', () => {
    const answer = ref('')
    const setAnswer = (newAnswer: string) => {
        answer.value = newAnswer
    }
    const getAnswer = () => {
        return answer.value
    }
    return { answer, setAnswer, getAnswer }
})

