<script setup lang="ts">
import { ref } from "vue";
import MenuComp from "./compentent/menu.vue";
import ChatBox from "./compentent/chatbox.vue";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();
const userId = userStore.userState?.id || null;

const selectedSessionId = ref<number | null>(null);

// 父组件接收子组件 emit
const handleSelectSession = (id: number) => {
  console.log("父组件收到 sessionId:", id);
  selectedSessionId.value = id;
};

const handleDeletedSession = (id: number) => {
  console.log("收到删除会话", id);
  if (selectedSessionId.value === id) {
    selectedSessionId.value = null;
  }
};
</script>

<template>
  <div class="home">
    <div class="menu">
      <MenuComp
        :userId="userId"
        @selectSession="handleSelectSession"
        @deletedSession="handleDeletedSession"
      />
    </div>
    <div class="chat-box">
      <ChatBox :sessionId="selectedSessionId" :userId="userId" />
    </div>
  </div>
</template>

<style scoped>
.home {
  display: flex;
  height: 100vh;
  background: linear-gradient(180deg, var(--bg-start), var(--bg-end));
  color: var(--text-primary);
}
.menu {
  width: 260px;
  border-right: 1px solid rgba(0, 0, 0, 0.06);
}
.chat-box {
  flex: 1;
  padding: 0;
  display: flex;
  flex-direction: column;
}
</style>
