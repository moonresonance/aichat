<template>
  <div class="chat-wrapper">
    <main class="chat-main">
      <transition-group name="message" tag="div" class="chat-messages">
        <div
          v-for="m in messages"
          :key="m.id"
          :class="['message-item', m.sender]"
        >
          <div class="message-avatar">
            {{ m.sender === "user" ? "你" : "AI" }}
          </div>
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
      </transition-group>
    </main>
    <div class="chat-input-floating show">
      <input
        v-model="messageInput"
        @keyup.enter="sendMessage"
        type="text"
        class="message-input"
        placeholder="输入消息..."
        :disabled="props.sessionId === null"
      />
      <button
        class="send-button"
        @click="sendMessage"
        :disabled="props.sessionId === null || isGenerating"
      >
        发送
      </button>
      <button
        v-if="isGenerating"
        class="send-button stop"
        @click="stopGeneration"
      >
        停止
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, nextTick } from "vue";
import { marked } from "marked";
import hljs from "highlight.js/lib/common";
import "highlight.js/styles/github-dark.css";
import { ElMessage } from "element-plus";
import { chatbyqwen3 } from "@/api/chatapi";

interface Message {
  id: number;
  content: string; // raw text
  sender: "user" | "ai";
  timestamp: Date;
  think: string;
  html?: string; // rendered markdown (AI only)
}

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

const messageInput = ref("");
const context = ref<string[]>([]);
const showThink = ref(true);
const customPrompt = ref("你是一个智能助手");
const isGenerating = ref(false);
let answerInterval: any = null;
let thinkAnimation: any = null;

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
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: transparent;
  position: relative;
  color: var(--text-primary, #111827);
}
.chat-main {
  flex: 1;
  overflow-y: auto;
  padding: 40px 20px;
  display: flex;
  justify-content: center;
  background-color: transparent;
}
.chat-messages {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  max-width: 820px; /* limit width similar to ChatGPT */
}
.message-item {
  display: flex;
  max-width: 100%;
  align-items: flex-start;
}
.message-item.user {
  flex-direction: row-reverse;
  margin-left: auto;
}
.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(
    135deg,
    var(--accent-start, #3b82f6),
    var(--accent-end, #06b6d4)
  );
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  margin-right: 12px;
  flex-shrink: 0;
}
.message-item.user .message-avatar {
  background: linear-gradient(135deg, #f97316, #facc15);
  margin-left: 12px;
  margin-right: 0;
}
.message-content {
  position: relative;
  display: inline-block;
  padding: 11px;
  border-radius: 8px;
  font-size: 15px;
  line-height: 1.6;
  background: var(--panel-bg, #ffffff);
  color: #111827;
  box-shadow: 0 6px 18px rgba(16, 24, 40, 0.06);
  word-wrap: break-word;
  white-space: pre-wrap;
  border: 1px solid rgba(0, 0, 0, 0.04);
  max-width: min(100%, 720px); /* 限制宽度，自动换行 */
  vertical-align: top;
}
.message-item.ai .message-content {
  align-self: flex-start;
}
.message-item.user .message-content {
  background: linear-gradient(135deg, #fff7ed, #ffedd5);
  color: #111827;
  border: 1px solid rgba(0, 0, 0, 0.03);
}
.message-think {
  font-size: 12px;
  color: var(--muted, #6b7280);
  margin-bottom: 4px;
  font-style: italic;
}
.message-answer {
  font-size: 14px;
  color: #111827;
}
.message-answer.ai {
  color: var(--ai-text, #2563eb);
}
/* 外侧操作按钮 */
.message-actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-left: 10px;
  align-self: flex-start;
}
.message-item.user .message-actions {
  display: none;
}
.act-btn {
  font-size: 12px;
  padding: 4px 8px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  background: rgba(255, 255, 255, 0.85);
  border-radius: 6px;
  cursor: pointer;
  backdrop-filter: blur(4px);
}
.act-btn:hover {
  background: #f1f5f9;
}
.dark .act-btn {
  background: rgba(30, 41, 59, 0.5);
  color: #e2e8f0;
  border-color: rgba(255, 255, 255, 0.2);
}
.dark .act-btn:hover {
  background: rgba(51, 65, 85, 0.6);
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
  background: #f1f5f9;
  padding: 2px 5px;
  border-radius: 4px;
  font-size: 90%;
}
.dark .message-answer.ai code:not(pre code) {
  background: #1e293b;
}
.message-answer.ai h1,
.message-answer.ai h2,
.message-answer.ai h3 {
  margin: 12px 0 8px;
}
.message-answer.ai ul {
  padding-left: 20px;
}
.chat-input-floating {
  position: fixed;
  bottom: 28px;
  left: 50%;
  transform: translateX(-50%) translateY(0);
  display: flex;
  gap: 12px;
  background: var(--panel-bg, #ffffff);
  padding: 10px 14px;
  border-radius: 999px;
  box-shadow: 0 8px 30px rgba(2, 6, 23, 0.08);
  z-index: 1000;
  width: 64%;
  max-width: 950px;
  min-width: 360px;
}
.message-input {
  flex: 1;
  padding: 12px 16px;
  border-radius: 24px;
  border: 1px solid #d1d5db;
  outline: none;
  font-size: 14px;
}
.send-button {
  padding: 10px 18px;
  border-radius: 999px;
  border: none;
  background: linear-gradient(135deg, #6f5fff, #3b82f6);
  color: white;
  cursor: pointer;
  font-weight: 600;
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.18);
}

/* Header inside chat column */
.chat-header {
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
  background: rgba(255, 255, 255, 0.6);
}
.chat-header h2 {
  margin: 0;
  font-size: 16px;
  color: #0f172a;
}
</style>
