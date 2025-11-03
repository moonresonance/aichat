<template>
  <div class="settings-page">
    <header class="settings-hero">
      <button @click="goBack" class="back-btn" aria-label="返回上一页">
        <svg
          class="icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M19 12H5"></path>
          <path d="M12 19l-7-7 7-7"></path>
        </svg>
      </button>
      <div class="hero-text">
        <span class="hero-subtitle">Personal Center</span>
        <h1 class="hero-title">设置中心</h1>
        <p class="hero-description">在这里管理你的个人资料、外观偏好和账户安全</p>
      </div>
      <div class="hero-decoration"></div>
    </header>

    <main class="settings-main">
      <section class="settings-card user-card">
        <div class="user-avatar">{{ userInitials }}</div>
        <div class="user-meta">
          <div class="user-meta-header">
            <input
              v-model="userInfo.name"
              type="text"
              class="user-name-input"
              :disabled="!editMode"
              placeholder="请输入用户名"
            />
            <button
              @click="toggleEditMode"
              class="primary-btn"
              :class="{ active: editMode }"
            >
              {{ editMode ? "保存信息" : "编辑资料" }}
            </button>
          </div>
          <div class="user-tags">
            <span class="user-id">ID: {{ userInfo.id }}</span>
            <span class="user-status">活跃用户</span>
          </div>
        </div>
      </section>

      <section class="settings-card">
        <div class="card-header">
          <div>
            <h2 class="card-title">数据管理</h2>
            <p class="card-description">掌控你的聊天记录与个人数据</p>
          </div>
        </div>
        <div class="setting-row">
          <div class="setting-info">
            <h3>清除会话数据</h3>
            <p>删除当前账号下的全部会话历史，操作后将无法恢复</p>
          </div>
          <button @click="clearSessionData" class="danger-btn">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"></path>
              <path d="M10 11v6"></path>
              <path d="M14 11v6"></path>
            </svg>
            清除所有会话
          </button>
        </div>
      </section>

      <section class="settings-card">
        <div class="card-header">
          <div>
            <h2 class="card-title">账户安全</h2>
            <p class="card-description">管理你的登录状态，保障账户安全</p>
          </div>
        </div>
        <div class="setting-row">
          <div class="setting-info">
            <h3>退出当前账号</h3>
            <p>退出登录后需要重新输入账号信息才能继续使用</p>
          </div>
          <button @click="handleLogout" class="danger-btn">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            退出登录
          </button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";

const router = useRouter();
const userStore = useUserStore();

// 编辑模式
const editMode = ref(false);
const userInfo = ref({
  id: userStore.userState?.id || 0,
  name: userStore.userState?.name || "",
});
const userInitials = computed(() => {
  const name = userInfo.value.name?.trim();
  if (!name) return "AI";
  const parts = name.split(/\s+/).filter(Boolean);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
});

// 返回
const goBack = () => {
  router.go(-1);
};

// 切换编辑模式
const toggleEditMode = async () => {
  if (editMode.value) {
    // 保存用户信息
    try {
      userStore.updateUser({
        ...userStore.userState!,
        name: userInfo.value.name,
      });
      editMode.value = false;
      alert("用户信息已保存");
    } catch (error) {
      console.error("保存用户信息失败:", error);
      alert("保存失败，请重试");
    }
  } else {
    editMode.value = true;
  }
};

// 清除会话数据
const clearSessionData = async () => {
  if (!confirm("确定要清除所有会话数据吗？此操作不可恢复。")) return;

  try {
    // 这里可以调用清除会话的API
    // await clearAllSessions(userStore.userState?.id)
    alert("会话数据已清除");
  } catch (error) {
    console.error("清除会话数据失败:", error);
    alert("清除失败，请重试");
  }
};

// 登出
const handleLogout = async () => {
  if (!confirm("确定要退出登录吗？")) return;

  try {
    await userStore.logout();
    router.replace({ name: "login" });
  } catch (error) {
    console.error("登出失败:", error);
    // 即使失败也跳转到登录页
    router.replace({ name: "login" });
  }
};

onMounted(() => {
  // 同步最新的用户信息
  userInfo.value = {
    id: userStore.userState?.id || 0,
    name: userStore.userState?.name || "",
  };
});
</script>

<style scoped>
.settings-page {
  position: relative;
  min-height: 100vh;
  padding-bottom: 48px;
  color: var(--text-primary);
  background:
    radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.12), transparent 55%),
    radial-gradient(circle at 80% 0%, rgba(129, 140, 248, 0.14), transparent 50%),
    var(--surface-muted);
  transition: background 0.3s ease, color 0.3s ease;
  isolation: isolate;
  overflow: hidden;
}

.settings-page::before,
.settings-page::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.4s ease;
  z-index: 0;
}

.settings-page::before {
  background-image:
    radial-gradient(1px 1px at 20% 30%, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(1px 1px at 80% 20%, rgba(148, 197, 255, 0.9), transparent),
    radial-gradient(2px 2px at 50% 60%, rgba(96, 165, 250, 0.7), transparent),
    radial-gradient(1px 1px at 10% 80%, rgba(226, 232, 240, 0.7), transparent);
  background-size: 220px 220px, 320px 320px, 420px 420px, 260px 260px;
  mix-blend-mode: screen;
}

.settings-page::after {
  background:
    radial-gradient(circle at 10% 10%, rgba(59, 130, 246, 0.28), transparent 55%),
    radial-gradient(circle at 90% 80%, rgba(129, 140, 248, 0.32), transparent 60%);
}

.settings-page > * {
  position: relative;
  z-index: 1;
}

.settings-hero {
  position: relative;
  padding: 32px 40px;
  display: flex;
  align-items: flex-start;
  gap: 24px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.22), rgba(129, 140, 248, 0.18));
  border-bottom: 1px solid var(--border-subtle);
  border-radius: 0 0 28px 28px;
  box-shadow: var(--shadow-md);
}

