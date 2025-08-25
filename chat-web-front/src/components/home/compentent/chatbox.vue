<template>
  <div class="chat-wrapper">
    <!-- 聊天消息区 -->
    <main class="chat-main">
      <transition-group name="message" tag="div" class="chat-messages">
        <div
            v-for="message in messages"
            :key="message.id"
            :class="['message-item', message.sender]"
        >
          <div class="message-avatar">{{ message.sender === 'user' ? '你' : 'AI' }}</div>
          <div class="message-content">
            <!-- 思考区 -->
            <div v-if="message.think && showThink" class="message-think">
              思考: {{ message.think }}
            </div>
            <!-- 回答内容 -->
            <div class="message-answer">{{ message.content }}</div>
          </div>
        </div>
      </transition-group>
    </main>

    <!-- 浮窗输入框 -->
    <div class="chat-input-floating show">
      <input
          v-model="messageInput"
          @keyup.enter="sendMessage"
          type="text"
          class="message-input"
          placeholder="输入消息..."
          :disabled="props.sessionId === null"
      />
      <button @click="sendMessage" class="send-button" :disabled="props.sessionId === null">
        发送
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import { chatbyqwen3 } from '@/api/chatapi';

interface Message {
  id: number;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  think: string;
}

const props = defineProps<{
  sessionId: number | null;
  userId: number | null;
}>();

const messages = ref<Message[]>([
  {
    id: Date.now(),
    content: props.sessionId ? `欢迎进入会话 ${props.sessionId}` : '请选择会话开始聊天',
    sender: 'ai',
    timestamp: new Date(),
    think: ''
  }
]);

const messageInput = ref('');
const context = ref<string[]>([]);
const showThink = ref(true); // 控制思考区显示
const customPrompt = ref('你是一个智能助手'); // 默认提示词

const scrollToBottom = () => {
  setTimeout(() => {
    const container = document.querySelector('.chat-messages');
    if (container) container.scrollTop = container.scrollHeight;
  }, 0);
};

// 监听会话切换
watch(
    () => props.sessionId,
    (newId) => {
      messages.value = [
        {
          id: Date.now(),
          content: newId ? `欢迎进入会话 ${newId}` : '请选择会话开始聊天',
          sender: 'ai',
          timestamp: new Date(),
          think: ''
        }
      ];
      scrollToBottom();
    }
);

// 发送消息
const sendMessage = async () => {
  if (props.sessionId === null) return;

  const question = messageInput.value.trim();
  if (!question) return;

  // 用户消息
  const userMessage: Message = {
    id: Date.now(),
    content: question,
    sender: 'user',
    timestamp: new Date(),
    think: ''
  };
  messages.value.push(userMessage);
  messageInput.value = '';
  scrollToBottom();

  // 先插入 AI 消息对象，显示思考动画
  const aiMessage: Message = reactive({
    id: Date.now() + 1,
    content: '',
    think: 'AI 正在思考', // 初始文字
    sender: 'ai',
    timestamp: new Date()
  });
  messages.value.push(aiMessage);
  scrollToBottom();

  // 思考动画
  let dotIndex = 0;
  const thinkAnimation = setInterval(() => {
    aiMessage.think = 'AI 正在思考' + '.'.repeat(dotIndex % 4);
    dotIndex++;
    scrollToBottom();
  }, 500); // 每 500ms 更新一次动画

  try {
    const response = await chatbyqwen3({ question, prompt: customPrompt.value, stream: true });
    clearInterval(thinkAnimation); // 停止思考动画

    const answerRaw = response?.answer || response?.data?.answer || response;
    let thinkText = '';
    let answerText = '';
    if (typeof answerRaw === 'string') {
      const thinkMatch = answerRaw.match(/<think>([\s\S]*?)<\/think>/);
      thinkText = thinkMatch ? thinkMatch[1].trim() : '';
      answerText = answerRaw.replace(/<think>[\s\S]*?<\/think>/, '').trim();
    } else {
      answerText = JSON.stringify(answerRaw);
    }

    // 输出真实思考区文字
    aiMessage.think = thinkText;

    // 逐字显示回答内容
    let answerIndex = 0;
    const answerInterval = setInterval(() => {
      if (answerIndex >= answerText.length) {
        clearInterval(answerInterval);
        return;
      }
      aiMessage.content += answerText[answerIndex];
      answerIndex++;
      scrollToBottom();
    }, 20);

    context.value.push(`Q: ${question}`);
    context.value.push(`A: ${answerText}`);
  } catch (error: any) {
    clearInterval(thinkAnimation); // 停止思考动画
    console.error('调用聊天接口失败:', error);
    aiMessage.think = '';
    aiMessage.content = 'AI 回复失败，请稍后再试。错误: ' + error.message;
    scrollToBottom();
  }
};

</script>

<style scoped>
.chat-wrapper {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  position: relative;
}
.chat-main {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f5f7fa;
}
.chat-messages {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.message-item { display: flex; max-width: 70%; align-items: flex-start; }
.message-item.user { flex-direction: row-reverse; margin-left: auto; }
.message-avatar { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #3b82f6, #06b6d4); color: white; display: flex; align-items: center; justify-content: center; font-size: 14px; margin-right: 8px; flex-shrink: 0; }
.message-item.user .message-avatar { background: linear-gradient(135deg, #f97316, #facc15); margin-left: 8px; margin-right: 0; }
.message-content { padding: 12px 18px; border-radius: 20px; font-size: 14px; line-height: 1.5; background: #e0e7ff; color: #111827; box-shadow: 0 4px 12px rgba(0,0,0,0.1); word-wrap: break-word; white-space: pre-wrap; }
.message-item.user .message-content { background: #fef3c7; color: #111827; }
.message-think { font-size: 12px; color: #6b7280; margin-bottom: 4px; font-style: italic; }
.message-answer { font-size: 14px; color: #111827; }
.chat-input-floating { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%) translateY(0); display: flex; gap: 10px; background: #ffffff; padding: 12px 16px; border-radius: 32px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 1000; width: 60%; max-width: 800px; min-width: 300px; }
.message-input { flex: 1; padding: 12px 16px; border-radius: 24px; border: 1px solid #d1d5db; outline: none; font-size: 14px; }
.send-button { padding: 12px 24px; border-radius: 24px; border: none; background: linear-gradient(135deg, #3b82f6, #06b6d4); color: white; cursor: pointer; font-weight: 500; }
</style>
