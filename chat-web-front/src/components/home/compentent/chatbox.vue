<template>
  <div class="chat-wrapper">
    <main class="chat-main" ref="scrollContainer">
      <transition-group name="message" tag="div" class="chat-messages">
        <div
          v-for="m in messages"
          :key="m.id"
          :class="['message-item', m.sender]"
        >
          <div class="message-content-wrapper">
            <div class="message-content" :class="m.sender">
              <div v-if="m.think && showThink" class="message-think">
                思考: {{ m.think }}
              </div>
              <div v-if="m.sender === 'user'" class="message-answer">
                {{ m.content }}
              </div>
              <div
                v-else
                class="message-answer ai"
                v-html="m.html || safeRender(m.content)"
              ></div>
            </div>
            <div v-if="m.sender === 'ai'" class="message-actions">
              <button class="act-btn" @click="copyMessage(m)">⧉</button>
              <button
                class="act-btn"
                v-if="isLastAI(m) && !isGenerating"
                @click="regenerate(m)"
              >
                ↻
              </button>
            </div>
          </div>
        </div>
      </transition-group>
    </main>
    <div class="chat-input-area">
      <div class="chat-input-container">
        <textarea
          v-model="messageInput"
          @keyup.enter.prevent="sendMessage"
          class="message-input"
          placeholder="输入消息..."
          :disabled="props.sessionId === null"
          rows="1"
          @input="autoResize"
          ref="textarea"
        ></textarea>
      </div>
      <button
        v-if="!isGenerating"
        class="send-button"
        @click="sendMessage"
        :disabled="
          props.sessionId === null || isGenerating || !messageInput.trim()
        "
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <line x1="22" y1="2" x2="11" y2="13"></line>
          <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
        </svg>
      </button>
      <button v-else class="send-button stop" @click="stopGeneration">▢</button>
    </div>
    <!-- 回到底部按钮：离开底部且有新消息时显示 -->
    <button
      class="scroll-bottom-btn"
      :class="{ show: showScrollToBottom }"
      @click="handleScrollToBottom"
      aria-label="回到底部"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        width="24"
        height="24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <!-- 线条风格双箭头向下 -->
        <path d="M6 8l6 6 6-6" />
        <path d="M6 4l6 6 6-6" />
        <!-- 底部基线 -->
        <line x1="4" y1="20" x2="20" y2="20" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import {
  ref,
  reactive,
  watch,
  nextTick,
  computed,
  onMounted,
  onUnmounted,
} from "vue";
import { marked } from "marked";
import hljs from "highlight.js/lib/common";
import "highlight.js/styles/github-dark.css";
import { ElMessage } from "element-plus";
import { chatbyqwen3, getchatlist ,addchat} from "@/api/chatapi";
import { useUserStore } from "@/stores/user";

interface Message {
  id: number;
  content: string; // raw text
  sender: "user" | "ai";
  timestamp: Date;
  think: string;
  html?: string; // rendered markdown (AI only)
}

const userStore = useUserStore();

const props = defineProps<{
  sessionId: number | null;
  userId: number | null;
}>();

const messages = ref<Message[]>([
  {
    id: Date.now(),
    content: props.sessionId
      ? `欢迎进入会话 ${props.sessionId}`
      : "请选择会话开始聊天",
    sender: "ai",
    timestamp: new Date(),
    think: "",
  },
]);

const formatTime = (date: Date) => {
  if (!date) return "";
  return date.toLocaleTimeString("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
  });
};

const messageInput = ref("");
const context = ref<string[]>([]);
const showThink = ref(true);
const customPrompt = ref("你是一个智能助手");
const isGenerating = ref(false);
let answerInterval: any = null;
let thinkAnimation: any = null;
const textarea = ref<HTMLTextAreaElement | null>(null);

// 滚动容器（聊天主体）
const scrollContainer = ref<HTMLElement | null>(null);

