# 🎬 会话切换动画实现指南

## 功能说明

当用户点击不同的会话时，会显示以下动画效果：

### 1️⃣ **现有消息离开动画**
- 当切换会话时，原来的消息气泡会以 **slideOut** 动画淡出并向上缩小
- 动画时长：**300ms**
- 使用缓动函数：**ease-out**
- 效果：opacity 从 1 到 0，scale 从 1 到 0.92，translateY 从 0 到 -12px

### 2️⃣ **加载状态指示器**
- 消息淡出后，显示一个加载指示器覆盖聊天区域
- 包含：
  - 旋转的加载 spinner（圆形旋转圈）
  - "正在加载会话..." 文本
  - 文本带有脉冲动画
- 加载指示器淡入时长：**300ms**

### 3️⃣ **新消息进入动画**
- 新会话的消息加载完成后，消息气泡逐个从下方滑入
- 动画时长：**400ms**
- 使用缓动函数：**cubic-bezier(0.34, 1.56, 0.64, 1)** （弹性效果）
- 效果：opacity 从 0 到 1，scale 从 0.92 到 1，translateY 从 12px 到 0

## 技术实现

### 核心代码

#### 1. 状态管理
```typescript
const isLoadingMessages = ref(false);  // 加载状态标志
```

#### 2. 模板结构
```vue
<main class="chat-main" ref="scrollContainer">
  <!-- 加载状态指示器 -->
  <div v-if="isLoadingMessages" class="loading-indicator">
    <div class="loading-spinner"></div>
    <p>正在加载会话...</p>
  </div>
  
  <!-- 消息列表，带 transition-group -->
  <transition-group 
    v-else
    name="messageList" 
    tag="div" 
    class="chat-messages"
    :key="`session-${props.sessionId}`"
  >
    <!-- 消息项 -->
  </transition-group>
</main>
```

#### 3. 关键 CSS 动画

**消息离开动画（slideOut）**
```css
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

.messageList-leave-active {
  animation: messageSlideOut 0.3s ease-out;
  position: absolute;
}
```

**加载 Spinner**
```css
.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(42, 157, 244, 0.1);
  border-top-color: #2a9df4;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

**消息进入动画（slideIn）**
```css
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

.messageList-enter-active {
  animation: messageSlideIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

## 动画时间轴

```
用户点击新会话
        ↓
[300ms] 旧消息淡出和缩小
        ↓
[300ms] 加载指示器淡入（同时进行）
        ↓
加载新会话数据...
        ↓
加载完成，加载指示器淡出
        ↓
[400ms] 新消息逐个弹性滑入
        ↓
完成
```

## 交互体验亮点

✅ **流畅过渡** - 无缝衔接旧消息离开和新消息进入
✅ **视觉反馈** - 加载指示器让用户知道正在加载
✅ **弹性效果** - 新消息进入时的弹性动画增加趣味性
✅ **深色模式支持** - 加载指示器在深色模式也美观
✅ **性能优化** - 使用 transform 和 opacity，避免重排

## 自定义选项

### 调整消息离开速度
修改 `messageSlideOut` 和 `.messageList-leave-active` 的时长（默认 300ms）

### 调整消息进入速度
修改 `messageSlideIn` 和 `.messageList-enter-active` 的时长（默认 400ms）

### 调整加载 Spinner 速度
修改 `spin` 动画的时长（默认 1s）

### 修改加载文本
在模板中修改：
```vue
<p>正在加载会话...</p>  <!-- 改为其他文本 -->
```

## 浏览器兼容性

| 浏览器 | 支持 | 备注 |
|------|------|------|
| Chrome | ✅ | 完全支持 |
| Firefox | ✅ | 完全支持 |
| Safari | ✅ | 完全支持 |
| Edge | ✅ | 完全支持 |
| IE11 | ❌ | 不支持 transform3d |

## 相关文件

- `chat-web-front/src/components/home/component/chatbox.vue` - 主要实现文件
- 需要的导入：
  - `transition-group` from `vue`（已内置）
  - CSS 动画（已定义）

---

**最后更新**: 2025-10-31
