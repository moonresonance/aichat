<script setup lang="js">

import * as live2d from 'live2d-render';
import { onMounted, defineExpose } from "vue";

onMounted(async () => {
  await live2d.initializeLive2D({
    CanvasId: "live2d-container",
    BackgroundRGBA: [0.0, 0.0, 0.0, 0.0],
    ResourcesPath: "/model/cat/sdwhite cat free.model3.json",
    CanvasSize: { height: 300, width: 180 },
    ShowToolBox: true,
    LoadFromCache: true
  });

  console.log('finish loading');
});

// 关闭 Live2D 气泡显示
const sendMessage = async () => {
  live2d.setMessageBox("");
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
  transition: width 0.3s ease, transform 0.3s ease;
  animation: live2dSlideIn 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes live2dSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50%) translateX(60px) scale(0.7);
  }
  to {
    opacity: 1;
    transform: translateY(-50%) translateX(0) scale(1);
  }
}

#live2d-panel:hover {
  pointer-events: auto;
  animation: live2dPulse 0.4s ease-out;
}

@keyframes live2dPulse {
  0% { transform: translateY(-50%) scale(1); }
  50% { transform: translateY(-50%) scale(1.08); }
  100% { transform: translateY(-50%) scale(1.05); }
}

/* Canvas 填充容器 */
#live2d-panel canvas {
  width: 100% !important;
  height: 100% !important;
  display: block;
}

/* 夜间模式下调整模型亮度 */
[data-theme="dark"] #live2d-container {
  filter: brightness(0.85) contrast(0.92) saturate(0.95);
  transition: filter 0.3s ease;
  /* 添加背景隔离层，防止星空闪烁影响模型 */
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  padding: 8px;
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

