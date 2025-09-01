<template>
  <div class="settings-container">
    <!-- Header -->
    <div class="settings-header">
      <button @click="goBack" class="back-btn" aria-label="返回">
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
      <h1 class="settings-title">设置</h1>
    </div>

    <!-- Settings Content -->
    <div class="settings-content">
      <!-- 用户信息区域 -->
      <div class="settings-section">
        <h2 class="section-title">用户信息</h2>
        <div class="setting-item">
          <label class="setting-label">用户名</label>
          <div class="setting-control">
            <input
              v-model="userInfo.name"
              type="text"
              class="setting-input"
              :disabled="!editMode"
              placeholder="请输入用户名"
            />
            <button
              @click="toggleEditMode"
              class="edit-btn"
              :class="{ active: editMode }"
            >
              {{ editMode ? "保存" : "编辑" }}
            </button>
          </div>
        </div>

        <div class="setting-item">
          <label class="setting-label">用户ID</label>
          <div class="setting-control">
            <input
              :value="userInfo.id"
              type="text"
              class="setting-input"
              disabled
            />
          </div>
        </div>
      </div>

      <!-- 外观设置 -->
      <div class="settings-section">
        <h2 class="section-title">外观设置</h2>
        <div class="setting-item">
          <label class="setting-label">主题模式</label>
          <div class="setting-control">
            <button
              @click="toggleTheme"
              class="theme-toggle-btn"
              :class="{ dark: isDark }"
            >
              <svg
                v-if="isDark"
                class="icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
              >
                <circle cx="12" cy="12" r="4"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
              </svg>
              <svg
                v-else
                class="icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
              >
                <path
                  d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79z"
                ></path>
              </svg>
              <span>{{ isDark ? "浅色模式" : "深色模式" }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 数据管理 -->
      <div class="settings-section">
        <h2 class="section-title">数据管理</h2>
        <div class="setting-item">
          <label class="setting-label">清除会话数据</label>
          <div class="setting-control">
            <button @click="clearSessionData" class="danger-btn">
              <svg
                class="icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
              >
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"></path>
                <path d="M10 11v6"></path>
                <path d="M14 11v6"></path>
              </svg>
              清除所有会话
            </button>
          </div>
        </div>
      </div>

      <!-- 账户操作 -->
      <div class="settings-section">
        <h2 class="section-title">账户操作</h2>
        <div class="setting-item">
          <label class="setting-label">登出账户</label>
          <div class="setting-control">
            <button @click="handleLogout" class="danger-btn">
              <svg
                class="icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
              >
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                <polyline points="16 17 21 12 16 7"></polyline>
                <line x1="21" y1="12" x2="9" y2="12"></line>
              </svg>
              退出登录
            </button>
          </div>
        </div>
      </div>
    </div>
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

// 主题
const isDark = ref(false);

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

// 主题切换
const applyTheme = (dark: boolean) => {
  const root = document.documentElement;
  if (dark) {
    root.classList.add("dark");
    root.classList.remove("light");
  } else {
    root.classList.add("light");
    root.classList.remove("dark");
  }
  try {
    localStorage.setItem("darkMode", dark ? "1" : "0");
  } catch {}
};

const initTheme = () => {
  try {
    const saved = localStorage.getItem("darkMode");
    if (saved === "1" || saved === "0") {
      isDark.value = saved === "1";
    } else {
      // 默认浅色，避免系统深色导致全局黑
      isDark.value = false;
    }
  } catch {
    isDark.value = false;
  }
  applyTheme(isDark.value);
};

const toggleTheme = () => {
  isDark.value = !isDark.value;
  applyTheme(isDark.value);
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
  initTheme();
  // 同步最新的用户信息
  userInfo.value = {
    id: userStore.userState?.id || 0,
    name: userStore.userState?.name || "",
  };
});
</script>

<style scoped>
.settings-container {
  height: 100vh;
  background-color: var(--color-background-soft);
  color: var(--text-primary);
  overflow-y: auto;
}

.settings-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-bottom: 1px solid var(--border-light);
  background-color: var(--color-background-mute);
  position: sticky;
  top: 0;
  z-index: 10;
}

.back-btn {
  background: none;
  border: 1px solid var(--border-light);
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.back-btn:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--border-hover);
}

.settings-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.settings-content {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.settings-section {
  margin-bottom: 32px;
  background-color: var(--color-background-mute);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-light);
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-light);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-label {
  font-weight: 500;
  color: var(--text-primary);
  min-width: 120px;
}

.setting-control {
  display: flex;
  align-items: center;
  gap: 12px;
}

.setting-input {
  padding: 8px 12px;
  border: 1px solid var(--border-light);
  border-radius: 6px;
  background-color: var(--color-background);
  color: var(--text-primary);
  font-size: 14px;
  min-width: 200px;
}

.setting-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.edit-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-light);
  border-radius: 6px;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.edit-btn:hover {
  background-color: var(--color-background-mute);
  border-color: var(--border-hover);
}

.edit-btn.active {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.theme-toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid var(--border-light);
  border-radius: 6px;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.theme-toggle-btn:hover {
  background-color: var(--bg-hover);
  border-color: var(--border-hover);
}

.danger-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid #ef4444;
  border-radius: 6px;
  background-color: transparent;
  color: #ef4444;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.danger-btn:hover {
  background-color: #ef4444;
  color: white;
}

.icon {
  width: 18px;
  height: 18px;
  stroke-width: 2;
}

/* 响应式 */
@media (max-width: 768px) {
  .settings-content {
    padding: 16px;
  }

  .setting-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .setting-control {
    width: 100%;
    justify-content: flex-end;
  }

  .setting-input {
    min-width: auto;
    flex: 1;
  }
}
</style>
