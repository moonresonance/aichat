<script setup lang="ts">
import { ref } from 'vue';
import MenuComp from './compentent/menu.vue';
import ChatBox from './compentent/chatbox.vue';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();
const userId = userStore.userState?.id || null;

const selectedSessionId = ref<number | null>(null);

// 父组件接收子组件 emit
const handleSelectSession = (id: number) => {
  console.log('父组件收到 sessionId:', id);
  selectedSessionId.value = id;
};
</script>

<template>
  <div class="home">
    <div class="menu">
      <MenuComp
          :userId="userId"
          @selectSession="handleSelectSession"
      />
    </div>
    <div class="chat-box">
      <ChatBox
          :sessionId="selectedSessionId"
          :userId="userId"
      />
    </div>
  </div>
</template>

<style scoped>
.home {
  display: flex;
  height: 100vh;
}
.menu { width: 180px; border-right: 1px solid #ccc; }
.chat-box { flex: 1; padding: 12px; }
</style>
