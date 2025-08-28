<template>
  <div class="chat-wrapper">
    <main class="chat-main">
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
              <button class="act-btn" @click="copyMessage(m)">复制</button>
              <button
                class="act-btn"
                v-if="isLastAI(m) && !isGenerating"
                @click="regenerate(m)"
              >
                重新生成
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, nextTick, computed, onMounted } from "vue";
import { marked } from "marked";
import hljs from "highlight.js/lib/common";
import "highlight.js/styles/github-dark.css";
import { ElMessage } from "element-plus";
import { chatbyqwen3 } from "@/api/chatapi";
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

const messageCount = computed(() => messages.value.length);
const currentSessionName = computed(() => {
  // In a real app, you might get this from a store or props
  return props.sessionId ? `会话 ${props.sessionId}` : "";
});

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

const scrollToBottom = () => {
  setTimeout(() => {
    const container = document.querySelector(".chat-messages");
    if (container) container.scrollTop = container.scrollHeight;
  });
};

// 监听会话切换
watch(
  () => props.sessionId,
  (newId) => {
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
      messages.value = [
        {
          id: Date.now(),
          content: `欢迎进入会话 ${newId}`,
          sender: "ai",
          timestamp: new Date(),
          think: "",
        },
      ];
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
  });
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
  aiMsg.content = "";
  aiMsg.html = "";
  aiMsg.think = "AI 正在思考";
  isGenerating.value = true;
  let dot = 0;
  thinkAnimation = setInterval(() => {
    aiMsg.think = "AI 正在思考" + ".".repeat(dot % 4);
    dot++;
  }, 500);
  try {
    const resp: any = await chatbyqwen3({
      question: prevUser.content,
      prompt: customPrompt.value,
      stream: true,
    });
    clearInterval(thinkAnimation);
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
  if (props.sessionId === null) return;

  const question = messageInput.value.trim();
  if (!question) return;

  // 用户消息
  const userMessage: Message = {
    id: Date.now(),
    content: question,
    sender: "user",
    timestamp: new Date(),
    think: "",
  };
  messages.value.push(userMessage);
  messageInput.value = "";

  // 重置输入框高度
  nextTick(() => {
    if (textarea.value) {
      textarea.value.style.height = "36px";
      const container = textarea.value.closest(".chat-input-container");
      if (container) {
        (container as HTMLElement).style.height = "36px";
      }
    }
  });

  scrollToBottom();

  // 先插入 AI 消息对象，显示思考动画
  const aiMessage: Message = reactive({
    id: Date.now() + 1,
    content: "",
    think: "AI 正在思考", // 初始文字
    sender: "ai",
    timestamp: new Date(),
    html: "",
  });
  messages.value.push(aiMessage);
  scrollToBottom();

  // 思考动画
  isGenerating.value = true;
  let dotIndex = 0;
  thinkAnimation = setInterval(() => {
    aiMessage.think = "AI 正在思考" + ".".repeat(dotIndex % 4);
    dotIndex++;
    scrollToBottom();
  }, 500);

  try {
    const response: any = await chatbyqwen3({
      question,
      prompt: customPrompt.value,
      stream: true,
    });
    clearInterval(thinkAnimation); // 停止思考动画

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

    // 输出真实思考区文字
    aiMessage.think = thinkText;

    // 逐字显示回答内容
    // 流式逐字：同时更新 html (简单处理：整体重渲)
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
      scrollToBottom();
      highlightBlocks();
    }, 20);

    context.value.push(`Q: ${question}`);
    context.value.push(`A: ${answerText}`);
  } catch (error: any) {
    clearInterval(thinkAnimation);
    console.error("调用聊天接口失败:", error);
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
  padding: 10px 20px 20px 20px;
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
  width: 500px;
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
  left: calc(50% + 255px);
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
</style>
