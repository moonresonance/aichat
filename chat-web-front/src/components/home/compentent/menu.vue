<script setup lang="ts">
import { onMounted, ref, computed, watch } from "vue";
import { getSessionList } from "@/api/session";
import { useUserStore } from "@/stores/user";
import { createSession } from "@/api/session";
import router from "@/router";
interface SessionItem {
  id: number;
  name: string;
  userId: number;
}
const menuList = ref<SessionItem[]>([]);
const selectedId = ref<number | null>(null);
const loadedOnce = ref(false);
const userStore = useUserStore();
const loading = ref(true);
const errorMsg = ref<string | null>(null);
const emit = defineEmits<{
  (e: "selectSession", id: number): void;
  (e: "deletedSession", id: number): void;
}>();
import { deleteSession } from "@/api/session";
const isDark = ref(document.documentElement.classList.contains("dark"));

const toggleDark = () => {
  const root = document.documentElement;
  if (root.classList.contains("dark")) {
    root.classList.remove("dark");
    isDark.value = false;
  } else {
    root.classList.add("dark");
    isDark.value = true;
  }
  try {
    localStorage.setItem("darkMode", isDark.value ? "1" : "0");
  } catch (e) {}
};

const avatarSrc = computed(() => {
  try {
    const u = (userStore.userState as any) || {};
    return u.avatar || "https://via.placeholder.com/40";
  } catch (e) {
    return "https://via.placeholder.com/40";
  }
});
// 模拟新会话 ID 自增（真实环境应由后端返回）仅供新名字序号展示
let nextId = 1000;
const userId = computed(() => userStore.userState.id);
const fetchMenuList = async () => {
  if (!userId.value || userId.value === 0) {
    errorMsg.value = "用户未登录";
    loading.value = false;
    return;
  }
  try {
    const res = await getSessionList({ userId: userId.value });
    menuList.value = res.data || [];

    if (menuList.value.length === 0) {
      errorMsg.value = "暂无会话";
    } else {
      // 默认选中第一个会话
      selectedId.value = menuList.value[0].id;
      if (selectedId.value != null) emit("selectSession", selectedId.value); // ✅ 触发父组件更新
      nextId = Math.max(...menuList.value.map((i) => i.id)) + 1;
    }
    loadedOnce.value = true;
  } catch (error) {
    errorMsg.value = "获取会话列表失败";
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// 点击会话
const handleClick = (item: SessionItem) => {
  selectedId.value = item.id;
  console.log("点击了会话:", item);
  if (selectedId.value != null) emit("selectSession", selectedId.value);
};

// 新聊天逻辑
const handleNewChat = async () => {
  if (!userId.value) {
    console.warn("用户未登录，无法创建会话");
    return;
  }

  const payload = {
    name: `新对话 ${menuList.value.length + 1}`,
    userId: userId.value,
  };

  try {
    // 创建新会话
    await createSession(payload);
    // 刷新列表
    await fetchMenuList();
    // 选中最新创建的会话（假设是最后一个）
    if (menuList.value.length > 0) {
      selectedId.value = menuList.value[menuList.value.length - 1].id;
      if (selectedId.value != null) emit("selectSession", selectedId.value);
    }
  } catch (err) {
    console.error("创建 session 失败", err);
  }
};

// 删除会话
const handleDelete = async (id: number) => {
  if (!confirm("确定要删除该会话吗？此操作不可恢复。")) return;
  try {
    await deleteSession({ id });
    menuList.value = menuList.value.filter((i) => i.id !== id);
    if (selectedId.value === id) {
      selectedId.value = menuList.value.length ? menuList.value[0].id : null;
      if (selectedId.value != null) emit("selectSession", selectedId.value);
    }
    emit("deletedSession", id);
  } catch (err) {
    console.error("删除失败", err);
  }
};

// 监听用户登录状态，登录后立即加载一次历史会话
watch(
  () => userId.value,
  (val) => {
    if (val && val > 0 && !loadedOnce.value) {
      fetchMenuList();
    }
  }
);

onMounted(() => {
  if (userId.value && userId.value > 0) fetchMenuList();
});
</script>

<template>
  <div class="menu-container">
    <!-- LOGO 区域 -->
    <div class="menu-logo">
      <div
        style="
          display: flex;
          align-items: center;
          justify-content: space-between;
          width: 100%;
        "
      >
        <span class="logo-text">AI 聊天</span>
        <button
          @click="toggleDark"
          class="theme-toggle"
          :title="isDark ? 'Light mode' : 'Dark mode'"
        >
          {{ isDark ? "☀️" : "🌙" }}
        </button>
      </div>
    </div>

    <!-- 用户信息 -->
    <div class="userinfo">
      <img :src="avatarSrc" alt="头像" class="user-avatar" />
      <span class="user-name">{{ userStore.userState?.name || "游客" }}</span>
    </div>

    <!-- 新聊天按钮 -->
    <div class="menu-header">
      <button class="new-chat-btn" @click="handleNewChat">+ 新聊天</button>
    </div>

    <div v-if="loading" class="menu-status">加载中...</div>
    <div v-else-if="errorMsg" class="menu-status">{{ errorMsg }}</div>
    <div v-else>
      <div
        v-for="item in menuList"
        :key="item.id"
        class="menu-item"
        :class="{ selected: selectedId === item.id }"
      >
        <div
          style="flex: 1; display: flex; align-items: center; gap: 8px"
          @click="handleClick(item)"
        >
          <div class="menu-item-icon">💬</div>
          <div class="menu-item-name">{{ item.name }}</div>
          <div class="menu-item-index">
            #{{ menuList.findIndex((s) => s.id === item.id) + 1 }}
          </div>
        </div>
        <button
          class="delete-btn"
          @click.stop="handleDelete(item.id)"
          title="删除"
        >
          🗑️
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.menu-container {
  background-color: var(--sidebar-bg);
  color: var(--sidebar-text, var(--text-primary));
  padding: 20px 12px;
  height: 100%;
  overflow-y: auto;
  font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  border-right: 1px solid var(--sidebar-border);
  transition: background-color 0.25s, color 0.25s;
}

/* LOGO 区域 */
.menu-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 0 40px;
  flex-direction: column;
  margin-bottom: 12px;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: inherit;
  letter-spacing: 0.6px;
}

/* 用户信息 - 竖直排列 */
.userinfo {
  display: flex;
  flex-direction: column; /* 垂直排列 */
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: 2px solid var(--sidebar-border);
  object-fit: cover;
  margin-bottom: 6px; /* 与名字间距 */
}

.user-name {
  font-size: 14px;
  font-weight: bold;
  color: var(--sidebar-text, var(--text-primary));
  text-align: center;
  padding-bottom: 100px;
}

/* 新聊天按钮 */
.menu-header {
  margin-bottom: 12px;
  text-align: center;
}

.new-chat-btn {
  padding: 8px 14px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #10b981, #06b6d4);
  color: #08232a;
  cursor: pointer;
  font-weight: 700;
  transition: all 0.16s ease-in-out;
}
.new-chat-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(2, 6, 23, 0.4);
}

/* 会话列表 */
.menu-status {
  text-align: center;
  padding: 16px;
  color: var(--muted);
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  margin-bottom: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.14s, transform 0.08s, box-shadow 0.14s;
  background: transparent;
}

.menu-item:hover {
  background: var(--sidebar-hover);
  transform: translateX(4px);
}

.menu-item.selected {
  background: var(--sidebar-selected);
  font-weight: 700;
}

.menu-item-icon {
  margin-right: 10px;
}

.menu-item-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.menu-item-index {
  font-size: 11px;
  opacity: 0.55;
}

/* theme toggle and delete button */
.theme-toggle {
  background: transparent;
  border: none;
  color: inherit;
  cursor: pointer;
  font-size: 16px;
}
.delete-btn {
  background: transparent;
  border: none;
  color: var(--muted);
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: background-color 0.2s, color 0.2s;
}
.delete-btn:hover {
  background: var(--sidebar-hover);
  color: #ff5d5d;
}
</style>
