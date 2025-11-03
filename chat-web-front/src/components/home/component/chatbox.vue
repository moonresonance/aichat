<template>
  <div class="chat-wrapper">
    <!-- 设置按钮 & 文本区 -->
    <div class="chat-settings">

      <!-- 弹窗 -->
      <div v-if="showSettings" class="settings-modal" @click.self="showSettings = false">
        <div class="settings-modal-content">
          <h3>设置</h3>
          <label for="customPrompt">自定义提示语:</label>
          <textarea
              id="customPrompt"
              v-model="customPrompt"
              placeholder="请输入自定义提示语..."
              rows="4"
          ></textarea>
          <div class="modal-actions">
            <button @click="showSettings = false" class="btn-close">关闭</button>
          </div>
        </div>
      </div>

    </div>

    <main class="chat-main" ref="scrollContainer">
      <!-- 加载状态指示器 -->
      <div v-if="isLoadingMessages" class="loading-indicator">
        <div class="loading-spinner"></div>
        <p>正在加载会话...</p>
      </div>
      
      <transition-group 
        v-else
        name="messageList" 
        tag="div" 
        class="chat-messages"
        :key="`session-${props.sessionId}`"
      >
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
        >
        </textarea>
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

    <!-- 回到底部按钮 -->
<!--    <button-->
<!--        class="scroll-bottom-btn"-->
<!--        :class="{ show: showScrollToBottom }"-->
<!--        @click="handleScrollToBottom"-->
<!--        aria-label="回到底部"-->
<!--    >-->
<!--      <svg-->
<!--          xmlns="http://www.w3.org/2000/svg"-->
<!--          viewBox="0 0 24 24"-->
<!--          width="24"-->
<!--          height="24"-->
<!--          fill="none"-->
<!--          stroke="currentColor"-->
<!--          stroke-width="2"-->
<!--          stroke-linecap="round"-->
<!--          stroke-linejoin="round"-->
<!--      >-->
<!--        <path d="M6 8l6 6 6-6" />-->
<!--        <path d="M6 4l6 6 6-6" />-->
<!--        <line x1="4" y1="20" x2="20" y2="20" />-->
<!--      </svg>-->
<!--    </button>-->
    <div class="live2d-panel" ref="live2dPanel">
    <live2d ref="live2dRef" />
    </div>
  </div>

</template>

<script setup lang="ts">
import { ref, reactive, watch, nextTick, onMounted, onUnmounted } from "vue";
import { marked } from "marked";
import hljs from "highlight.js/lib/common";
import "highlight.js/styles/github.css";
import { ElMessage } from "element-plus";
import { chatbyqwen3, getchatlist, addchat } from "@/api/chatapi";
import { useUserStore } from "@/stores/user";
import {useAnswerStore} from "@/stores/answer";
import Live2d from "@/components/home/component/live2d.vue";
// === 类型定义 ===
interface Message {
  id: number;
  content: string;
  sender: "user" | "ai";
  timestamp: Date;
  think: string;
  html?: string;
}

const userStore = useUserStore();

// === Props ===
const props = defineProps<{
  sessionId: number | null;
  userId: number | null;
}>();

// === 响应式数据 ===
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
const showSettings = ref(false);

let answerInterval: any = null;
let thinkAnimation: any = null;

const textarea = ref<HTMLTextAreaElement | null>(null);
const scrollContainer = ref<HTMLElement | null>(null);

const newMessagesPending = ref(false);
const showScrollToBottom = ref(false);
const isLoadingMessages = ref(false);
let shouldAutoScroll = true;
let scrollAnimationId: number | null = null;
const AUTO_SCROLL_THRESHOLD = 150;
let renderTimer: number | null = null;
let pendingRenderMessage: Message | null = null;

// === 高亮代码 ===
const highlightBlocks = () => {
  nextTick(() => {
    document
        .querySelectorAll(".message-answer.ai pre code, .message-content pre code")
        .forEach((el: any) => {
          // 给 pre 标签添加语言标签
          const pre = el.parentElement;
          if (pre && pre.tagName === 'PRE') {
            const classNames = el.className || '';
            const match = classNames.match(/language-(\w+)/);
            const lang = match ? match[1] : 'code';
            pre.setAttribute('data-language', lang);
          }
          
          // 高亮代码
          hljs.highlightElement(el);
        });
  });
};