const autoResize = () => {
  if (textarea.value) {
    textarea.value.style.height = "auto";
    const newHeight = Math.min(200, Math.max(36, textarea.value.scrollHeight));
    textarea.value.style.height = `${newHeight}px`;

    // 更新父容器的高度
    const container = textarea.value.closest(".chat-input-container");
    if (container) {
      (container as HTMLElement).style.height = `${newHeight}px`;
    }
  }
};

const highlightBlocks = () => {
  nextTick(() => {
    document
      .querySelectorAll(".message-answer.ai pre code")
      .forEach((el: any) => hljs.highlightElement(el));
  });
};

const isLastAI = (msg: Message) => {
  const list = messages.value.filter((v) => v.sender === "ai");
  return list.length > 0 && list[list.length - 1] === msg;
};

// 平滑滚动到底部
const getScrollEl = () =>
  scrollContainer.value ||
  (document.querySelector(".chat-main") as HTMLElement | null);

const scrollToBottom = () => {
  setTimeout(() => {
    const container = getScrollEl();
    if (container) {
      container.scrollTo({
        top: container.scrollHeight,
        behavior: "smooth",
      });
    }
  });
};

// 立即滚动到底部(不使用平滑效果，确保AI回答时内容实时可见)
const immediateScrollToBottom = () => {
  const container = getScrollEl();
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
};

// 回到底部按钮显示控制
const showScrollToBottom = ref(false); // 控制按钮显隐
const newMessagesPending = ref(false); // 离开底部后是否有新消息

const isAtBottom = (el: HTMLElement, threshold = 12) => {
  return el.scrollHeight - el.scrollTop - el.clientHeight <= threshold;
};

const recomputeScrollButton = () => {
  const el = getScrollEl();
  if (!el) return;
  const atBottom = isAtBottom(el);
  if (atBottom) {
    newMessagesPending.value = false;
    showScrollToBottom.value = false;
  } else {
    // 新需求：只要离开底部就展示按钮（不再限制必须有新消息或正在生成）
    showScrollToBottom.value = true;
  }
  shouldAutoScroll = atBottom; // 同步原有逻辑
};

const handleScrollToBottom = () => {
  const el = getScrollEl();
  if (!el) return;
  scrollToBottom();
  newMessagesPending.value = false;
  showScrollToBottom.value = false;
};

// 监听会话切换
// ✅ 切换会话时，从数据库拉历史消息
watch(
    () => props.sessionId,
    async (newId) => {
      if (newId == null) {
        messages.value = [
          {
            id: Date.now(),
            content: "已删除或未选中会话，请选择或新建会话",
            sender: "ai",
            timestamp: new Date(),
            think: "",
          },
        ];
      } else {
        try{
          const resp: any = await getchatlist({
            userId: props.userId,
            sessionId: newId,
          });
          if(resp.data.length > 0){
            messages.value = resp.data.map((item: any) => ({
              id: item.id,
              content: item.content,
              sender: item.role === "user" ? "user" : "ai",
              timestamp: new Date(),
              think: "",
              html: item.role === "ai" ? marked.parse(item.content) : undefined,
            }));
          }else {
            messages.value = [
              {
                id: Date.now(),
                content: `欢迎使用幻想ai,很高兴为你服务`,
                sender: "ai",
                timestamp: new Date(),
                think: "",
              },
            ];
          }
        }
        catch(e){
          console.error("获取聊天记录失败:", e);
          messages.value = [
            {
              id: Date.now(),
              content: `进入会话 ${newId}，但加载历史失败`,
              sender: "ai",
              timestamp: new Date(),
              think: "",
            },
          ];
        }
      }
      scrollToBottom();
    }
);

// 监听输入内容变化，自动调整高度
watch(messageInput, () => {
  nextTick(() => {
    autoResize();
  });
});

