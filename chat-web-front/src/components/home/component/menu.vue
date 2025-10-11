<script setup lang="ts">
import {onMounted, ref, computed, watch, onBeforeUnmount} from "vue";
import { getSessionList, createSession, deleteSession } from "@/api/session";
import {addchat,deletechat} from "@/api/chatapi";
import { useUserStore } from "@/stores/user";
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
const searchQuery = ref("");
const userMenuOpen = ref(false);
const userBtnRef = ref<HTMLElement | null>(null);
const userMenuRef = ref<HTMLElement | null>(null);

const emit = defineEmits<{
  (e: "selectSession", id: number): void;
  (e: "deletedSession", id: number): void;
}>();

// ---------- 主题 ----------
const isDark = ref(false);
const applyDark = (val: boolean) => {
  const root = document.documentElement;
  if (val) {
    root.classList.add("dark");
    root.classList.remove("light");
  } else {
    root.classList.add("light");
    root.classList.remove("dark");
  }
  isDark.value = val;
  try {
    localStorage.setItem("darkMode", val ? "1" : "0");
  } catch {}
};
const initDark = () => {
  try {
    const saved = localStorage.getItem("darkMode");
    if (saved === "1" || saved === "0") {
      applyDark(saved === "1");
    } else {
      // 默认浅色，避免系统深色造成页面过暗
      applyDark(false);
    }
  } catch {
    applyDark(false);
  }
};
const toggleDark = () => applyDark(!isDark.value);

// ---------- 用户 ----------
const userId = computed(() => userStore.userState?.id ?? 0);

// ---------- 数据获取 ----------
const fetchMenuList = async () => {
  loading.value = true;
  errorMsg.value = null;

  if (!userId.value) {
    errorMsg.value = "用户未登录";
    menuList.value = [];
    loading.value = false;
    return;
  }

  try {
    const res = await getSessionList({ userId: userId.value });
    const list = (res?.data as SessionItem[]) || [];
    menuList.value = list;

    if (list.length === 0) {
      selectedId.value = null;
      errorMsg.value = "暂无会话";
    } else {
      // 保持原选中，若不存在则选第一个
      const keep =
        list.find((i) => i.id === selectedId.value)?.id ?? list[0].id;
      selectedId.value = keep;
      emit("selectSession", keep);
    }
    loadedOnce.value = true;
  } catch (e) {
    console.error(e);
    errorMsg.value = "获取会话列表失败";
  } finally {
    loading.value = false;
  }
};

// ---------- 操作 ----------
const handleClick = (item: SessionItem) => {
  if (selectedId.value === item.id) return;
  selectedId.value = item.id;
  emit("selectSession", item.id);
};

const handleNewChat = async () => {
  if (!userId.value) return;

  const payload = {
    name: `新对话 ${menuList.value.length + 1}`,
    userId: userId.value,
  };

  try {
    // 创建会话
    const res: any = await createSession(payload);
    await fetchMenuList();

    if (menuList.value.length > 0) {
      const last = menuList.value[menuList.value.length - 1].id;
      selectedId.value = last;
      emit("selectSession", last);

      // ✅ 插入 AI 开场白
      const aiMessageContent = "欢迎使用幻想AI，很高兴为你服务！";
      try {
        const savedAI = await addchat({
          userId: userId.value,
          sessionId: last,
          role: "ai",
          content: aiMessageContent,
        });
      } catch (err) {
        console.error("保存开场白失败:", err);
      }
    }
  } catch (err) {
    console.error("创建会话失败", err);
  }
};


const handleDelete = async (id: number) => {
  if (!confirm("确定要删除该会话吗？此操作不可恢复。")) return;

  try {
    // 先删除该会话下的所有聊天内容
    await deletechat({ session_id: id });
    // 再删除会话本身
    await deleteSession({ id });
    // 更新前端会话列表
    menuList.value = menuList.value.filter((i) => i.id !== id);
    // 如果当前选中的是被删除的会话，切换到下一个
    if (selectedId.value === id) {
      const next = menuList.value[0]?.id ?? null;
      selectedId.value = next;
      if (next != null) emit("selectSession", next);


    emit("deletedSession", id);

    if (menuList.value.length === 0) {
      errorMsg.value = "暂无会话";
    }
  }
  }catch (err){
    console.error("删除失败", err);
  }
};


// 点击外部关闭
const onDocClick = (e: MouseEvent) => {
  const t = e.target as Node;
  if (userMenuOpen.value) {
    if (!userBtnRef.value?.contains(t) && !userMenuRef.value?.contains(t)) {
      userMenuOpen.value = false;
    }
  }
};

// 键盘交互：Esc 关闭
const onDocKey = (e: KeyboardEvent) => {
  if (e.key === "Escape" && userMenuOpen.value) {
    userMenuOpen.value = false;
  }
};

// 切换菜单
const toggleUserMenu = () => {
  userMenuOpen.value = !userMenuOpen.value;
  if (userMenuOpen.value) {
    // 下一帧聚焦第一个菜单项
    requestAnimationFrame(() => {
      const el =
        userMenuRef.value?.querySelector<HTMLElement>("[data-menuitem]");
      el?.focus();
    });
  }
};

