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
  width: 320px;
  flex-shrink: 0;
  border-right: 1px solid var(--sidebar-border);
  transition: width 0.3s ease;
}
@media (max-width: 768px) {
  .menu {
    width: 100%;
    position: absolute;
    z-index: 10;
    /* Add logic to hide/show menu on mobile */
  }
}
.chat-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Prevent content from overflowing */
}
</style>