// 组件挂载后初始化
onMounted(() => {
  nextTick(() => {
    autoResize();
    const el = getScrollEl();
    if (el) {
      el.addEventListener("scroll", () => {
        recomputeScrollButton();
      });
      immediateScrollToBottom();
    }
  });
});

// 自动下滑功能
const handleScroll = () => {
  const container = getScrollEl();
  if (!container) return;
  const nearBottom =
    container.scrollHeight - container.scrollTop - container.clientHeight < 100;
  if (nearBottom) immediateScrollToBottom();
};

// 是否应该自动滚动
let shouldAutoScroll = true;

// 添加消息变化监听，以便在内容变化时自动滚动
watch(
  () => messages.value.length,
  () => {
    const el = getScrollEl();
    if (shouldAutoScroll) {
      immediateScrollToBottom();
    } else if (el && !isAtBottom(el)) {
      // 离开底部新增消息
      newMessagesPending.value = true;
      recomputeScrollButton();
    }
  }
);

// 组件卸载时清理
onUnmounted(() => {
  const el = getScrollEl();
  if (el) el.removeEventListener("scroll", handleScroll);
});

const stopGeneration = () => {
  if (answerInterval) {
    clearInterval(answerInterval);
    answerInterval = null;
  }
  if (thinkAnimation) {
    clearInterval(thinkAnimation);
    thinkAnimation = null;
  }
  isGenerating.value = false;
};

const regenerate = async (aiMsg: Message) => {
  if (isGenerating.value) return;

  const idx = messages.value.indexOf(aiMsg);
  const prevUser = [...messages.value.slice(0, idx)]
      .reverse()
      .find((m) => m.sender === "user");

  if (!prevUser) {
    ElMessage.warning("无可重生的问题");
    return;
  }

  // 重置 AI 消息
  aiMsg.content = "";
  aiMsg.html = "";
  aiMsg.think = "AI 正在思考";
  isGenerating.value = true;

  // 思考动画
  let dot = 0;
  thinkAnimation = setInterval(() => {
    aiMsg.think = "AI 正在思考" + ".".repeat(dot % 4);
    dot++;
  }, 500);

  try {
    // 调用 AI 接口
    const resp: any = await chatbyqwen3({
      userId: props.userId,
      sessionId:props.sessionId,
      question: prevUser.content,
      prompt: customPrompt.value,
      stream: true,
    });
    clearInterval(thinkAnimation);

    // 解析 AI 返回
    const raw = resp?.answer || resp?.data?.answer || resp;
    let thinkText = "";
    let answerText = "";
    if (typeof raw === "string") {
      const m = raw.match(/<think>([\s\S]*?)<\/think>/);
      thinkText = m ? m[1].trim() : "";
      answerText = raw.replace(/<think>[\s\S]*?<\/think>/, "").trim();
    } else {
      answerText = JSON.stringify(raw);
    }

    aiMsg.think = thinkText;

    // ✅ 保存 AI 消息到数据库
    try {
      const savedAI = await addchat({
        userId: props.userId!,
        sessionId: props.sessionId!,
        role: "ai",
        content: answerText,
      });
      if (savedAI?.data?.id) {
        aiMsg.id = savedAI.data.id; // 替换临时 id
      }
    } catch (err) {
      console.error("保存 AI 消息失败:", err);
    }

    // 流式逐字显示 AI 回复
    let i = 0;
    answerInterval = setInterval(() => {
      if (i >= answerText.length) {
        clearInterval(answerInterval);
        answerInterval = null;
        trimLeading(aiMsg);
        isGenerating.value = false;
        highlightBlocks();
        return;
      }
      aiMsg.content += answerText[i];
      aiMsg.html = safeRender(aiMsg.content);
      i++;
      highlightBlocks();

      const el = getScrollEl();
      if (el && !isAtBottom(el)) {
        newMessagesPending.value = true;
        recomputeScrollButton();
      }
    }, 20);
  } catch (e: any) {
    clearInterval(thinkAnimation);
    aiMsg.think = "";
    aiMsg.content = "重新生成失败: " + e.message;
    aiMsg.html = safeRender(aiMsg.content);
    isGenerating.value = false;
  }
};