let highlightTimer: number | null = null;
const scheduleHighlight = () => {
  if (highlightTimer !== null) return;
  highlightTimer = window.setTimeout(() => {
    highlightTimer = null;
    highlightBlocks();
  }, 120);
};

// 批量渲染 Markdown，减少 DOM 重排
const scheduleRender = (msg: Message) => {
  pendingRenderMessage = msg;
  if (renderTimer !== null) return;
  
  renderTimer = window.setTimeout(() => {
    renderTimer = null;
    if (pendingRenderMessage) {
      pendingRenderMessage.html = safeRender(pendingRenderMessage.content);
      pendingRenderMessage = null;
    }
  }, 50);
};

// === 辅助函数 ===
const getScrollEl = () =>
    scrollContainer.value || (document.querySelector(".chat-main") as HTMLElement | null);

const scrollToBottom = () => {
  setTimeout(() => immediateScrollToBottom(true));
};

const immediateScrollToBottom = (force = false) => {
  const container = getScrollEl();
  if (!container) return;

  const nearBottom = isAtBottom(container, AUTO_SCROLL_THRESHOLD);
  if (!force && !shouldAutoScroll && !nearBottom) return;

  if (scrollAnimationId !== null) {
    cancelAnimationFrame(scrollAnimationId);
  }

  scrollAnimationId = requestAnimationFrame(() => {
    const targetTop = container.scrollHeight - container.clientHeight;
    const distance = targetTop - container.scrollTop;
    if (!force && Math.abs(distance) <= AUTO_SCROLL_THRESHOLD) {
      scrollAnimationId = null;
      return;
    }

    container.scrollTop = force ? container.scrollHeight : targetTop;
    scrollAnimationId = null;
  });
};

const isAtBottom = (el: HTMLElement, threshold = AUTO_SCROLL_THRESHOLD) =>
    el.scrollHeight - el.scrollTop - el.clientHeight <= threshold;

const recomputeScrollButton = () => {
  const el = getScrollEl();
  if (!el) return;
  const atBottom = isAtBottom(el);
  showScrollToBottom.value = !atBottom;
  shouldAutoScroll = atBottom;
};

const handleScrollToBottom = () => {
  scrollToBottom();
  newMessagesPending.value = false;
  showScrollToBottom.value = false;
};

// === 样式高度自适应 ===
const autoResize = () => {
  if (!textarea.value) return;
  textarea.value.style.height = "auto";
  const newHeight = Math.min(200, Math.max(36, textarea.value.scrollHeight));
  textarea.value.style.height = `${newHeight}px`;

  const container = textarea.value.closest(".chat-input-container");
  if (container) (container as HTMLElement).style.height = `${newHeight}px`;
};

// === 判断是否最后一条 AI 消息 ===
const isLastAI = (msg: Message) => {
  const list = messages.value.filter((v) => v.sender === "ai");
  return list.length > 0 && list[list.length - 1] === msg;
};

// === 消息操作函数 ===
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

// 预渲染 DOM 结构但隐藏内容，用于占位
const preRenderStructure = (text: string): string => {
  try {
    const sanitized = text
        .replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, "")
        .replace(/on\w+\s*=\s*"[^"]*"/gi, "")
        .replace(/on\w+\s*=\s*'[^']*'/gi, "");
    
    const rendered = marked.parse(sanitized) as string;
    
    // 将代码块和行内代码的文本内容替换为占位符，保留结构
    return rendered
      .replace(/(<pre[^>]*><code[^>]*>)([\s\S]*?)(<\/code><\/pre>)/gi, '$1$3')
      .replace(/(<code[^>]*>)([\s\S]*?)(<\/code>)/gi, '$1$3')
      .replace(/(<p[^>]*>)([\s\S]*?)(<\/p>)/gi, (match, start, content, end) => {
        // 保留段落结构，但清空非标签内容
        const cleaned = content.replace(/[^<>]+/g, '');
        return start + cleaned + end;
      });
  } catch (e) {
    return '';
  }
};

