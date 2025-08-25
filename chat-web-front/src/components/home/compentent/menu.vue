<script setup lang="ts">
import { onMounted, ref } from "vue";
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
const userStore = useUserStore();
const loading = ref(true);
const errorMsg = ref<string | null>(null);
const emit = defineEmits<{
  (e: 'selectSession', id: number): void
}>();
// 模拟新会话 ID 自增（真实环境应由后端返回）
let nextId = 1000;
const userId = userStore.userState?.id;
const fetchMenuList = async () => {
  if (!userId) {
    errorMsg.value = "用户未登录";
    loading.value = false;
    return;
  }
  try {
    const res = await getSessionList({ userId });
    menuList.value = res.data || [];

    if (menuList.value.length === 0) {
      errorMsg.value = "暂无会话";
    } else {
      // 默认选中第一个会话
      selectedId.value = menuList.value[0].id;
      emit('selectSession', selectedId.value); // ✅ 触发父组件更新
      nextId = Math.max(...menuList.value.map(i => i.id)) + 1;
    }
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
  emit('selectSession', selectedId.value)
};

// 新聊天逻辑
const handleNewChat = async () => {
  if (!userId) {
    console.warn("用户未登录，无法创建会话");
    return;
  }

  const payload = {
    name: new Date().toLocaleString(),
    userId,
  };

  try {
    // 创建新会话
     await createSession(payload);
    // 刷新列表
    await fetchMenuList();
    // 选中最新创建的会话（假设是最后一个）
    if (menuList.value.length > 0) {
      selectedId.value = menuList.value[menuList.value.length - 1].id;
      console.log("选中最新会话 ID:", selectedId.value);
      emit('selectSession', selectedId.value)

    }
  } catch (err) {
    console.error("创建 session 失败", err);
  }
};



onMounted(() => {
  fetchMenuList();
});



</script>

<template>
  <div class="menu-container">
    <!-- LOGO 区域 -->
    <div class="menu-logo">
      <span class="logo-text">AI 聊天</span>
    </div>

    <!-- 用户信息 -->
    <div class="userinfo">
      <img
          :src="userStore.userState?.avatar || 'https://via.placeholder.com/40'"
          alt="头像"
          class="user-avatar"
      />
      <span class="user-name">{{ userStore.userState?.name || '游客' }}</span>
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
          @click="handleClick(item)"
      >
        <div class="menu-item-icon">💬</div>
        <div class="menu-item-name">{{ item.name }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.menu-container {
  background-color: #ffffff;
  color: #333333;
  padding: 12px;
  height: 100%;
  overflow-y: auto;
  font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  border-right: 1px solid #ddd;
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
  font-weight: bold;
  color: #6f5fff;
  text-shadow: 0 0 4px #6f5fff;
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
  border: 2px solid #6f5fff;
  object-fit: cover;
  margin-bottom: 6px; /* 与名字间距 */
}

.user-name {
  font-size: 14px;
  font-weight: bold;
  color: #333;
  text-align: center;
  padding-bottom: 100px;
}

/* 新聊天按钮 */
.menu-header {
  margin-bottom: 12px;
  text-align: center;
}

.new-chat-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  background: linear-gradient(135deg, #6f5fff, #9d7cff);
  color: #ffffff;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.2s;
}
.new-chat-btn:hover {
  background: linear-gradient(135deg, #9d7cff, #6f5fff);
  box-shadow: 0 0 8px #6f5fff;
}

/* 会话列表 */
.menu-status {
  text-align: center;
  padding: 16px;
  color: #999;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.1s, box-shadow 0.2s;
}

.menu-item:hover {
  background-color: #f0f0ff;
  transform: translateX(2px);
  box-shadow: 0 0 6px #6f5fff;
}

.menu-item.selected {
  background-color: #e0e0ff;
  font-weight: bold;
  box-shadow: 0 0 8px #9d7cff;
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
</style>
