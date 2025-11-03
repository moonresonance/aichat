<!-- Home.vue -->
<script setup lang="ts">
import { ref } from "vue";
import MenuComp from "@/components/home/component/menu.vue";
import ChatBox from "@/components/home/component/chatbox.vue";
import { useUserStore } from "@/stores/user";

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
    <div class="home-frame">
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
  </div>
</template>
<style scoped>
.home {
  min-height: 100vh;
  margin: 0;
  padding: 32px 24px;
  box-sizing: border-box;
  background:
    radial-gradient(circle at 8% 12%, rgba(42, 157, 244, 0.18), transparent 40%),
    radial-gradient(circle at 82% 6%, rgba(126, 214, 223, 0.2), transparent 52%),
    linear-gradient(135deg, #f1f5ff 0%, #eef3fb 45%, #e8eff8 100%);
  display: flex;
  justify-content: center;
  align-items: stretch;
  color: var(--text-primary);
  transition: background 0.4s ease;
  position: relative;
  overflow: hidden;
}

.home::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.45s ease;
  background-image:
    radial-gradient(2px 2px at 12% 18%, rgba(255, 255, 255, 0.95), transparent 60%),
    radial-gradient(1px 1px at 42% 72%, rgba(255, 255, 255, 0.85), transparent 55%),
    radial-gradient(1px 1px at 72% 38%, rgba(255, 255, 255, 0.8), transparent 60%),
    radial-gradient(2px 2px at 18% 84%, rgba(255, 255, 255, 0.9), transparent 60%),
    radial-gradient(3px 3px at 64% 58%, rgba(255, 255, 255, 1), transparent 70%),
    radial-gradient(1px 1px at 88% 22%, rgba(255, 255, 255, 0.85), transparent 55%),
    radial-gradient(2px 2px at 28% 48%, rgba(255, 255, 255, 0.9), transparent 65%),
    radial-gradient(1px 1px at 58% 88%, rgba(255, 255, 255, 0.75), transparent 60%),
    radial-gradient(1px 1px at 92% 68%, rgba(255, 255, 255, 0.8), transparent 55%),
    radial-gradient(2px 2px at 8% 28%, rgba(255, 255, 255, 0.95), transparent 70%),
    radial-gradient(1px 1px at 48% 8%, rgba(255, 255, 255, 0.85), transparent 60%),
    radial-gradient(3px 3px at 78% 78%, rgba(255, 255, 255, 0.9), transparent 65%),
    radial-gradient(1px 1px at 22% 58%, rgba(255, 255, 255, 0.8), transparent 55%),
    radial-gradient(2px 2px at 68% 12%, rgba(255, 255, 255, 1), transparent 70%),
    radial-gradient(1px 1px at 38% 92%, rgba(255, 255, 255, 0.75), transparent 60%),
    radial-gradient(1px 1px at 82% 42%, rgba(255, 255, 255, 0.85), transparent 55%),
    radial-gradient(2px 2px at 52% 62%, rgba(255, 255, 255, 0.9), transparent 65%),
    radial-gradient(1px 1px at 2% 52%, rgba(255, 255, 255, 0.8), transparent 60%),
    radial-gradient(3px 3px at 95% 8%, rgba(255, 255, 255, 0.95), transparent 70%);
  background-size: 420px 420px, 460px 460px, 380px 380px, 500px 500px, 340px 340px,
                   540px 540px, 400px 400px, 480px 480px, 360px 360px, 520px 520px,
                   440px 440px, 320px 320px, 560px 560px, 300px 300px, 580px 580px,
                   280px 280px, 600px 600px, 260px 260px, 620px 620px;
  background-repeat: repeat;
}

:global([data-theme="dark"]) .home::before {
  opacity: 1;
  animation: homeStarTwinkle 4.5s ease-in-out infinite;
}

@keyframes homeStarTwinkle {
  0%, 100% { 
    opacity: 0.88;
    filter: brightness(1.15);
  }
  50% { 
    opacity: 1;
    filter: brightness(1.3);
  }
}

.home-frame {
  width: min(1180px, 100%);
  min-height: calc(100vh - 64px);
  background: rgba(255, 255, 255, 0.15);
  border-radius: 28px;
  border: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(40px) saturate(180%) contrast(120%);
  -webkit-backdrop-filter: blur(40px) saturate(180%) contrast(120%);
  overflow: hidden;
  display: flex;
  animation: frameSlideIn 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  z-index: 1;
}

[data-theme="dark"] .home-frame {
  background: rgba(8, 12, 22, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 
    0 40px 80px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(50px) saturate(200%) contrast(130%);
  -webkit-backdrop-filter: blur(50px) saturate(200%) contrast(130%);
}

.menu {
  width: 340px;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.1);
  border-right: 1px solid var(--sidebar-border);
  backdrop-filter: blur(30px) saturate(160%);
  -webkit-backdrop-filter: blur(30px) saturate(160%);
}

[data-theme="dark"] .menu {
  background: rgba(10, 16, 26, 0.2);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
}

.chat-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(244, 249, 255, 0.15);
  backdrop-filter: blur(30px) saturate(160%);
  -webkit-backdrop-filter: blur(30px) saturate(160%);
}

[data-theme="dark"] .chat-box {
  background: rgba(5, 7, 13, 0.2);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
}

@media (max-width: 1024px) {
  .home {
    padding: 18px;
  }

  .home-frame {
    border-radius: 22px;
  }

  .menu {
    width: 300px;
  }
}

@media (max-width: 768px) {
  .home {
    padding: 12px;
    background: linear-gradient(160deg, #f1f5ff 0%, #eef3fb 100%);
  }

  .home-frame {
    flex-direction: column;
    min-height: calc(100vh - 24px);
  }

  .menu {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--border-subtle);
  }
}

@keyframes frameSlideIn {
  from {
    opacity: 0;
    transform: scale(0.96) translateY(12px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.home {
  animation: fadeIn 0.45s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

</style>

<style>
/* 全局暗色主题样式 - 不使用 scoped */
[data-theme="dark"] .home {
  background-color: #000000 !important;
  background-image: none !important;
}

[data-theme="dark"] .home::before {
  opacity: 1 !important;
}

@media (max-width: 768px) {
  [data-theme="dark"] .home {
    background-color: #000000 !important;
    background-image: none !important;
  }
}
</style>