.hero-text {
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: var(--accent-contrast);
}

.hero-subtitle {
  font-size: 13px;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  opacity: 0.9;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.hero-title {
  margin: 0;
  font-size: 32px;
  font-weight: 700;
  color: #ffffff;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
}

.hero-description {
  margin: 0;
  font-size: 14px;
  color: #ffffff;
  opacity: 0.92;
  text-shadow: 0 1px 6px rgba(0, 0, 0, 0.25);
}

.hero-decoration {
  position: absolute;
  right: -60px;
  top: -40px;
  width: 240px;
  height: 240px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.35), transparent 70%);
  filter: blur(0.4px);
}

.back-btn {
  background: var(--accent-ghost);
  border: 1px solid rgba(255, 255, 255, 0.35);
  color: var(--accent-contrast);
  cursor: pointer;
  padding: 10px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.24s ease, background 0.24s ease;
  backdrop-filter: blur(6px);
}

.back-btn:hover {
  transform: translateX(-2px);
  background: rgba(255, 255, 255, 0.22);
}

.settings-main {
  max-width: 980px;
  margin: 0 auto;
  padding: 32px 24px 0;
  display: grid;
  gap: 24px;
}

.settings-card {
  background: var(--surface-base);
  border-radius: 18px;
  padding: 24px;
  border: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-md);
  backdrop-filter: blur(16px);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.settings-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.user-card {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-avatar {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: linear-gradient(135deg, var(--accent-color), var(--accent-strong));
  color: var(--accent-contrast);
  font-size: 26px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  letter-spacing: 1px;
  box-shadow: var(--shadow-soft);
}

.user-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-meta-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-name-input {
  flex: 1;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid var(--control-border);
  background: var(--surface-elevated);
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  transition: border 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.user-name-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.18);
  background: var(--surface-overlay);
}

.user-name-input:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.user-tags {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  color: var(--text-secondary);
  font-size: 13px;
}

.user-status {
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--accent-ghost);
  color: var(--accent-color);
  font-weight: 600;
}

.primary-btn {
  padding: 10px 18px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, var(--accent-color), var(--accent-strong));
  color: var(--accent-contrast);
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
}

.primary-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 25px -16px rgba(59, 130, 246, 0.65);
}

.primary-btn.active {
  background: linear-gradient(135deg, #22c55e, #16a34a);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.card-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.card-description {
  margin: 6px 0 0 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 18px 0 0;
  border-top: 1px dashed var(--border-subtle);
}

.setting-info h3 {
  margin: 0 0 6px 0;
  font-size: 16px;
  font-weight: 600;
}

.setting-info p {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.danger-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 18px;
  border-radius: 999px;
  border: 1px solid rgba(239, 68, 68, 0.5);
  color: var(--danger-color);
  background: var(--danger-ghost);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.danger-btn:hover {
  background: var(--danger-color);
  color: #ffffff;
  box-shadow: 0 12px 28px -18px rgba(239, 68, 68, 0.65);
}

.icon {
  width: 20px;
  height: 20px;
  stroke-width: 2;
}

/* 夜空效果 */
:where([data-theme="dark"]) .settings-page {
  background: linear-gradient(180deg, #04050c 0%, #070d1a 55%, #020307 100%);
}

:where([data-theme="dark"]) .settings-page::before,
:where([data-theme="dark"]) .settings-page::after {
  opacity: 1;
}

:where([data-theme="dark"]) .settings-hero {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.35), rgba(14, 116, 144, 0.28));
  border-bottom: 1px solid var(--border-strong);
}

:where([data-theme="dark"]) .hero-description {
  color: rgba(226, 232, 240, 0.78);
}

:where([data-theme="dark"]) .back-btn {
  border-color: rgba(148, 163, 184, 0.35);
  background: rgba(59, 130, 246, 0.16);
}

:where([data-theme="dark"]) .back-btn:hover {
  background: rgba(59, 130, 246, 0.28);
}

:where([data-theme="dark"]) .settings-card {
  box-shadow: var(--shadow-md);
}

:where([data-theme="dark"]) .primary-btn:hover {
  box-shadow: 0 14px 30px -18px rgba(96, 165, 250, 0.65);
}

:where([data-theme="dark"]) .danger-btn {
  border-color: rgba(248, 113, 113, 0.6);
}

:where([data-theme="dark"]) .danger-btn:hover {
  box-shadow: 0 14px 32px -18px rgba(248, 113, 113, 0.6);
}

/* 响应式 */
@media (max-width: 900px) {
  .settings-main {
    padding: 28px 20px 0;
  }

  .setting-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .danger-btn,
  .primary-btn {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 640px) {
  .settings-hero {
    flex-direction: column;
    align-items: flex-start;
    padding: 28px 24px;
  }

  .user-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .user-meta-header {
    flex-direction: column;
    align-items: stretch;
  }

  .back-btn {
    margin-bottom: 8px;
  }

  .settings-main {
    padding: 24px 16px 0;
  }
}
</style>
