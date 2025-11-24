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

    <!-- 确认对话框 -->
    <div v-if="showConfirmDialog" class="modal-overlay" @click.self="cancelConfirm">
      <div class="confirm-dialog">
        <div class="confirm-icon" :class="confirmConfig.type">
          <svg v-if="confirmConfig.type === 'danger'" viewBox="0 0 24 24" fill="currentColor">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <svg v-else-if="confirmConfig.type === 'warning'" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L2 20h20L12 2z"></path>
            <text x="12" y="16" font-size="12" text-anchor="middle" fill="white">!</text>
          </svg>
        </div>
        
        <div class="confirm-content">
          <h3 class="confirm-title">{{ confirmConfig.title }}</h3>
          <p class="confirm-message">{{ confirmConfig.message }}</p>
        </div>
        
        <div class="confirm-footer">
          <button class="confirm-btn cancel" @click="cancelConfirm">
            {{ confirmConfig.cancelText || '取消' }}
          </button>
          <button class="confirm-btn danger" @click="confirmAction">
            {{ confirmConfig.confirmText || '确认' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑信息弹窗 -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="edit-modal">
        <div class="modal-header">
          <h2>编辑个人资料</h2>
          <button class="modal-close" @click="closeEditModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        
        <div class="modal-content">
          <div class="form-group">
            <label for="edit-name">用户名</label>
            <input
              id="edit-name"
              v-model="editForm.name"
              type="text"
              class="form-input"
              placeholder="请输入新用户名"
            />
          </div>
          
          <div class="form-group">
            <label for="edit-password">新密码</label>
            <input
              id="edit-password"
              v-model="editForm.password"
              type="password"
              class="form-input"
              placeholder="留空表示不修改密码"
            />
          </div>
          
          <div class="form-group">
            <label for="edit-password-confirm">确认密码</label>
            <input
              id="edit-password-confirm"
              v-model="editForm.passwordConfirm"
              type="password"
              class="form-input"
              placeholder="请再次输入密码"
            />
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeEditModal">取消</button>
          <button class="btn-submit" @click="saveEditInfo">保存修改</button>
        </div>
      </div>
    </div>

    <main class="settings-main">
      <section class="settings-card user-card">
        <div class="user-avatar">{{ userInitials }}</div>
        <div class="user-meta">
          <div class="user-name-row">
            <div class="user-name-display">{{ userInfo.name || "用户名" }}</div>
            <span class="user-status">活跃用户</span>
          </div>
          <div class="user-tags">
            <span class="user-id">ID: {{ userInfo.id }}</span>
          </div>
        </div>
        <button
          @click="openEditModal"
          class="primary-btn"
        >
          编辑资料
        </button>
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

// 确认对话框
const showConfirmDialog = ref(false);
const confirmConfig = ref({
  title: '',
  message: '',
  type: 'warning', // 'warning' | 'danger'
  confirmText: '确认',
  cancelText: '取消',
  onConfirm: null as (() => void) | null,
});

// 打开确认对话框
const openConfirmDialog = (config: {
  title: string;
  message: string;
  type?: 'warning' | 'danger';
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void | Promise<void>;
}) => {
  confirmConfig.value = {
    title: config.title,
    message: config.message,
    type: config.type || 'warning',
    confirmText: config.confirmText || '确认',
    cancelText: config.cancelText || '取消',
    onConfirm: config.onConfirm,
  };
  showConfirmDialog.value = true;
};

// 确认操作
const confirmAction = async () => {
  if (confirmConfig.value.onConfirm) {
    try {
      await confirmConfig.value.onConfirm();
    } catch (error) {
      console.error('确认操作失败:', error);
    }
  }
  cancelConfirm();
};

// 取消操作
const cancelConfirm = () => {
  showConfirmDialog.value = false;
  confirmConfig.value = {
    title: '',
    message: '',
    type: 'warning',
    confirmText: '确认',
    cancelText: '取消',
    onConfirm: null,
  };
};

// 编辑模式
const editMode = ref(false);
const showEditModal = ref(false);
const editForm = ref({
  name: "",
  password: "",
  passwordConfirm: "",
});

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
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push("/home");
  }
};

// 打开编辑弹窗
const openEditModal = () => {
  editForm.value = {
    name: userInfo.value.name,
    password: "",
    passwordConfirm: "",
  };
  showEditModal.value = true;
};

