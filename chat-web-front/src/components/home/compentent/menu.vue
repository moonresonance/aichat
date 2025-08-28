<script setup lang="ts">
import { onMounted, ref, computed, watch } from "vue";
import { getSessionList } from "@/api/session";
import { useUserStore } from "@/stores/user";
import { createSession } from "@/api/session";
import { deleteSession } from "@/api/session";
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

const handleClick = (item: SessionItem) => {
  selectedId.value = item.id;
  console.log("点击了会话:", item);
  if (selectedId.value != null) emit("selectSession", selectedId.value);
};

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
    await createSession(payload);
    await fetchMenuList();
    if (menuList.value.length > 0) {
      selectedId.value = menuList.value[menuList.value.length - 1].id;
      if (selectedId.value != null) emit("selectSession", selectedId.value);
    }
  } catch (err) {
    console.error("创建 session 失败", err);
  }
};

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
    <!-- Header with Search and New Chat -->
    <div class="menu-header">
      <div class="search-bar">
        <span class="search-icon">🔍</span>
        <input type="text" placeholder="搜索" class="search-input" />
      </div>
      <button @click="handleNewChat" class="new-chat-icon" title="新聊天">
        <span>➕</span>
      </button>
    </div>

    <!-- Chat List -->
    <div class="chat-list">
      <div v-if="loading" class="menu-status">加载中...</div>
      <div v-else-if="errorMsg" class="menu-status">{{ errorMsg }}</div>
      <div v-else>
        <div
          v-for="item in menuList"
          :key="item.id"
          class="menu-item"
          :class="{ selected: selectedId === item.id }"
          @click="handleClick(item)"
        >
          <div class="menu-item-content">
            <div class="menu-item-name">{{ item.name }}</div>
            <div class="menu-item-detail">
              <span class="menu-item-index"
                >#{{ menuList.findIndex((s) => s.id === item.id) + 1 }}</span
              >
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

    <!-- Footer with User Info and Theme Toggle -->
    <div class="menu-footer">
      <div class="userinfo">
        <span class="user-name">{{ userStore.userState?.name || "游客" }}</span>
      </div>
      <button
        @click="toggleDark"
        class="theme-toggle"
        :title="isDark ? 'Light mode' : 'Dark mode'"
      >
        {{ isDark ? "☀️" : "🌙" }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.menu-container {
  background-color: var(--sidebar-bg);
  color: var(--sidebar-text);
  height: 100%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--sidebar-border);
  transition: background-color 0.3s ease, color 0.3s ease;
}

.menu-header {
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid var(--sidebar-border);
}

.search-bar {
  flex-grow: 1;
  display: flex;
  align-items: center;
  background-color: var(--sidebar-search-bg);
  border-radius: 20px;
  padding: 0 10px;
  margin-right: 10px;
}

.search-icon {
  font-size: 16px;
  color: var(--muted);
}

.search-input {
  border: none;
  background: transparent;
  color: var(--sidebar-text);
  padding: 8px 5px;
  width: 100%;
  outline: none;
}
.search-input::placeholder {
  color: var(--muted);
}

.new-chat-icon {
  background: none;
  border: none;
  color: var(--muted);
  cursor: pointer;
  font-size: 22px;
  padding: 5px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}
.new-chat-icon:hover {
  background-color: var(--sidebar-hover);
}

.chat-list {
  flex-grow: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.menu-status {
  text-align: center;
  padding: 16px;
  color: var(--muted);
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;
}

.menu-item:hover {
  background: var(--sidebar-hover);
}

.menu-item.selected {
  background: var(--sidebar-selected);
}

.menu-item-content {
  flex-grow: 1;
  overflow: hidden;
}

.menu-item-name {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.menu-item-detail {
  font-size: 13px;
  color: var(--muted);
}

.delete-btn {
  background: transparent;
  border: none;
  color: var(--muted);
  cursor: pointer;
  padding: 6px;
  border-radius: 50%;
  font-size: 16px;
  opacity: 0;
  transition: opacity 0.2s, color 0.2s;
}

.menu-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: #ff5d5d;
}

.menu-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  border-top: 1px solid var(--sidebar-border);
}

.userinfo {
  display: flex;
  align-items: center;
  gap: 10px;
  overflow: hidden;
}

.user-name {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.theme-toggle {
  background: transparent;
  border: none;
  color: var(--muted);
  cursor: pointer;
  font-size: 20px;
  padding: 5px;
  border-radius: 50%;
  transition: background-color 0.2s;
}
.theme-toggle:hover {
  background-color: var(--sidebar-hover);
}
</style>
