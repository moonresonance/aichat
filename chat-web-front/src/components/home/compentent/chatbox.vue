<template>
  <div class="chat-wrapper">
    <!-- 控制显示/隐藏思考区按钮 -->
    <div class="think-toggle">
      <button @click="showThink = !showThink">
        {{ showThink ? '隐藏思考区' : '显示思考区' }}
      </button>
    </div>

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
      />
      <button @click="sendMessage" class="send-button">发送</button>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue';
import { chatbyqwen3 } from '@/api/chatapi';

export default {
  name: 'ChatBox',
  setup() {
    const messages = ref([
      {
        id: 1,
        content: '你好！我是AI助手，有什么可以帮助你的吗？',
        sender: 'ai',
        timestamp: new Date(),
        think: ''
      }
    ]);

    const messageInput = ref('');
    const context = ref([]);
    const showThink = ref(true); // 控制思考区显示

    const scrollToBottom = () => {
      setTimeout(() => {
        const container = document.querySelector('.chat-messages');
        if (container) container.scrollTop = container.scrollHeight;
      }, 0);
    };

    const sendMessage = async () => {
      const question = messageInput.value.trim();
      if (!question) return;

      // 用户消息
      const userMessage = {
        id: Date.now(),
        content: question,
        sender: 'user',
        timestamp: new Date()
      };
      messages.value.push(userMessage);
      messageInput.value = '';
      scrollToBottom();

      try {
        const response = await chatbyqwen3({ question, prompt: '你是一个智能助手', stream: true });
        const answerRaw = response?.answer || response?.data?.answer || response;

        // 提取思考区和回答内容
        let thinkText = '';
        let answerText = '';
        if (typeof answerRaw === 'string') {
          const thinkMatch = answerRaw.match(/<think>([\s\S]*?)<\/think>/);
          thinkText = thinkMatch ? thinkMatch[1].trim() : '';
          answerText = answerRaw.replace(/<think>[\s\S]*?<\/think>/, '').trim();
        } else {
          answerText = JSON.stringify(answerRaw);
        }

        // AI 消息对象，用 reactive 保证响应式
        const aiMessage = reactive({
          id: Date.now() + 1,
          content: '',
          think: '',
          sender: 'ai',
          timestamp: new Date()
        });
        messages.value.push(aiMessage);
        scrollToBottom();

        // 逐字输出思考区
        let thinkIndex = 0;
        const thinkInterval = setInterval(() => {
          if (thinkIndex >= thinkText.length) {
            clearInterval(thinkInterval);

            // 逐字输出回答内容
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

            return;
          }
          aiMessage.think += thinkText[thinkIndex];
          thinkIndex++;
          scrollToBottom();
        }, 20);

        context.value.push(`Q: ${question}`);
        context.value.push(`A: ${answerText}`);
      } catch (error) {
        console.error('调用聊天接口失败:', error);
        const errorMessage = {
          id: Date.now() + 2,
          content: 'AI 回复失败，请稍后再试。错误: ' + error.message,
          sender: 'ai',
          timestamp: new Date(),
          think: ''
        };
        messages.value.push(errorMessage);
        scrollToBottom();
      }
    };

    return { messages, messageInput, sendMessage, scrollToBottom, showThink };
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

/* 思考区切换按钮 */
.think-toggle {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1100;
}

.think-toggle button {
  padding: 6px 12px;
  border-radius: 6px;
  border: none;
  background: #3b82f6;
  color: white;
  cursor: pointer;
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

.message-think {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
  font-style: italic;
}

.message-answer {
  font-size: 14px;
  color: #111827;
}

.message-enter-from { opacity: 0; transform: translateY(20px); }
.message-enter-active { transition: all 0.3s ease; }
.message-enter-to { opacity: 1; transform: translateY(0); }

.chat-input-floating {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%) translateY(20px);
  display: flex;
  gap: 10px;
  background: #ffffff;
  padding: 12px 16px;
  border-radius: 32px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 1000;
  width: 60%;
  max-width: 800px;
  min-width: 300px;
  opacity: 0;
  transition: all 0.3s ease-in-out;
}

.chat-input-floating.show { transform: translateX(-50%) translateY(0); opacity: 1; }

.message-input { flex: 1; padding: 12px 16px; border-radius: 24px; border: 1px solid #d1d5db; outline: none; font-size: 14px; transition: all 0.2s ease-in-out; }
.message-input:focus { border-color: #3b82f6; box-shadow: 0 0 8px rgba(59,130,246,0.3); }

.send-button { padding: 12px 24px; border-radius: 24px; border: none; background: linear-gradient(135deg, #3b82f6, #06b6d4); color: white; cursor: pointer; font-weight: 500; transition: transform 0.1s ease-in-out, box-shadow 0.1s ease-in-out; }
.send-button:active { transform: scale(0.95); box-shadow: 0 2px 6px rgba(0,0,0,0.2); }

.chat-main::-webkit-scrollbar { width: 6px; }
.chat-main::-webkit-scrollbar-thumb { background-color: rgba(107,114,128,0.3); border-radius: 3px; }
</style>