// 关闭编辑弹窗
const closeEditModal = () => {
  showEditModal.value = false;
  editForm.value = {
    name: "",
    password: "",
    passwordConfirm: "",
  };
};

// 保存编辑信息
const saveEditInfo = async () => {
  // 验证用户名
  if (!editForm.value.name.trim()) {
    alert("用户名不能为空");
    return;
  }
  
  // 验证密码
  if (editForm.value.password || editForm.value.passwordConfirm) {
    if (editForm.value.password.length < 6) {
      alert("密码长度不能少于6位");
      return;
    }
    if (editForm.value.password !== editForm.value.passwordConfirm) {
      alert("两次输入的密码不一致");
      return;
    }
  }
  
  try {
    // 更新用户信息
    userStore.updateUser({
      ...userStore.userState!,
      name: editForm.value.name,
    });
    
    userInfo.value.name = editForm.value.name;
    alert("信息修改成功");
    closeEditModal();
  } catch (error) {
    console.error("保存失败:", error);
    alert("保存失败，请重试");
  }
};

// 切换编辑模式（已弃用，保持兼容性）
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
  openConfirmDialog({
    title: '清除所有会话数据',
    message: '确定要删除当前账号下的全部会话历史吗？此操作无法撤销，请谨慎操作。',
    type: 'danger',
    confirmText: '删除所有会话',
    cancelText: '取消',
    onConfirm: async () => {
      try {
        // 这里可以调用清除会话的API
        // await clearAllSessions(userStore.userState?.id)
        alert("会话数据已清除");
      } catch (error) {
        console.error("清除会话数据失败:", error);
        alert("清除失败，请重试");
      }
    }
  });
};

// 登出
const handleLogout = async () => {
  openConfirmDialog({
    title: '退出登录',
    message: '确定要退出当前账号吗？退出后需要重新输入账号信息才能继续使用。',
    type: 'warning',
    confirmText: '退出登录',
    cancelText: '取消',
    onConfirm: async () => {
      try {
        await userStore.logout();
        router.replace({ name: "login" });
      } catch (error) {
        console.error("登出失败:", error);
        // 即使失败也跳转到登录页
        router.replace({ name: "login" });
      }
    }
  });
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
  animation: pageSlideIn 0.4s ease-out;
}

@keyframes pageSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.settings-page::before,
.settings-page::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0;
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
  padding: 48px 40px;
  display: flex;
  align-items: flex-start;
  gap: 24px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.28), rgba(129, 140, 248, 0.22), rgba(99, 102, 241, 0.18));
  border-bottom: 2px solid var(--border-subtle);
  border-radius: 0 0 32px 32px;
  box-shadow: 0 20px 40px -15px rgba(59, 130, 246, 0.3);
  animation: heroFadeInDown 0.5s ease-out;
}

@keyframes heroFadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
  animation: backBtnFadeIn 0.4s ease-out;
  position: relative;
  z-index: 10;
}

@keyframes backBtnFadeIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
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
  background: linear-gradient(135deg, var(--surface-base) 0%, rgba(255, 255, 255, 0.04) 100%);
  border-radius: 24px;
  padding: 32px;
  border: 1.5px solid var(--border-subtle);
  box-shadow: 0 16px 40px -12px rgba(15, 23, 42, 0.12);
  backdrop-filter: blur(20px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  animation: cardSlideUp 0.4s ease-out both;
}

.settings-card:nth-child(1) {
  animation-delay: 0.05s;
}

.settings-card:nth-child(2) {
  animation-delay: 0.1s;
}

.settings-card:nth-child(3) {
  animation-delay: 0.15s;
}

@keyframes cardSlideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.settings-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%, rgba(255, 255, 255, 0.05) 100%);
  pointer-events: none;
  border-radius: 24px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.settings-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 24px 56px -12px rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.3);
}

.settings-card:hover::before {
  opacity: 1;
}

.user-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(129, 140, 248, 0.06));
  border: 1.5px solid rgba(59, 130, 246, 0.15);
}

