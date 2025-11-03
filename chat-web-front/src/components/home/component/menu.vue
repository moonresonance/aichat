<script setup lang="ts">
import {onMounted, ref, computed, watch, onBeforeUnmount} from "vue";
import { getSessionList, createSession, deleteSession } from "@/api/session";
import {addchat,deletechat} from "@/api/chatapi";
import { useUserStore } from "@/stores/user";
import router from "@/router";
import ThemeToggle from "@/components/common/ThemeToggle.vue";

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
    // 先删除该会话下的所有聊天记录
    try {
      const deleteRes = await deletechat({ session_id: id });
      console.log("删除聊天记录结果:", deleteRes);
    } catch (err) {
      console.warn("删除聊天记录时出错:", err);
      // 继续删除会话，不中断流程
    }

    // 再删除会话本身
    const sessionRes = await deleteSession({ id });
    console.log("删除会话结果:", sessionRes);

    // 从列表中移除
    menuList.value = menuList.value.filter((i) => i.id !== id);

    // 如果删除的是当前选中的会话，切换到下一个
    if (selectedId.value === id) {
      const next = menuList.value[0]?.id ?? null;
      selectedId.value = next;
      if (next != null) {
        emit("selectSession", next);
      }
    }

    emit("deletedSession", id);

    if (menuList.value.length === 0) {
      errorMsg.value = "暂无会话";
    }

    console.log("删除会话成功");
  } catch (err) {
    console.error("删除会话失败:", err);
    alert("删除会话失败，请重试");
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
      <ThemeToggle dense />

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

    </div>
  </div>
</template>

<style scoped>
.menu-container {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans CJK SC", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
  background: transparent;
  border-right: 1px solid var(--sidebar-border);
  backdrop-filter: blur(50px) saturate(200%) brightness(105%);
  -webkit-backdrop-filter: blur(50px) saturate(200%) brightness(105%);
  transition: background 0.3s ease, border-color 0.3s ease;
  animation: sidebarSlideIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  overflow: hidden;
}

[data-theme="dark"] .menu-container {
  backdrop-filter: blur(60px) saturate(220%) contrast(110%);
  -webkit-backdrop-filter: blur(60px) saturate(220%) contrast(110%);
  border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* 星空背景 */
.menu-container::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background-image:
    radial-gradient(1px 1px at 15% 25%, rgba(255, 255, 255, 0.9), transparent),
    radial-gradient(1px 1px at 85% 15%, rgba(255, 255, 255, 0.85), transparent),
    radial-gradient(2px 2px at 45% 65%, rgba(255, 255, 255, 0.95), transparent),
    radial-gradient(1px 1px at 25% 85%, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(1px 1px at 65% 45%, rgba(255, 255, 255, 0.75), transparent),
    radial-gradient(1px 1px at 92% 72%, rgba(255, 255, 255, 0.7), transparent),
    radial-gradient(2px 2px at 8% 58%, rgba(255, 255, 255, 0.85), transparent),
    radial-gradient(1px 1px at 48% 18%, rgba(255, 255, 255, 0.9), transparent),
    radial-gradient(1px 1px at 72% 88%, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(1px 1px at 35% 42%, rgba(255, 255, 255, 0.75), transparent),
    radial-gradient(1px 1px at 18% 62%, rgba(255, 255, 255, 0.85), transparent),
    radial-gradient(1px 1px at 58% 8%, rgba(255, 255, 255, 0.7), transparent),
    radial-gradient(2px 2px at 78% 38%, rgba(255, 255, 255, 0.9), transparent),
    radial-gradient(1px 1px at 12% 48%, rgba(255, 255, 255, 0.75), transparent),
    radial-gradient(1px 1px at 95% 55%, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(1px 1px at 38% 78%, rgba(255, 255, 255, 0.85), transparent),
    radial-gradient(1px 1px at 5% 22%, rgba(255, 255, 255, 0.7), transparent),
    radial-gradient(2px 2px at 68% 92%, rgba(255, 255, 255, 0.95), transparent);
  background-size: 280px 280px, 320px 320px, 240px 240px, 360px 360px, 300px 300px,
                   260px 260px, 340px 340px, 220px 220px, 380px 380px, 290px 290px,
                   310px 310px, 270px 270px, 330px 330px, 250px 250px, 350px 350px,
                   230px 230px, 400px 400px, 210px 210px;
  background-repeat: repeat;
  opacity: 0;
  transition: opacity 0.5s ease;
}

[data-theme="dark"] .menu-container::before {
  opacity: 1;
  animation: starTwinkle 4s ease-in-out infinite;
}

/* 添加第二层闪烁星星 */
.menu-container::after {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background-image:
    radial-gradient(1px 1px at 22% 38%, rgba(255, 255, 255, 0.9), transparent),
    radial-gradient(1px 1px at 78% 62%, rgba(255, 255, 255, 0.85), transparent),
    radial-gradient(1px 1px at 52% 78%, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(2px 2px at 12% 12%, rgba(255, 255, 255, 0.95), transparent),
    radial-gradient(1px 1px at 88% 28%, rgba(255, 255, 255, 0.75), transparent),
    radial-gradient(1px 1px at 42% 92%, rgba(255, 255, 255, 0.85), transparent),
    radial-gradient(1px 1px at 62% 32%, rgba(255, 255, 255, 0.7), transparent),
    radial-gradient(2px 2px at 28% 68%, rgba(255, 255, 255, 0.9), transparent),
    radial-gradient(1px 1px at 82% 8%, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(1px 1px at 8% 82%, rgba(255, 255, 255, 0.75), transparent),
    radial-gradient(1px 1px at 55% 52%, rgba(255, 255, 255, 0.85), transparent),
    radial-gradient(1px 1px at 32% 15%, rgba(255, 255, 255, 0.7), transparent),
    radial-gradient(2px 2px at 95% 45%, rgba(255, 255, 255, 0.95), transparent),
    radial-gradient(1px 1px at 2% 35%, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(1px 1px at 75% 75%, rgba(255, 255, 255, 0.85), transparent);
  background-size: 310px 310px, 270px 270px, 350px 350px, 230px 230px, 330px 330px, 
                   250px 250px, 390px 390px, 215px 215px, 295px 295px, 370px 370px,
                   240px 240px, 325px 325px, 265px 265px, 410px 410px, 200px 200px;
  background-repeat: repeat;
  opacity: 0;
  transition: opacity 0.5s ease;
}

[data-theme="dark"] .menu-container::after {
  opacity: 1;
  animation: starTwinkle 3.5s ease-in-out infinite 0.8s;
}

@keyframes starTwinkle {
  0%, 100% { 
    opacity: 0.85;
    filter: brightness(1.1);
  }
  50% { 
    opacity: 1;
    filter: brightness(1.35);
  }
}

.menu-container > * {
  position: relative;
  z-index: 1;
}

@keyframes sidebarSlideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.menu-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 18px 14px;
  border-bottom: 1px solid var(--sidebar-border);
  background: transparent;
}

.search-bar {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 14px;
  background: var(--sidebar-search-bg);
  border: 1px solid rgba(42, 157, 244, 0.07);
  box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.6);
}

.icon {
  width: 18px;
  height: 18px;
  display: inline-block;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  color: var(--sidebar-text);
  font-size: 14px;
  outline: none;
}

.search-input::placeholder {
  color: var(--muted);
}

.icon-btn {
  width: 40px;
  height: 40px;
  border-radius: 16px;
  border: 1px solid transparent;
  background: var(--sidebar-elev);
  color: var(--muted);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, color 0.2s ease, border 0.2s ease;
  box-shadow: 0 4px 12px rgba(42, 157, 244, 0.08);
  animation: buttonBounce 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes buttonBounce {
  0% {
    opacity: 0;
    transform: scale(0.3) translateY(8px);
  }
  60% {
    transform: scale(1.08);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.icon-btn:hover {
  color: var(--accent-color);
  border-color: rgba(42, 157, 244, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(42, 157, 244, 0.14);
}

.icon-btn:hover svg {
  animation: iconSpin 0.6s ease-in-out;
}

@keyframes iconSpin {
  0% { transform: rotate(0deg) scale(1); }
  50% { transform: rotate(180deg) scale(1.15); }
  100% { transform: rotate(360deg) scale(1); }
}

.chat-list {
  flex: 1;
  padding: 14px 18px 18px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.chat-list::-webkit-scrollbar {
  width: 6px;
}

.chat-list::-webkit-scrollbar-thumb {
  background: rgba(42, 157, 244, 0.25);
  border-radius: 999px;
}

.menu-status {
  text-align: center;
  padding: 24px 0;
  color: var(--muted);
  font-size: 14px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 18px;
  background: transparent;
  border: 1px solid transparent;
  cursor: pointer;
  transition: background 0.2s ease, border 0.2s ease, transform 0.18s ease;
  position: relative;
  animation: itemFadeInLeft 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  animation-fill-mode: both;
}

/* 为不同的菜单项设置不同的延迟 */
.menu-item:nth-child(1) { animation-delay: 0.05s; }
.menu-item:nth-child(2) { animation-delay: 0.1s; }
.menu-item:nth-child(3) { animation-delay: 0.15s; }
.menu-item:nth-child(4) { animation-delay: 0.2s; }
.menu-item:nth-child(5) { animation-delay: 0.25s; }

@keyframes itemFadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-12px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.menu-item:hover {
  background: var(--sidebar-hover);
}

.menu-item:hover::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 18px;
  background: radial-gradient(circle at 50% 50%, rgba(42, 157, 244, 0.1), transparent);
  animation: hoverGlow 0.6s ease-out;
  pointer-events: none;
  z-index: -1;
}

@keyframes hoverGlow {
  from {
    opacity: 1;
    transform: scale(0.8);
  }
  to {
    opacity: 0;
    transform: scale(1.2);
  }
}

.menu-item.selected {
  background: var(--sidebar-selected);
  border: 1px solid rgba(42, 157, 244, 0.28);
  box-shadow: 0 8px 24px rgba(42, 157, 244, 0.18);
  transform: translateY(-1px);
}

.menu-item-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.menu-item-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--sidebar-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.menu-item-detail {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--muted);
}

.menu-item-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--accent-ghost);
  color: var(--accent-color);
  font-size: 12px;
  font-weight: 500;
}

.delete-btn {
  width: 36px;
  height: 36px;
  border-radius: 14px;
  border: 1px solid rgba(42, 157, 244, 0.06);
  background: rgba(42, 157, 244, 0.05);
  color: rgba(42, 157, 244, 0.6);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease, transform 0.2s ease, color 0.2s ease, border 0.2s ease;
  cursor: pointer;
  pointer-events: auto;
  z-index: 10;
  flex-shrink: 0;
}

.menu-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: #fff;
  background: linear-gradient(135deg, #ff6b6b, #f05454);
  border-color: rgba(255, 107, 107, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 10px 20px rgba(240, 84, 84, 0.25);
}

.menu-footer {
  padding: 16px 18px;
  border-top: 1px solid var(--sidebar-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  background: transparent;
}

.user-menu-container {
  position: relative;
  flex: 1;
}

.user-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 16px;
  background: var(--sidebar-elev);
  border: 1px solid rgba(42, 157, 244, 0.08);
  color: var(--sidebar-text);
  cursor: pointer;
  transition: box-shadow 0.2s ease, transform 0.2s ease, border 0.2s ease;
  box-shadow: var(--shadow-soft);
  text-align: left;
  animation: userBtnSlide 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes userBtnSlide {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-btn:hover {
  transform: translateY(-1px);
  border-color: rgba(42, 157, 244, 0.25);
  box-shadow: 0 12px 24px rgba(42, 157, 244, 0.15);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(42, 157, 244, 0.25), rgba(126, 214, 223, 0.45));
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent);
}

.user-name {
  flex: 1;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-icon {
  width: 16px;
  height: 16px;
  transition: transform 0.2s ease;
}

.user-btn[aria-expanded="true"] .dropdown-icon {
  transform: rotate(180deg);
}

.user-dropdown {
  position: absolute;
  bottom: calc(100% + 12px);
  left: 0;
  right: 0;
  background: var(--sidebar-elev);
  border-radius: 18px;
  border: 1px solid rgba(42, 157, 244, 0.08);
  box-shadow: 0 18px 32px rgba(15, 23, 42, 0.18);
  overflow: hidden;
  animation: dropdownFade 0.18s ease;
}

@keyframes dropdownFade {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  background: transparent;
  border: none;
  font-size: 14px;
  color: var(--sidebar-text);
  cursor: pointer;
  transition: background 0.18s ease, color 0.18s ease;
}

.dropdown-item:hover,
.dropdown-item:focus {
  outline: none;
  background: var(--sidebar-hover);
}

.dropdown-item.danger {
  color: #f87171;
}

.dropdown-item.danger:hover {
  background: rgba(248, 113, 113, 0.12);
  color: #f43f5e;
}

.dropdown-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(15, 23, 42, 0.08), transparent);
}

.unread-badge {
  margin-left: auto;
  padding: 2px 8px;
  border-radius: 12px;
  background: var(--accent);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
}

@media (max-width: 768px) {
  .menu-container {
    border-right: none;
    border-bottom: 1px solid var(--sidebar-border);
  }

  .menu-header {
    padding: 14px;
  }

  .chat-list {
    padding: 12px 14px;
  }
}

</style>