// 发送消息
const sendMessage = async () => {
  if (props.sessionId === null || props.userId === null) return;
  const question = messageInput.value.trim();
  if (!question) return;

  // 前端临时消息
  const userMessage: Message = {
    id: Date.now(), // 临时 id
    content: question,
    sender: "user",
    timestamp: new Date(),
    think: "",
  };
  messages.value.push(userMessage);
  messageInput.value = "";

  nextTick(() => {
    if (textarea.value) {
      textarea.value.style.height = "36px";
      const container = textarea.value.closest(".chat-input-container");
      if (container) (container as HTMLElement).style.height = "36px";
    }
  });

  scrollToBottom();


  // 插入 AI 临时消息
  const aiMessage: Message = reactive({
    id: Date.now() + 1,
    content: "",
    think: "AI 正在思考",
    sender: "ai",
    timestamp: new Date(),
    html: "",
  });
  messages.value.push(aiMessage);
  scrollToBottom();

  // 思考动画...
  isGenerating.value = true;
  let dotIndex = 0;
  thinkAnimation = setInterval(() => {
    aiMessage.think = "AI 正在思考" + ".".repeat(dotIndex % 4);
    dotIndex++;
  }, 500);

  try {
    const response: any = await chatbyqwen3({
      userId:props.userId,
      sessionId:props.sessionId,
      question,
      prompt: customPrompt.value,
      stream: true,
    });
    clearInterval(thinkAnimation);

    const answerRaw = response?.answer || response?.data?.answer || response;
    let thinkText = "";
    let answerText = "";
    if (typeof answerRaw === "string") {
      const thinkMatch = answerRaw.match(/<think>([\s\S]*?)<\/think>/);
      thinkText = thinkMatch ? thinkMatch[1].trim() : "";
      answerText = answerRaw.replace(/<think>[\s\S]*?<\/think>/, "").trim();
    } else {
      answerText = JSON.stringify(answerRaw);
    }
    aiMessage.think = thinkText;

    // ✅ 保存用户消息到数据库
    try {
      const saved = await addchat({
        userId: props.userId,
        sessionId: props.sessionId,
        role: "user",
        content: question,
      });
      // 用数据库返回的 id 替换临时 id
      if (saved?.data?.id) {
        userMessage.id = saved.data.id;
      }
    } catch (err) {
      console.error("保存用户消息失败:", err);
    }
    // 保存 AI 消息到数据库
    try {
      const savedAI = await addchat({
        userId: props.userId,
        sessionId: props.sessionId,
        role: "ai",
        content: answerText,
      });
      if (savedAI?.data?.id) {
        aiMessage.id = savedAI.data.id;
      }
    } catch (err) {
      console.error("保存 AI 消息失败:", err);
    }

    // 流式显示 AI 回复
    let answerIndex = 0;
    answerInterval = setInterval(() => {
      if (answerIndex >= answerText.length) {
        clearInterval(answerInterval);
        answerInterval = null;
        trimLeading(aiMessage);
        isGenerating.value = false;
        highlightBlocks();
        return;
      }
      aiMessage.content += answerText[answerIndex];
      aiMessage.html = safeRender(aiMessage.content);
      answerIndex++;
      if (shouldAutoScroll) immediateScrollToBottom();
      highlightBlocks();
      const el2 = getScrollEl();
      if (el2 && !isAtBottom(el2)) {
        newMessagesPending.value = true;
        recomputeScrollButton();
      }
    }, 20);

    context.value.push(`Q: ${question}`);
    context.value.push(`A: ${answerText}`);
  } catch (error: any) {
    clearInterval(thinkAnimation);
    aiMessage.think = "";
    aiMessage.content = "AI 回复失败，请稍后再试。错误: " + error.message;
    aiMessage.html = safeRender(aiMessage.content);
    scrollToBottom();
    isGenerating.value = false;
  }
};


