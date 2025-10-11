<!-- Home.vue -->
<script setup lang="ts">
import { ref } from "vue";
import MenuComp from "@/components/home/component/menu.vue";
import ChatBox from "@/components/home/component/chatbox.vue";
import { useUserStore } from "@/stores/user";
import Live2d from "@/components/home/component/live2d.vue";

const userStore = useUserStore();
const userId = userStore.userState?.id || null;
const selectedSessionId = ref<number | null>(null);

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
  background: #e7ebf0;
  color: var(--text-primary);
  position: relative;
  overflow: hidden;
}

.menu {
  width: 360px;
  flex-shrink: 0;
  border-right: 1px solid rgba(0, 0, 0, 0.06);
  background: #ffffff;
  transition: width 0.3s ease;
}

.chat-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #e7ebf0;
}

/* 修复 Live2D 容器样式 */
.live2d-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 300px;
  height: 300px;
  z-index: 9999;
  pointer-events: none;
  border: 1px solid #ccc; /* 临时边框用于调试 */
}

/* 确保在移动端也能显示 */
@media (max-width: 768px) {
  .menu {
    width: 100%;
    position: absolute;
    z-index: 10;
  }

  .live2d-container {
    width: 200px;
    height: 200px;
    bottom: 10px;
    right: 10px;
  }
}

/* 深色主题 */
.dark .home,
.dark .chat-box {
  background: #0e1621;
}

.dark .menu {
  background: #17212b;
  border-right: 1px solid rgba(255, 255, 255, 0.06);
}
</style>