// 无障碍键盘导航（上下/回车）
const onUserMenuKeydown = (e: KeyboardEvent) => {
  const items = Array.from(
    userMenuRef.value?.querySelectorAll<HTMLElement>("[data-menuitem]") ?? []
  );
  if (!items.length) return;

  const idx = items.findIndex((el) => el === document.activeElement);
  if (e.key === "ArrowDown") {
    e.preventDefault();
    const next = items[(idx + 1 + items.length) % items.length];
    next.focus();
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    const prev = items[(idx - 1 + items.length) % items.length];
    prev.focus();
  } else if (e.key === "Enter" || e.key === " ") {
    (document.activeElement as HTMLElement)?.click();
  }
};

// 行为：设置、退出
const goSettings = () => {
  userMenuOpen.value = false;
  router.push({ name: "settings" }); // 改成你的路由
};
const logout = async () => {
  userMenuOpen.value = false;
  try {
    await userStore.logout?.(); // 若无该方法，请替换为你的登出逻辑
  } finally {
    router.replace({ name: "login" }); // 改成你的路由
  }
};

onMounted(() => {
  document.addEventListener("click", onDocClick);
  document.addEventListener("keydown", onDocKey);
});
onBeforeUnmount(() => {
  document.removeEventListener("click", onDocClick);
  document.removeEventListener("keydown", onDocKey);
});
// ---------- 过滤 ----------
const normalized = (s: string) => s.toLowerCase().trim();
const filteredList = computed(() => {
  const q = normalized(searchQuery.value);
  if (!q) return menuList.value;
  return menuList.value.filter((i) => normalized(i.name).includes(q));
});

// 用户登录后首次加载
watch(
  () => userId.value,
  (val) => {
    if (val && !loadedOnce.value) fetchMenuList();
  },
  { immediate: true }
);

onMounted(() => {
  initDark();
});
</script>

<template>
  <div class="menu-container">
    <!-- Header -->
    <div class="menu-header">
      <div class="search-bar">
        <!-- 放大镜（线条） -->
        <svg
          class="icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <circle cx="11" cy="11" r="7"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input
          type="text"
          placeholder="搜索"
          class="search-input"
          v-model="searchQuery"
          aria-label="搜索会话"
        />
      </div>

      <!-- 新建（线条） -->
      <button
        @click="handleNewChat"
        class="icon-btn"
        title="新聊天"
        aria-label="新建聊天"
      >
        <svg
          class="icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
      </button>
    </div>

    <!-- Chat List -->
    <div class="chat-list">
      <div v-if="loading" class="menu-status">加载中...</div>
      <div v-else-if="errorMsg" class="menu-status">{{ errorMsg }}</div>
      <div v-else>
        <div
          v-for="(item, idx) in filteredList"
          :key="item.id"
          class="menu-item"
          :class="{ selected: selectedId === item.id }"
          @click="handleClick(item)"
        >
          <div class="menu-item-content">
            <div class="menu-item-name" :title="item.name">{{ item.name }}</div>
            <div class="menu-item-detail">
              <span class="menu-item-index">#{{ idx + 1 }}</span>
            </div>
          </div>

          <!-- 删除（线条） -->
          <button
            class="delete-btn"
            @click.stop="handleDelete(item.id)"
            title="删除"
            aria-label="删除会话"
          >
            <svg
              class="icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"></path>
              <path d="M10 11v6"></path>
              <path d="M14 11v6"></path>
              <path d="M9 6V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"></path>
            </svg>
          </button>
        </div>

        <div v-if="!filteredList.length" class="menu-status">无匹配会话</div>
      </div>
    </div>

    <!-- Footer -->
    <div class="menu-footer">
      <!-- 用户菜单 -->
      <div class="user-menu-container">
        <button
          ref="userBtnRef"
          @click="toggleUserMenu"
          @keydown.enter="toggleUserMenu"
          @keydown.space.prevent="toggleUserMenu"
          class="user-btn"
          :aria-expanded="userMenuOpen"
          aria-haspopup="true"
        >
          <div class="user-avatar">
            <svg
              class="icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
          <span class="user-name" :title="userStore.userState?.name || '游客'">
            {{ userStore.userState?.name || "游客" }}
          </span>
          <svg
            class="dropdown-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </button>

        <!-- 下拉菜单 -->
        <div
          v-if="userMenuOpen"
          ref="userMenuRef"
          @keydown="onUserMenuKeydown"
          class="user-dropdown"
          role="menu"
          aria-orientation="vertical"
        >
          <button
            @click="goSettings"
            data-menuitem
            class="dropdown-item"
            role="menuitem"
            tabindex="0"
          >
            <svg
              class="icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M12 1v6m0 6v6"></path>
              <path d="m15.5 3.5-3.5 3.5-3.5-3.5"></path>
              <path d="m15.5 20.5-3.5-3.5-3.5 3.5"></path>
            </svg>
            设置
          </button>

          <div class="dropdown-divider"></div>

          <button
            @click="logout"
            data-menuitem
            class="dropdown-item danger"
            role="menuitem"
            tabindex="0"
          >
            <svg
              class="icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            退出登录
          </button>
        </div>
      </div>

      <!-- 主题切换（线条太阳/月亮） -->
      <button
        @click="toggleDark"
        class="icon-btn"
        :title="isDark ? '切换为浅色' : '切换为深色'"
        :aria-label="isDark ? '切换为浅色' : '切换为深色'"
      >
        <svg
          v-if="isDark"
          class="icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <!-- Sun -->
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
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <!-- Moon -->
          <path d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79z"></path>
        </svg>
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
  gap: 8px;
  border-bottom: 1px solid var(--sidebar-border);
}

