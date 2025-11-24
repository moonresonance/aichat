<script setup lang="js">

import * as live2d from 'live2d-render';
import { onMounted, defineExpose, ref } from "vue";

// 使用全局标志防止重复初始化
const isInitialized = ref(false);

onMounted(async () => {
  // 检查是否已在全局窗口对象上标记初始化完成
  if (window.__live2dInitialized__) {
    isInitialized.value = true;
    console.log('Live2D already initialized');
    return;
  }

  try {
    await live2d.initializeLive2D({
      CanvasId: "live2d-container",
      BackgroundRGBA: [0.0, 0.0, 0.0, 0.0],
      ResourcesPath: "/model/cat/sdwhite cat free.model3.json",
      CanvasSize: { height: 300, width: 180 },
      ShowToolBox: true,
      LoadFromCache: true
    });

    // 标记初始化完成
    window.__live2dInitialized__ = true;
    isInitialized.value = true;
    console.log('Live2D initialization complete');
  } catch (error) {
    console.error('Live2D initialization failed:', error);
  }
});

// 关闭 Live2D 气泡显示
const sendMessage = async () => {
  if (isInitialized.value) {
    live2d.setMessageBox("");
  }
};

defineExpose({
  sendMessage
});

</script>
<template>
  <div id="live2d-container">
    <canvas id="live2d-container">
    </canvas>
  </div>
</template>

<style>
/* Live2D 面板右侧居中 */
.live2d-panel {
  position: fixed;
  top: 50%;
  right: 30px;
  transform: translateY(-50%);
  width: 200px; /* 默认宽度 */
  height: auto;
  aspect-ratio: 2 / 3; /* 保持模型比例 */
  z-index: 150;
  pointer-events: none;
  transition: width 0.3s ease;
  will-change: auto;
}

#live2d-panel:hover {
  pointer-events: auto;
}

/* Canvas 填充容器 */
#live2d-panel canvas {
  width: 100% !important;
  height: 100% !important;
  display: block;
}

/* 夜间模式下调整模型亮度 - 保持透明背景 */
#live2d-container {
  background: transparent !important;
  border-radius: 0 !important;
  padding: 0 !important;
}

[data-theme="dark"] #live2d-container {
  filter: brightness(0.85) contrast(0.92) saturate(0.95);
  transition: filter 0.3s ease;
  background: transparent !important;
  will-change: filter;
}

/* 响应式缩放 */
@media (max-width: 1024px) {
  #live2d-panel { width: 160px; }
}
@media (max-width: 768px) {
  #live2d-panel { width: 140px; }
}
@media (max-width: 480px) {
  #live2d-panel { width: 120px; right: 10px; }
}

/* 消息气泡保持原来的浮动动画 */
#live2dMessageBox-content {
  background-color: #FF95BC;
  color: white;
  font-family: var(--base-font);
  padding: 10px;
  height: fit-content;
  width: fit-content;
  border-radius: 0.7em;
  word-break: break-all;
  border-right: 1px solid transparent;
  transform-origin: bottom right;
  
  /* 文字淡入动画 */
  animation: textFadeIn 0.3s ease-out;
  /* 背景微妙脉冲效果 */
  box-shadow: 0 4px 15px rgba(255, 149, 188, 0.4);
  transition: box-shadow 0.3s ease;
}

/* 文字逐字淡入动画 */
@keyframes textFadeIn {
  from {
    opacity: 0.7;
    transform: scale(0.98);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.live2dMessageBox-content-hidden {
  opacity: 0;
  transform: scale(0.5) translateY(20px);
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1),
  opacity 0.6s ease-in;
}

.live2dMessageBox-content-visible {
  opacity: 1;
  transform: scale(1) translateY(0);
  transition: transform 0.35s cubic-bezier(0.4, 1.2, 0.2, 1),
  opacity 0.35s ease-out;
  animation: float 2s ease-in-out infinite alternate;
}

@keyframes float {
  0% { transform: scale(1) translateY(0); }
  50% { transform: scale(1) translateY(-3px); }
  100% { transform: scale(1) translateY(0); }
}

</style>