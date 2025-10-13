<script setup lang="js">

import * as live2d from 'live2d-render';

import {onMounted,defineExpose} from "vue";


onMounted(async () => {
  await live2d.initializeLive2D({

    CanvasId:"live2d-container",
    // live2d 所在区域的背景颜色
    BackgroundRGBA: [0.0, 0.0, 0.0, 0.0],
    // live2d 的 model3.json 文件的相对 根目录 的路径
    ResourcesPath: "/model/cat/sdwhite cat free.model3.json",

    // live2d 的大小
    CanvasSize: {
      height: 300,
      width: 180
    },
    // 展示工具箱（可以控制 live2d 的展出隐藏，使用特定表情）
    ShowToolBox: true,
    // 是否使用 indexDB 进行缓存优化，这样下一次载入就不会再发起网络请求了
    LoadFromCache: true
  });

  console.log('finish loading');
});

const sendMessage = (message) => {
  live2d.setMessageBox(message);
}
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
}

#live2d-panel:hover {
  pointer-events: auto;
  transform: translateY(-50%) scale(1.05);
}

/* Canvas 填充容器 */
#live2d-panel canvas {
  width: 100% !important;
  height: 100% !important;
  display: block;
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
  border-radius: 0.7em;
  word-break: break-all;
  border-right: 1px solid transparent;
  transform-origin: bottom right;
}

.live2dMessageBox-content-hidden {
  opacity: 0;
  transform: scale(0.5) translateY(20px);
  transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1),
  opacity 0.35s ease-in;
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