.user-avatar {
  width: 88px;
  height: 88px;
  border-radius: 24px;
  background: linear-gradient(135deg, var(--accent-color), var(--accent-strong), rgba(129, 140, 248, 0.8));
  color: var(--accent-contrast);
  font-size: 32px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  letter-spacing: 1px;
  box-shadow: 0 12px 32px -8px rgba(59, 130, 246, 0.4);
  flex-shrink: 0;
  animation: avatarPulse 2s ease-in-out infinite;
}

@keyframes avatarPulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.03);
  }
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

.user-name-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-name-input {
  flex: 1;
  padding: 14px 18px;
  border-radius: 14px;
  border: 1.5px solid var(--control-border);
  background: var(--surface-elevated);
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.user-name-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
  background: var(--surface-overlay);
  transform: translateY(-1px);
}

.user-name-input:disabled {
  opacity: 0.65;
  cursor: not-allowed;
  background: var(--surface-muted);
}

.user-tags {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-secondary);
  font-size: 13px;
}

.user-status {
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--accent-ghost);
  color: var(--accent-color);
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  animation: statusPulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  position: relative;
}

.user-status::before {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-color);
  animation: statusDotGlow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes statusPulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.3);
    transform: scale(1);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(59, 130, 246, 0);
    transform: scale(1.02);
  }
}

@keyframes statusDotGlow {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.8);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0);
  }
}

.primary-btn {
  padding: 12px 24px;
  border-radius: 14px;
  border: none;
  background: linear-gradient(135deg, var(--accent-color), var(--accent-strong));
  color: var(--accent-contrast);
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
  box-shadow: 0 8px 20px -8px rgba(59, 130, 246, 0.4);
  will-change: transform, box-shadow;
}

.primary-btn:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 12px 28px -8px rgba(59, 130, 246, 0.5);
}

.primary-btn:active {
  transform: translateY(0) scale(0.98);
  box-shadow: 0 4px 12px -8px rgba(59, 130, 246, 0.3);
}

.primary-btn.active {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  box-shadow: 0 8px 20px -8px rgba(34, 197, 94, 0.4);
}

.user-card .primary-btn {
  flex-shrink: 0;
  margin-left: auto;
  white-space: nowrap;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 2px solid var(--border-subtle);
}

.card-title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--text-primary), var(--text-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.card-description {
  margin: 8px 0 0 0;
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
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
  padding: 12px 24px;
  border-radius: 14px;
  border: 1.5px solid rgba(239, 68, 68, 0.4);
  color: var(--danger-color);
  background: rgba(239, 68, 68, 0.08);
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
  will-change: transform, box-shadow;
}

.danger-btn:hover {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.9), rgba(220, 38, 38, 0.85));
  color: #ffffff;
  border-color: rgba(239, 68, 68, 0.8);
  box-shadow: 0 12px 28px -8px rgba(239, 68, 68, 0.4);
  transform: translateY(-2px) scale(1.02);
}