.search-bar {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  background-color: var(--sidebar-search-bg);
  border-radius: 20px;
  padding: 0 10px;
}

.icon {
  width: 18px;
  height: 18px;
  display: inline-block;
}

.search-input {
  border: none;
  background: transparent;
  color: var(--sidebar-text);
  padding: 8px 5px;
  width: 100%;
  outline: none;
  font-size: 14px;
}
.search-input::placeholder {
  color: var(--muted);
}

.icon-btn {
  background: none;
  border: 1px solid var(--sidebar-border);
  color: var(--muted);
  cursor: pointer;
  padding: 6px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s, color 0.2s, border-color 0.2s;
}
.icon-btn:hover {
  background-color: var(--sidebar-hover);
  color: var(--text-primary);
  border-color: var(--sidebar-hover);
}

.chat-list {
  flex: 1;
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
  flex: 1;
  min-width: 0;
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
  border: 1px solid var(--sidebar-border);
  color: var(--muted);
  cursor: pointer;
  padding: 6px;
  border-radius: 8px;
  font-size: 0;
  opacity: 0;
  transition: opacity 0.2s, color 0.2s, background-color 0.2s, border-color 0.2s;
}
.menu-item:hover .delete-btn {
  opacity: 1;
}
.delete-btn:hover {
  background-color: var(--sidebar-hover);
  color: var(--text-primary);
  border-color: var(--sidebar-hover);
}

.menu-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  border-top: 1px solid var(--sidebar-border);
}

/* 用户菜单 */
.user-menu-container {
  position: relative;
  flex: 1;
}

.user-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 12px;
  background: transparent;
  border: 1px solid var(--sidebar-border);
  border-radius: 8px;
  color: var(--sidebar-text);
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.user-btn:hover {
  background-color: var(--sidebar-hover);
  border-color: var(--sidebar-hover);
}

.user-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: var(--sidebar-selected);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-name {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.dropdown-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  transition: transform 0.2s;
}

.user-btn[aria-expanded="true"] .dropdown-icon {
  transform: rotate(180deg);
}

.user-dropdown {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  background-color: var(--sidebar-bg);
  border: 1px solid var(--sidebar-border);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  margin-bottom: 8px;
  overflow: hidden;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 12px 16px;
  background: transparent;
  border: none;
  color: var(--sidebar-text);
  cursor: pointer;
  transition: background-color 0.2s;
  text-align: left;
  font-size: 14px;
}

.dropdown-item:hover {
  background-color: var(--sidebar-hover);
}

.dropdown-item:focus {
  background-color: var(--sidebar-hover);
  outline: none;
}

.dropdown-item.danger {
  color: #ef4444;
}

.dropdown-item.danger:hover {
  background-color: #ef4444;
  color: white;
}

.dropdown-divider {
  height: 1px;
  background-color: var(--sidebar-border);
  margin: 4px 0;
}

/* === Telegram-inspired sidebar/menu styling overrides === */
.menu-container {
  --tg-accent: #2a9df4;
  --tg-subtle: #f2f5f8;
  --tg-pressed: #e4eef8;
  --tg-text: #0f1419;
  --tg-subtext: #6b7280;
  background: #ffffff;
  color: var(--tg-text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans CJK SC", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

.menu-header {
  background: #ffffff;
  border-bottom: 1px solid rgba(0,0,0,.06);
  padding: 10px 12px;
}

.search-bar {
  background: var(--tg-subtle);
  border: 1px solid rgba(0,0,0,.06);
  border-radius: 14px;
}

.search-input {
  font-size: 14px;
}

.icon-btn {
  border-radius: 999px;
  background: #ffffff;
  border: 1px solid rgba(0,0,0,.06);
}

.chat-list {
  padding: 6px;
}

.menu-item {
  border-radius: 14px;
  padding: 10px 12px;
  transition: background .15s ease;
}

.menu-item:hover {
  background: var(--tg-subtle);
}

.menu-item.selected {
  background: var(--tg-pressed);
  border: 1px solid rgba(42,157,244,.25);
}

.menu-item-name {
  font-weight: 600;
  font-size: 15px;
  color: var(--tg-text);
}

.menu-item-detail {
  color: var(--tg-subtext);
  font-size: 12px;
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