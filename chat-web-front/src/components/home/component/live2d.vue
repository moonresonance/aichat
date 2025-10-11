<script setup lang="js">

import * as live2d from 'live2d-render';

import {onMounted,defineExpose} from "vue";


onMounted(async () => {
  await live2d.initializeLive2D({
    // live2d 所在区域的背景颜色
    BackgroundRGBA: [0.0, 0.0, 0.0, 0.0],
    // live2d 的 model3.json 文件的相对 根目录 的路径
    ResourcesPath: '/model/Snow Leopard.model3.json',

    // live2d 的大小
    CanvasSize: {
      height: 500,
      width: 300
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

<style>
#live2dMessageBox-content {
  background-color: #FF95BC;
  color: white;
  font-family: var(--base-font);
  padding: 10px;
  height: fit-content;
  border-radius: 0.7em;
  word-break: break-all;
  border-right: 1px solid transparent;
  transform-origin: bottom right; /* 从右下角弹出 */
}

/* 消失状态 */
.live2dMessageBox-content-hidden {
  opacity: 0;
  transform: scale(0.5) translateY(20px);
  transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1),
  opacity 0.35s ease-in;
}

/* 出现状态 */
.live2dMessageBox-content-visible {
  opacity: 1;
  transform: scale(1) translateY(0);
  transition: transform 0.35s cubic-bezier(0.4, 1.2, 0.2, 1),
  opacity 0.35s ease-out;

  /* 添加轻微浮动动画 */
  animation: float 2s ease-in-out infinite alternate;
}

/* 浮动关键帧 */
@keyframes float {
  0% { transform: scale(1) translateY(0); }
  50% { transform: scale(1) translateY(-3px); }
  100% { transform: scale(1) translateY(0); }
}

</style>

