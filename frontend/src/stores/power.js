import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePowerStore = defineStore('power', () => {
  const dormNumber = ref('101') // 默认宿舍号，可以从配置或用户设置中获取
  
  const setDormNumber = (number) => {
    dormNumber.value = number
  }
  
  return {
    dormNumber,
    setDormNumber
  }
})