// 逐字填充已有 DOM 结构的内容
const fillRenderedContent = (container: HTMLElement, fullText: string, currentText: string) => {
  try {
    const fullRendered = safeRender(fullText);
    const currentRendered = safeRender(currentText);
    
    // 创建临时容器解析完整内容
    const tempFull = document.createElement('div');
    tempFull.innerHTML = fullRendered;
    
    const tempCurrent = document.createElement('div');
    tempCurrent.innerHTML = currentRendered;
    
    // 递归填充文本节点
    const fillTextNodes = (fullNode: Node, currentNode: Node, targetNode: Node) => {
      if (fullNode.nodeType === Node.TEXT_NODE && currentNode.nodeType === Node.TEXT_NODE) {
        const fullText = fullNode.textContent || '';
        const currentText = currentNode.textContent || '';
        if (targetNode.nodeType === Node.TEXT_NODE) {
          targetNode.textContent = currentText;
        }
      } else if (fullNode.nodeType === Node.ELEMENT_NODE && currentNode.nodeType === Node.ELEMENT_NODE) {
        const fullChildren = Array.from(fullNode.childNodes);
        const currentChildren = Array.from(currentNode.childNodes);
        const targetChildren = Array.from(targetNode.childNodes);
        
        for (let i = 0; i < Math.min(fullChildren.length, currentChildren.length, targetChildren.length); i++) {
          fillTextNodes(fullChildren[i], currentChildren[i], targetChildren[i]);
        }
      }
    };
    
    fillTextNodes(tempFull, tempCurrent, container);
  } catch (e) {
    console.error('填充内容失败:', e);
  }
};

const trimLeading = (msg: Message) => {
  if (msg.sender !== "ai") return;
  const t = msg.content.replace(/^[\s\u3000]+/, "");
  if (t !== msg.content) {
    msg.content = t;
    msg.html = safeRender(t);
  }
};

const copyMessage = (msg: Message) => {
  navigator.clipboard
      ?.writeText(msg.content)
      .then(() => ElMessage.success("已复制"))
      .catch(() => ElMessage.error("复制失败"));
};

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

