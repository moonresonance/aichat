# 🎬 前端动画效果指南

## 已添加的动画效果总览

### 1️⃣ **页面进入动画**
- **frameSlideIn**: 整个聊天框从下方滑入并弹起（600ms）
- **sidebarSlideIn**: 左侧菜单从左边滑入（500ms）
- **fadeIn**: 整个首页淡入效果（450ms）

### 2️⃣ **菜单项动画**
- **itemFadeInLeft**: 菜单项依次从左滑入，带有延迟效果
- **hoverGlow**: 菜单项悬停时产生光晕扩散效果
- **buttonBounce**: 按钮弹性进入动画

### 3️⃣ **消息动画**
- **messageSlideIn**: 消息气泡从下方滑入（400ms）
- **messageShine**: 用户消息顶部闪光效果
- **thinkingPulse**: "AI 正在思考"文本脉冲效果（1.4s 循环）

### 4️⃣ **输入框动画**
- **inputFadeIn**: 输入框从下方淡入并滑入（500ms）
- **buttonPopIn**: 发送按钮弹出效果（400ms）
- **iconSpin**: 图标按钮旋转动画（600ms）

### 5️⃣ **交互动画**
- **用户按钮**: 悬停时向上移动，阴影增强
- **发送按钮**: 悬停时放大，点击时缩小反馈
- **消息内容**: 悬停时向上移动，阴影增强
- **操作按钮**: 缩放和阴影反馈

### 6️⃣ **Live2D 角色动画**
- **live2dSlideIn**: 角色从右侧滑入（600ms）
- **live2dPulse**: 角色悬停时脉冲缩放效果
- **float**: 消息气泡浮动动画（2s 循环）

## 动画参数详解

### 缓动函数
- **cubic-bezier(0.34, 1.56, 0.64, 1)**: 弹性/弹跳效果（用于进入动画）
- **cubic-bezier(0.4, 0, 0.2, 1)**: 标准缓出效果
- **ease-in-out**: 平滑进出
- **ease-out**: 平滑结束

### 关键动画参数
| 动画 | 时长 | 缓动 | 用途 |
|------|------|------|------|
| frameSlideIn | 600ms | cubic-bezier | 主框架进入 |
| sidebarSlideIn | 500ms | cubic-bezier | 侧边栏进入 |
| messageSlideIn | 400ms | cubic-bezier | 消息进入 |
| itemFadeInLeft | 400ms | cubic-bezier | 菜单项进入 |
| thinkingPulse | 1400ms | ease-in-out | 思考指示 |
| messageShine | 600ms | ease-out | 消息闪光 |

## 动画延迟

菜单项使用 stagger 效果，逐项延迟：
```
第1项: 50ms延迟
第2项: 100ms延迟
第3项: 150ms延迟
第4项: 200ms延迟
第5项: 250ms延迟
```

## 悬停效果

### 菜单项 (.menu-item:hover)
- 背景色改变
- 圆形光晕扩散（hoverGlow）
- 轻微上移

### 按钮 (.icon-btn:hover)
- 图标旋转（iconSpin）
- 上移 2px
- 阴影增强

### 消息 (.message-content:hover)
- 上移 1px
- 阴影增强

## 点击反馈

### 发送按钮 (.send-button)
- **:hover**: scale(1.08)
- **:active**: scale(0.95)

### 操作按钮 (.act-btn)
- **:hover**: scale(1.08)
- **:active**: scale(0.95)

## 响应式动画

在移动设备上（max-width: 768px）：
- 菜单项延迟减少
- 动画时长可能需要调整
- Live2D 组件大小自适应

## 性能优化建议

✅ 使用 `transform` 和 `opacity` 进行动画
✅ 使用 `cubic-bezier` 而非 `ease` 获得更好效果
✅ 动画时长控制在 300-600ms
✅ 避免在滚动时频繁触发重排

## 浏览器兼容性

- Chrome/Edge: ✅ 完全支持
- Firefox: ✅ 完全支持
- Safari: ✅ 完全支持（需要 -webkit- 前缀）
- 已添加 `-webkit-backdrop-filter` 用于 Safari 支持

## 自定义动画

若要修改动画效果，请编辑相应的 `@keyframes` 规则，例如：

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
```

调整 `from` 和 `to` 的 `transform` 和 `opacity` 值来创建不同效果。

---

**最后更新**: 2025-10-31
**作者**: GitHub Copilot