.danger-btn:active {
  transform: translateY(0) scale(0.98);
  box-shadow: 0 4px 12px -8px rgba(239, 68, 68, 0.3);
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

  .user-card .primary-btn {
    margin-left: 0;
    align-self: flex-start;
    margin-top: 12px;
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

/* 编辑模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
  animation: overlayFadeIn 0.3s ease-out;
}

@keyframes overlayFadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.edit-modal {
  background: var(--surface-elevated);
  border-radius: 20px;
  border: 1.5px solid var(--border-subtle);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  max-width: 480px;
  width: 90%;
  animation: modalSlideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  overflow: hidden;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
  border-bottom: 1px solid var(--border-subtle);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(99, 102, 241, 0.04));
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s ease;
  color: var(--text-secondary);
}

.modal-close:hover {
  background: var(--sidebar-hover);
  color: var(--text-primary);
  transform: rotate(90deg);
}

.modal-close svg {
  width: 20px;
  height: 20px;
  stroke-width: 2.5;
}

.modal-content {
  padding: 32px 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.form-input {
  padding: 12px 16px;
  border-radius: 12px;
  border: 1.5px solid var(--border-subtle);
  background: var(--surface-base);
  color: var(--text-primary);
  font-size: 14px;
  transition: all 0.2s ease;
  font-family: inherit;
}

.form-input::placeholder {
  color: var(--text-secondary);
}

.form-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  background: var(--surface-elevated);
}

[data-theme="dark"] .form-input {
  background: rgba(17, 24, 39, 0.6);
}

[data-theme="dark"] .form-input:focus {
  background: rgba(17, 24, 39, 0.8);
}

.modal-footer {
  padding: 24px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  border-top: 1px solid var(--border-subtle);
  background: var(--surface-base);
}

.btn-cancel,
.btn-submit {
  padding: 10px 24px;
  border-radius: 10px;
  border: none;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel {
  background: var(--surface-base);
  color: var(--text-secondary);
  border: 1.5px solid var(--border-subtle);
}

.btn-cancel:hover {
  background: var(--sidebar-hover);
  color: var(--text-primary);
  transform: translateY(-1px);
}

.btn-cancel:active {
  transform: translateY(0);
}

.btn-submit {
  background: linear-gradient(135deg, var(--accent-color), var(--accent-strong));
  color: var(--accent-contrast);
  box-shadow: 0 8px 20px -8px rgba(59, 130, 246, 0.4);
}

.btn-submit:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 12px 28px -8px rgba(59, 130, 246, 0.5);
}

.btn-submit:active {
  transform: translateY(0) scale(0.98);
  box-shadow: 0 4px 12px -8px rgba(59, 130, 246, 0.3);
}

.user-name-display {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  padding: 8px 0;
}

/* 确认对话框样式 */
.confirm-dialog {
  background: var(--surface-elevated);
  border-radius: 24px;
  border: 1.5px solid var(--border-subtle);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  max-width: 420px;
  width: 90%;
  animation: confirmSlideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 40px 32px;
  gap: 24px;
}

@keyframes confirmSlideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.confirm-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  animation: iconPop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.confirm-icon.warning {
  background: linear-gradient(135deg, rgba(251, 146, 60, 0.2), rgba(234, 179, 8, 0.15));
  color: #f97316;
  border: 2px solid rgba(251, 146, 60, 0.3);
}

.confirm-icon.danger {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.15));
  color: #ef4444;
  border: 2px solid rgba(239, 68, 68, 0.3);
}

@keyframes iconPop {
  0% {
    opacity: 0;
    transform: scale(0.3) rotate(-180deg);
  }
  100% {
    opacity: 1;
    transform: scale(1) rotate(0);
  }
}

.confirm-icon svg {
  width: 100%;
  height: 100%;
  stroke-width: 2;
}

.confirm-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.confirm-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  animation: titleFadeIn 0.5s ease-out 0.1s both;
}

@keyframes titleFadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.confirm-message {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  animation: messageFadeIn 0.5s ease-out 0.2s both;
}

@keyframes messageFadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.confirm-footer {
  display: flex;
  gap: 12px;
  width: 100%;
  animation: footerFadeIn 0.5s ease-out 0.3s both;
}

@keyframes footerFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.confirm-btn {
  flex: 1;
  padding: 12px 24px;
  border-radius: 12px;
  border: none;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  will-change: transform, box-shadow;
}

.confirm-btn.cancel {
  background: var(--surface-base);
  color: var(--text-secondary);
  border: 1.5px solid var(--border-subtle);
}

.confirm-btn.cancel:hover {
  background: var(--sidebar-hover);
  color: var(--text-primary);
  border-color: var(--border-strong);
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.1);
}

.confirm-btn.cancel:active {
  transform: translateY(0) scale(0.98);
}

.confirm-btn.danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: #ffffff;
  box-shadow: 0 8px 20px -8px rgba(239, 68, 68, 0.4);
}

.confirm-btn.danger:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 12px 28px -8px rgba(239, 68, 68, 0.5);
}

.confirm-btn.danger:active {
  transform: translateY(0) scale(0.98);
  box-shadow: 0 4px 12px -8px rgba(239, 68, 68, 0.3);
}

@media (max-width: 768px) {
  .edit-modal {
    width: 95%;
    max-width: 90vw;
  }

  .modal-content {
    padding: 24px 16px;
  }

  .modal-header,
  .modal-footer {
    padding: 16px;
  }

  .modal-header h2 {
    font-size: 18px;
  }

  .confirm-dialog {
    max-width: 85vw;
    padding: 32px 24px;
  }

  .confirm-title {
    font-size: 18px;
  }

  .confirm-message {
    font-size: 13px;
  }

  .confirm-footer {
    flex-direction: column;
  }

  .confirm-btn {
    padding: 14px 20px;
  }
}
</style>
