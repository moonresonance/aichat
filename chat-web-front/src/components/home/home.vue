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

/* === Telegram-inspired layout container styling overrides === */
.home {
  background: #e7ebf0;
}

.menu {
  width: 360px;
  border-right: 1px solid rgba(0,0,0,.06);
  background: #ffffff;
}

.chat-box {
  background: #e7ebf0;
}


/* === Telegram-inspired Dark Theme & Extra Elements === */

/* 深色模式整体 */
.dark .home,
.dark .chat-box {
  background: #0e1621;
}

.dark .menu {
  background: #17212b;
  border-right: 1px solid rgba(255,255,255,.06);
}

.dark .menu-item {
  color: #e9edef;
}

.dark .menu-item:hover {
  background: rgba(255,255,255,0.04);
}

.dark .menu-item.selected {
  background: #2b5278;
  border: 1px solid rgba(255,255,255,0.1);
}

.dark .menu-item-name {
  color: #fff;
}

.dark .menu-item-detail {
  color: #aebac1;
}

.dark .message-item.user .message-content {
  background: #2b5278;
  color: #fff;
}

.dark .message-item.ai .message-content {
  background: #182533;
  color: #fff;
}

.dark .message-meta,
.dark .message-time {
  color: #8696a0;
}

/* === 头像 === */
.message-item {
  display: flex;
  align-items: flex-end;
}

.message-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  margin-right: 8px;
  flex-shrink: 0;
  background: #ccc;
  overflow: hidden;
}

.message-item.user .message-avatar {
  display: none; /* 我方消息一般不显示头像 */
}

/* === 已读双勾 === */
.message-status {
  display: inline-flex;
  align-items: center;
  margin-left: 4px;
  font-size: 12px;
  color: #34b7f1;
}

.message-status .check {
  width: 14px;
  height: 14px;
  display: inline-block;
  background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="%2334b7f1"><path d="M5.5 11.5l-3-3 1.06-1.06L5.5 9.38l6.94-6.94L13.5 3.5z"/><path d="M9.5 11.5l-3-3 1.06-1.06L9.5 9.38l6.94-6.94L17.5 3.5z"/></svg>') no-repeat center;
  background-size: contain;
}

/* === 未读徽标 === */
.unread-badge {
  background: #2a9df4;
  color: #fff;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
  padding: 2px 6px;
  margin-left: auto;
}

</style>