// markdown 渲染（基本防护）
const safeRender = (text: string): string => {
  try {
    const sanitized = text
      .replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, "")
      .replace(/on\w+\s*=\s*"[^"]*"/gi, "")
      .replace(/on\w+\s*=\s*'[^']*'/gi, "");
    return marked.parse(sanitized) as string;
  } catch (e) {
    return text;
  }
};

// 移除 AI 消息开头多余空白（包括换行与全角空格）
const trimLeading = (msg: Message) => {
  if (msg.sender !== "ai") return;
  const t = msg.content.replace(/^[\s\u3000]+/, "");
  if (t !== msg.content) {
    msg.content = t;
    msg.html = safeRender(t);
  }
};

const copyMessage = (msg: Message) => {
  const raw = msg.content;
  navigator.clipboard
    ?.writeText(raw)
    .then(() => {
      ElMessage.success("已复制");
    })
    .catch(() => ElMessage.error("复制失败"));
};
</script>

<style scoped>
.chat-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--chat-bg);
  color: var(--text-primary);
}

.chat-main {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}
.chat-messages {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 820px;
  margin: 0 auto;
}
.message-item {
  display: flex;
  max-width: 100%;
  align-items: flex-start;
}
.message-item.user {
  flex-direction: row-reverse;
}
.message-content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 85%;
}
.message-content {
  position: relative;
  padding: 10px 14px;
  border-radius: 18px;
  font-size: 15px;
  line-height: 1.6;
  word-wrap: break-word;
  white-space: pre-wrap;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
.message-item.ai .message-content {
  background-color: var(--ai-message-bg);
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
}
.message-item.user .message-content {
  background-color: var(--user-message-bg);
  color: var(--user-message-text);
  border-bottom-right-radius: 4px;
}

.message-think {
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 4px;
  font-style: italic;
}
.message-answer {
  font-size: 14px;
}
.message-answer.ai {
  color: var(--text-primary);
}
/* 外侧操作按钮 */
.message-actions {
  display: flex;
  gap: 6px;
  align-self: flex-start;
  padding-left: 10px;
  opacity: 0;
  transition: opacity 0.2s;
}
.message-item:hover .message-actions {
  opacity: 1;
}

.act-btn {
  font-size: 12px;
  padding: 4px 8px;
  border: 1px solid var(--sidebar-border);
  background: var(--sidebar-bg);
  border-radius: 6px;
  cursor: pointer;
  color: var(--muted);
}
.act-btn:hover {
  background: var(--sidebar-hover);
  color: var(--text-primary);
}

/* markdown 内部基础样式 */
.message-answer.ai pre code {
  display: block;
  padding: 12px;
  background: #1e293b;
  color: #e2e8f0;
  border-radius: 6px;
  overflow: auto;
  font-size: 13px;
}
.dark .message-answer.ai pre code {
  background: #0f172a;
}
.message-answer.ai code:not(pre code) {
  background: rgba(0, 0, 0, 0.05);
  padding: 2px 5px;
  border-radius: 4px;
  font-size: 90%;
}
.dark .message-answer.ai code:not(pre code) {
  background: #2c3845;
}
.message-answer.ai h1,
.message-answer.ai h2,
.message-answer.ai h3 {
  margin: 12px 0 8px;
}
.message-answer.ai ul {
  padding-left: 20px;
}
.chat-input-area {
  padding: 10px 20px 40px 20px;
  background-color: transparent;
  max-width: 100%;
  width: 100%;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: center;
  position: relative;
}
.chat-input-container {
  flex-grow: 0;
  position: relative;
  background-color: var(--sidebar-bg);
  border-radius: 8px;
  border: 1px solid var(--sidebar-border);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: border-color 0.2s, box-shadow 0.2s, height 0.2s;
  height: 36px;
  min-height: 36px;
  max-height: 200px;
  width: 800px;
  margin: 0 auto;
}
.chat-input-container:focus-within {
  border-color: var(--accent-color);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}
.message-input {
  flex-grow: 1;
  width: 100%;
  padding: 8px 12px;
  border-radius: 8px;
  border: none;
  background-color: transparent;
  color: var(--sidebar-text);
  outline: none;
  font-size: 16px;
  resize: none;
  height: 20px;
  overflow-y: auto;
  box-sizing: border-box;
  line-height: 1.2;
}
.message-input:focus {
  box-shadow: none;
}
.send-button {
  border-radius: 8px;
  border: none;
  background: var(--accent-color);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  transition: background-color 0.2s, opacity 0.2s;
  position: absolute;
  left: calc(50% + 410px);
  top: 10px;
}
.send-button:disabled {
  background-color: var(--muted);
  cursor: not-allowed;
  opacity: 0.5;
}
.send-button.stop {
  background-color: #ef4444;
  font-size: 24px;
}
.send-button svg {
  width: 20px;
  height: 20px;
}

/* 回到底部按钮样式 */
.scroll-bottom-btn {
  position: fixed;
  right: 28px;
  bottom: 120px; /* 避开输入框 */
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--sidebar-bg);
  border: 1px solid var(--sidebar-border);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  opacity: 0;
  transform: translateY(8px);
  pointer-events: none;
  transition: opacity 0.18s, transform 0.18s, border-color 0.2s, background 0.2s;
  z-index: 50;
}
.scroll-bottom-btn.show {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}
.scroll-bottom-btn:hover {
  border-color: var(--accent-color);
  background: var(--ai-message-bg);
}
.dark .scroll-bottom-btn {
  background: #1e2530;
}