// === 重生 AI 消息 ===
const regenerate = async (aiMsg: Message) => {
  if (isGenerating.value) return;

  const idx = messages.value.indexOf(aiMsg);
  const prevUser = [...messages.value.slice(0, idx)].reverse().find((m) => m.sender === "user");
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
      userId: props.userId,
      sessionId: props.sessionId,
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

    try {
      const savedAI = await addchat({
        userId: props.userId!,
        sessionId: props.sessionId!,
        role: "ai",
        content: answerText,
      });
      if (savedAI?.data?.id) aiMsg.id = savedAI.data.id;
    } catch (err) {
      console.error("保存 AI 消息失败:", err);
    }

    // 先预渲染完整的 DOM 结构（用于占位）
    aiMsg.html = safeRender(answerText);
    aiMsg.content = "";
    
    // 等待 DOM 渲染
    await nextTick();
    scheduleHighlight();

    // 流式显示 AI 回复 - 逐字填充内容
    let i = 0;
    answerInterval = setInterval(() => {
      if (i >= answerText.length) {
        clearInterval(answerInterval);
        answerInterval = null;
        
        // 确保最终内容完整
        aiMsg.content = answerText;
        aiMsg.html = safeRender(answerText);
        
        trimLeading(aiMsg);
        isGenerating.value = false;
        scheduleHighlight();
        return;
      }
      
      aiMsg.content += answerText[i];
      aiMsg.html = safeRender(aiMsg.content);
      i++;

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
const live2dRef = ref<InstanceType<typeof Live2d>>();

const sendToLive2d = (text: string) => {
  (live2dRef.value as any)?.sendMessage?.(text);
};
// === 发送消息 ===
const sendMessage = async () => {
  if (props.sessionId === null || props.userId === null) return;
  const question = messageInput.value.trim();
  if (!question) return;

  const containerBeforeSend = getScrollEl();
  if (containerBeforeSend) {
  shouldAutoScroll = isAtBottom(containerBeforeSend, AUTO_SCROLL_THRESHOLD);
  }

  // 前端临时消息
  const userMessage: Message = {
    id: Date.now(),
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

  // 保存用户消息到数据库
  try {
    const saved = await addchat({
      userId: props.userId,
      sessionId: props.sessionId,
      role: "user",
      content: question,
    });
    if (saved?.data?.id) userMessage.id = saved.data.id;
  } catch (err) {
    console.error("保存用户消息失败:", err);
  }

  // AI 临时消息 - 添加到列表中，显示思考状态
  const aiMessage: Message = reactive({
    id: Date.now() + 1,
    content: "",
    think: "AI 正在思考",
    sender: "ai",
    timestamp: new Date(),
    html: "",
  });
  
  // 立即添加 AI 消息到列表
  messages.value.push(aiMessage);
  scrollToBottom();

  // 思考动画
  isGenerating.value = true;
  let dotIndex = 0;
  thinkAnimation = setInterval(() => {
    aiMessage.think = "AI 正在思考" + ".".repeat(dotIndex % 4);
    dotIndex++;
  }, 500);

  try {
    const response: any = await chatbyqwen3({
      userId: props.userId,
      sessionId: props.sessionId,
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

    // 保存 AI 消息到数据库
    try {
      const savedAI = await addchat({
        userId: props.userId,
        sessionId: props.sessionId,
        role: "ai",
        content: answerText,
      });
      if (savedAI?.data?.id) aiMessage.id = savedAI.data.id;
    } catch (err) {
      console.error("保存 AI 消息失败:", err);
    }

    sendToLive2d(answerText);
    
    // 先预渲染完整的 DOM 结构（用于占位）
    aiMessage.html = safeRender(answerText);
    aiMessage.content = "";
    
    // 等待 DOM 渲染
    await nextTick();
    scheduleHighlight();
    immediateScrollToBottom(true);
    
    let answerIndex = 0;
    
    answerInterval = setInterval(() => {
      if (answerIndex >= answerText.length) {
        clearInterval(answerInterval);
        answerInterval = null;
        
        // 确保最终内容完整
        aiMessage.content = answerText;
        aiMessage.html = safeRender(answerText);
        
        trimLeading(aiMessage);
        isGenerating.value = false;
        scheduleHighlight();
        // AI 回复完成后强制滚动到底部
        immediateScrollToBottom(true);
        return;
      }
      
      aiMessage.content += answerText[answerIndex];
      aiMessage.html = safeRender(aiMessage.content);
      answerIndex++;

      immediateScrollToBottom();

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
    // 添加错误消息到列表
    const errorMessage: Message = reactive({
      id: Date.now() + 1,
      content: "AI 回复失败，请稍后再试。错误: " + error.message,
      think: "",
      sender: "ai",
      timestamp: new Date(),
      html: "",
    });
    messages.value.push(errorMessage);
    // 错误消息也滚动到底部
    nextTick(() => {
      immediateScrollToBottom(true);
    });
    isGenerating.value = false;
  }
};

// === Watchers ===
watch(
    () => props.sessionId,
    async (newId) => {
      isLoadingMessages.value = true;
      
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
        try {
          const resp: any = await getchatlist({ userId: props.userId, sessionId: newId });
          if (resp.data.length > 0) {
            messages.value = resp.data.map((item: any) => ({
              id: item.id,
              content: item.content,
              sender: item.role === "user" ? "user" : "ai",
              timestamp: new Date(),
              think: "",
              html: item.role === "ai" ? marked.parse(item.content) : undefined,
            }));
          } else {
            messages.value = [
              {
                id: Date.now(),
                content: "欢迎使用幻想ai,很高兴为你服务",
                sender: "ai",
                timestamp: new Date(),
                think: "",
              },
            ];
          }
        } catch (e) {
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
      
      // 消息加载完成后滚动到底部
      nextTick(() => {
  scheduleHighlight();
        // 确保 transition-group 动画完成后再滚动
        setTimeout(() => {
          shouldAutoScroll = true;
          immediateScrollToBottom(true);
        }, 50);
      });
      isLoadingMessages.value = false;
    }
);

watch(messageInput, () => {
  nextTick(() => {
    autoResize();
  });
});

// === 生命周期 ===
onMounted(async () => {
  nextTick(() => {
    autoResize();
    const el = getScrollEl();
    if (el) {
      el.addEventListener("scroll", handleScroll, { passive: true } as AddEventListenerOptions);
      recomputeScrollButton();
      immediateScrollToBottom(true);
    }
    highlightBlocks();
  });
});
// 自动下滑功能
const handleScroll = () => {
  const container = getScrollEl();
  if (!container) return;
  const distance = container.scrollHeight - container.scrollTop - container.clientHeight;
  const nearBottom = distance < AUTO_SCROLL_THRESHOLD;
  shouldAutoScroll = nearBottom;
  showScrollToBottom.value = !nearBottom;

  if (nearBottom) {
    immediateScrollToBottom();
    newMessagesPending.value = false;
  }
};

onUnmounted(() => {
  const el = getScrollEl();
  if (el) el.removeEventListener("scroll", handleScroll);
  if (highlightTimer !== null) {
    clearTimeout(highlightTimer);
    highlightTimer = null;
  }
  if (renderTimer !== null) {
    clearTimeout(renderTimer);
    renderTimer = null;
  }
  if (scrollAnimationId !== null) {
    cancelAnimationFrame(scrollAnimationId);
    scrollAnimationId = null;
  }
});
</script>


<style scoped>
/* === 聊天框基础 === */
.chat-wrapper { height: 100%; display: flex; flex-direction: column; background-color: var(--chat-bg); color: var(--text-primary); }

/* === 设置面板 === */
.chat-settings {
  position: absolute;
  top: 12px;
  right: 24px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  z-index: 100;
}
.settings-btn {
  background: var(--accent-color);
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}
.settings-panel {
  margin-top: 8px;
  width: 300px;
  display: flex;
  flex-direction: column;
  background: var(--sidebar-bg);
  padding: 8px;
  border-radius: 8px;
  border: 1px solid var(--sidebar-border);
}
.settings-panel textarea {
  width: 100%;
  border-radius: 6px;
  border: 1px solid var(--sidebar-border);
  padding: 6px;
  resize: vertical;
  font-size: 14px;
}

/* === 原有聊天样式保持不变，可复制你原来的 CSS === */
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
  overflow-x: hidden;
  padding: 20px;
  position: relative;
  max-height: calc(100vh - 280px);
  scroll-behavior: smooth;
}

/* 自定义滚动条样式 */
.chat-main::-webkit-scrollbar {
  width: 8px;
}

.chat-main::-webkit-scrollbar-track {
  background: transparent;
}

.chat-main::-webkit-scrollbar-thumb {
  background: rgba(42, 157, 244, 0.3);
  border-radius: 4px;
  transition: background 0.3s ease;
}

.chat-main::-webkit-scrollbar-thumb:hover {
  background: rgba(42, 157, 244, 0.6);
}

/* Firefox 滚动条 */
.chat-main {
  scrollbar-width: thin;
  scrollbar-color: rgba(42, 157, 244, 0.3) transparent;
}

.loading-indicator {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(244, 249, 255, 0.92), rgba(233, 242, 255, 0.92));
  animation: fadeIn 0.3s ease-out;
  z-index: 10;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(42, 157, 244, 0.1);
  border-top-color: #2a9df4;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-indicator p {
  color: rgba(15, 23, 42, 0.6);
  font-size: 14px;
  margin: 0;
  font-weight: 500;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}
.chat-messages {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 820px;
  margin: 0 auto;
}
/* === 消息进入动画 === */
@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.92);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* === 消息离开动画 === */
@keyframes messageSlideOut {
  from {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateY(-12px) scale(0.92);
  }
}

/* Vue transition-group 动画类 */
.messageList-enter-active {
  animation: messageSlideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.messageList-leave-active {
  animation: messageSlideOut 0.3s ease-out;
  position: absolute;
}

.messageList-move {
  transition: transform 0.4s ease;
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
  padding: 12px 16px;
  border-radius: 20px;
  font-size: 15px;
  line-height: 1.6;
  word-wrap: break-word;
  white-space: pre-wrap;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  will-change: transform;
  contain: layout style;
  min-width: 0;
}

.message-content:hover {
  transform: translateY(-1px);
}

.message-content:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
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
  position: relative;
  overflow: hidden;
}

.message-item.user .message-content::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, 
    transparent 0%, 
    rgba(255, 255, 255, 0.15) 45%,
    rgba(255, 255, 255, 0.3) 50%,
    rgba(255, 255, 255, 0.15) 55%,
    transparent 100%
  );
  opacity: 0;
  animation: messageShine 3s ease-in-out infinite;
  pointer-events: none;
}

@keyframes messageShine {
  0%, 100% { 
    opacity: 0;
    transform: translateX(-150%) skewX(-20deg); 
  }
  50% { 
    opacity: 1;
    transform: translateX(150%) skewX(-20deg); 
  }
}

.message-think {
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 4px;
  font-style: italic;
  animation: thinkingPulse 1.4s ease-in-out infinite;
}

@keyframes thinkingPulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; transform: translateX(2px); }
}
.message-answer {
  font-size: 14px;
  transform: translateZ(0);
  backface-visibility: hidden;
}
.message-answer.ai {
  color: var(--text-primary);
}

/* 确保空段落也有高度 */
.message-answer p:empty::before,
.message-content p:empty::before {
  content: '\200B';
  visibility: hidden;
}

.message-answer h1:empty::before,
.message-answer h2:empty::before,
.message-answer h3:empty::before,
.message-content h1:empty::before,
.message-content h2:empty::before,
.message-content h3:empty::before {
  content: '\200B';
  visibility: hidden;
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
  transition: all 0.2s ease;
}

.act-btn:hover {
  background: var(--sidebar-hover);
  color: var(--text-primary);
  transform: scale(1.08);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.act-btn:active {
  transform: scale(0.95);
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
  border: 1px solid #334155;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  line-height: 1.5;
}

[data-theme="dark"] .message-answer.ai pre code {
  background: #1e293b;
  color: #e2e8f0;
  border-color: #334155;
}

.message-answer.ai code:not(pre code) {
  background: rgba(30, 41, 59, 0.2);
  color: #1e293b;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 90%;
  border: 1px solid rgba(30, 41, 59, 0.15);
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

[data-theme="dark"] .message-answer.ai code:not(pre code) {
  background: rgba(148, 163, 184, 0.2);
  color: #cbd5e1;
  border-color: rgba(148, 163, 184, 0.25);
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
  padding:10px 5px 20px;
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
  background: var(--surface-elevated);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1.5px solid var(--border-subtle);
  box-shadow: 
    0 8px 24px rgba(15, 23, 42, 0.08),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  height: 52px;
  min-height: 52px;
  max-height: 200px;
  width: 700px;
  right: 40px;
  margin: 0 auto;
  animation: inputFadeIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

[data-theme="dark"] .chat-input-container {
  background: rgba(17, 24, 39, 0.6);
  border-color: rgba(148, 163, 184, 0.15);
  box-shadow: 
    0 8px 24px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset;
}

@keyframes inputFadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.chat-input-container:focus-within {
  border-color: var(--accent-color);
  box-shadow: 
    0 12px 32px rgba(59, 130, 246, 0.2),
    0 0 0 3px rgba(59, 130, 246, 0.1),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  transform: translateY(-2px);
}

[data-theme="dark"] .chat-input-container:focus-within {
  box-shadow: 
    0 12px 32px rgba(59, 130, 246, 0.3),
    0 0 0 3px rgba(59, 130, 246, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.08) inset;
}
.message-input {
  flex-grow: 1;
  width: 100%;
  padding: 14px 20px;
  border-radius: 24px;
  border: none;
  background-color: transparent;
  color: var(--text-primary);
  outline: none;
  font-size: 15px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  resize: none;
  height: 24px;
  overflow-y: auto;
  box-sizing: border-box;
  line-height: 1.5;
  transition: color 0.3s ease;
}

.message-input::placeholder {
  color: var(--muted);
  opacity: 0.6;
  transition: opacity 0.3s ease;
}

.message-input:focus::placeholder {
  opacity: 0.4;
}
.message-input:focus {
  box-shadow: none;
}
.send-button {
  border-radius: 20px;
  border: none;
  background: linear-gradient(135deg, var(--accent-color), var(--accent-strong));
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: absolute;
  left: calc(50% + 328px);
  top: 12px;
  animation: buttonPopIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 
    0 4px 12px rgba(59, 130, 246, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
}

[data-theme="dark"] .send-button {
  box-shadow: 
    0 4px 16px rgba(59, 130, 246, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.08) inset;
}

@keyframes buttonPopIn {
  from {
    opacity: 0;
    transform: scale(0.6);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.send-button:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 
    0 8px 24px rgba(59, 130, 246, 0.45),
    0 0 0 1px rgba(255, 255, 255, 0.15) inset;
}

[data-theme="dark"] .send-button:hover {
  box-shadow: 
    0 8px 28px rgba(59, 130, 246, 0.6),
    0 0 0 1px rgba(255, 255, 255, 0.12) inset;
}

.send-button:active {
  transform: translateY(0) scale(0.98);
}
.send-button:disabled {
  background: linear-gradient(135deg, var(--muted), rgba(107, 114, 128, 0.8));
  cursor: not-allowed;
  opacity: 0.5;
  transform: none;
  box-shadow: none;
}

.send-button:disabled:hover {
  transform: none;
  box-shadow: none;
}

.send-button.stop {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  font-size: 24px;
  animation: pulseStop 1.5s ease-in-out infinite;
}

@keyframes pulseStop {
  0%, 100% {
    box-shadow: 
      0 4px 12px rgba(239, 68, 68, 0.4),
      0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  }
  50% {
    box-shadow: 
      0 6px 20px rgba(239, 68, 68, 0.6),
      0 0 0 1px rgba(255, 255, 255, 0.15) inset;
  }
}
.send-button svg {
  width: 22px;
  height: 22px;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.2));
}

/* 回到底部按钮样式 */
.scroll-bottom-btn {
  position: fixed;
  right: 5%;
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
  animation: scrollBtnBounce 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes scrollBtnBounce {
  0% { transform: translateY(20px) scale(0.8); opacity: 0; }
  60% { transform: translateY(-2px) scale(1.05); }
  100% { transform: translateY(0) scale(1); opacity: 1; }
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

/* === Telegram-inspired chat styling overrides === */
.chat-wrapper {
  --tg-accent: var(--accent-color);
  --tg-bg: var(--chat-bg);
  --tg-incoming: var(--message-ai-bg);
  --tg-outgoing: var(--message-user-bg);
  --tg-text: var(--message-text);
  --tg-subtext: var(--message-subtext);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans CJK SC", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  background: var(--tg-bg);
  color: var(--tg-text);
}

.chat-main {
  padding: 16px 18px 90px;
  background-image: radial-gradient(rgba(15, 23, 42, 0.05) 1px, transparent 1px);
  background-size: 24px 24px;
  background-position: -12px -12px;
  background-attachment: local;
}

.message-item {
  margin: 16px 0;
  animation: messageSlideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-content-wrapper {
  max-width: 68%;
}

.message-content.user,
.message-item.user .message-content {
  background: linear-gradient(135deg, #4F9FFF 0%, #2E7FE8 100%);
  color: #ffffff;
  border-radius: 20px 20px 4px 20px;
  box-shadow: 
    0 2px 8px rgba(59, 130, 246, 0.25),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  border: none;
  padding: 12px 16px;
  position: relative;
  overflow: hidden;
}

.message-content.user::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, transparent 50%);
  pointer-events: none;
}

[data-theme="dark"] .message-content.user,
[data-theme="dark"] .message-item.user .message-content {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  box-shadow: 
    0 2px 12px rgba(59, 130, 246, 0.35),
    0 0 0 1px rgba(255, 255, 255, 0.08) inset;
}

.message-content.ai,
.message-item.ai .message-content {
  background: var(--surface-elevated);
  color: var(--text-primary);
  border-radius: 20px 20px 20px 4px;
  box-shadow: 
    0 2px 8px rgba(15, 23, 42, 0.08),
    0 0 0 1px rgba(15, 23, 42, 0.05);
  border: 1px solid var(--border-subtle);
  padding: 12px 16px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

[data-theme="dark"] .message-content.ai,
[data-theme="dark"] .message-item.ai .message-content {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(148, 163, 184, 0.15);
  box-shadow: 
    0 2px 12px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset;
}

.message-think,
.message-answer,
.message-stream,
.message-render {
  line-height: 1.45;
  font-size: 15px;
}

.message-meta,
.message-time {
  color: var(--tg-subtext);
  font-size: 12px;
}

/* Scroll-to-bottom button like Telegram's floating button */
.scroll-bottom-btn {
  border-radius: 999px;
  background: var(--surface-elevated);
  border: 1px solid var(--border-subtle);
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.12);
}

/* Code blocks subtle */
.message-content pre,
.message-content code {
  border-radius: 10px;
}

.message-content pre {
  padding: 0;
  overflow: hidden;
  background: #1e293b;
  color: #e2e8f0;
  border: 1px solid #334155;
  margin: 8px 0;
  transform: translateZ(0);
  backface-visibility: hidden;
  min-height: 3em;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.message-content pre::before {
  content: attr(data-language);
  position: absolute;
  top: 0;
  right: 0;
  padding: 4px 10px;
  background: rgba(0, 0, 0, 0.2);
  color: #94a3b8;
  font-size: 11px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom-left-radius: 6px;
  z-index: 1;
}

.message-content pre:empty::before {
  content: '';
  display: inline-block;
  width: 1px;
  height: 1em;
}

.message-content pre code {
  display: block;
  min-height: inherit;
  padding: 36px 12px 12px 12px;
  background: transparent;
  border: none;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre;
  color: inherit;
}

.message-content pre code:empty::before {
  content: '\200B';
  visibility: hidden;
}

[data-theme="dark"] .message-content pre {
  background: #1e293b;
  color: #e2e8f0;
  border-color: #334155;
}

.message-content code {
  padding: 2px 6px;
  border-radius: 6px;
  background: rgba(30, 41, 59, 0.15);
  color: #1e293b;
  border: 1px solid rgba(30, 41, 59, 0.2);
  font-size: 90%;
  transform: translateZ(0);
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

[data-theme="dark"] .message-content code {
  background: rgba(148, 163, 184, 0.2);
  color: #cbd5e1;
  border-color: rgba(148, 163, 184, 0.25);
}

:where([data-theme="dark"]) .chat-main {
  background-image: radial-gradient(rgba(148, 163, 184, 0.12) 1px, transparent 1px);
}

:where([data-theme="dark"]) .scroll-bottom-btn {
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.45);
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
/* 弹窗遮罩 */
.settings-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 200;
}

/* 弹窗内容 */
.settings-modal-content {
  background: var(--sidebar-bg);
  padding: 24px;
  border-radius: 12px;
  width: 400px;
  max-width: 90%;
  box-shadow: 0 8px 24px rgba(0,0,0,0.25);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 弹窗标题 */
.settings-modal-content h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  color: var(--text-primary);
}

/* 文本域 */
.settings-modal-content textarea {
  width: 100%;
  border-radius: 6px;
  border: 1px solid var(--sidebar-border);
  padding: 8px;
  font-size: 14px;
  resize: vertical;
  background: var(--chat-bg);
  color: var(--text-primary);
}

/* 底部按钮 */
.modal-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-close {
  padding: 6px 16px;
  border-radius: 6px;
  border: none;
  background: var(--accent-color);
  color: #fff;
  cursor: pointer;
}
.live2d-panel {
  position: fixed;
  bottom: 80px;        /* 高度略高于发送按钮 */
  right: 20px;         /* 保持右侧间距 */
  width: 180px;        /* 默认宽度 */
  height: auto;
  aspect-ratio: 9 / 16;
  z-index: 150;
  pointer-events: none;
  transition: transform 0.3s ease, width 0.3s ease;
}

.live2d-panel:hover {
  pointer-events: auto;
  transform: scale(1.05);
}
@media (max-width: 1024px) {
  .live2d-panel { width: 140px; bottom: 70px; }
}
@media (max-width: 768px) {
  .live2d-panel { width: 120px; bottom: 60px; }
}
@media (max-width: 480px) {
  .live2d-panel { width: 100px; bottom: 50px; right: 10px; }
}

</style>