/* === Telegram-inspired chat styling overrides === */
.chat-wrapper {
  --tg-accent: #2a9df4;
  --tg-bg: #e7ebf0;
  --tg-incoming: #ffffff;
  --tg-outgoing: #dff1ff;
  --tg-text: #0f1419;
  --tg-subtext: #6b7280;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans CJK SC", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  background: var(--tg-bg);
}

.chat-main {
  padding: 16px 18px 90px;
  background-image: radial-gradient(#fff 1px, transparent 1px);
  background-size: 24px 24px;
  background-position: -12px -12px;
  background-attachment: local;
}

.message-item {
  margin: 6px 0;
}

.message-content-wrapper {
  max-width: 72%;
}

.message-content.user, .message-item.user .message-content {
  background: var(--tg-outgoing);
  color: var(--tg-text);
  border-radius: 18px 18px 4px 18px;
  box-shadow: 0 1px 1px rgba(0,0,0,.06);
  border: 1px solid rgba(0,0,0,.04);
}

.message-content.ai, .message-item.ai .message-content {
  background: var(--tg-incoming);
  color: var(--tg-text);
  border-radius: 18px 18px 18px 4px;
  box-shadow: 0 1px 1px rgba(0,0,0,.06);
  border: 1px solid rgba(0,0,0,.04);
}

.message-think, .message-answer, .message-stream, .message-render {
  line-height: 1.45;
  font-size: 15px;
}

.message-meta, .message-time {
  color: var(--tg-subtext);
  font-size: 12px;
}

/* Scroll-to-bottom button like Telegram's floating button */
.scroll-bottom-btn {
  border-radius: 999px;
  background: #ffffff;
  border: 1px solid rgba(0,0,0,.08);
  box-shadow: 0 2px 8px rgba(0,0,0,.08);
}

/* Code blocks subtle */
.message-content pre, .message-content code {
  border-radius: 10px;
}

/* Images/attachments rounded */
.message-content img, .message-content .attachment {
  border-radius: 12px;
  overflow: hidden;
}

/* Reduce animation jitter */
.message-enter-active, .message-leave-active {
  transition: all .18s ease;
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