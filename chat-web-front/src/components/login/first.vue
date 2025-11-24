<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElForm, ElFormItem, ElInput, ElButton, ElMessage, ElCard, selectProps } from 'element-plus';
import { ArrowRight, User, Lock } from '@element-plus/icons-vue';
import {login,register} from "@/api/userapi.js";
import { useRouter } from 'vue-router';
import {useUserStore} from "@/stores/user.js";
import { useLoadingStore } from '@/stores/loading';
import Live2d from "@/components/home/component/live2d.vue";

const userStore=useUserStore();
const loadingStore = useLoadingStore();
const router = useRouter();
const isLoginMode = ref(true);
const isTransitioning = ref(false);
const formData = reactive({ name: '', password: '',confirmPassword:''});
const rules = reactive({
  name: [{ required: true, message: '用户名不能为空', trigger: 'blur' }],
  email: [
    { required: true, message: '邮箱不能为空', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '密码不能为空', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {  validator: (rule, value, callback) => {
        if (value !== formData.password) callback(new Error('两次密码输入不一致'));
        else callback();
      }, trigger: 'blur' }
  ]
});

const formRef = ref(null);

const toggleMode = () => {
  isTransitioning.value = true;
  setTimeout(() => {
    isLoginMode.value = !isLoginMode.value;
    formRef.value.resetFields();
    isTransitioning.value = false;
  }, 600);
};

const handleSubmit = async () => {
  await formRef.value.validate();
  try {
    if (isLoginMode.value) {
      loadingStore.show(0);
      let progress = 0;
      
      // 模拟进度加载
      const timer = setInterval(() => {
        if (progress < 90) {
          // 随机增加进度，越接近90越慢
          const increment = Math.random() * 2 + 0.5;
          progress += increment;
          if (progress > 90) progress = 90;
          loadingStore.setProgress(progress);
        }
      }, 100);

      try {
        const data = await login(formData);
        console.log(data);
        
        if(data.code !== 200){
          clearInterval(timer);
          loadingStore.hide();
          ElMessage.error(data.msg);
          return;
        }

        userStore.login(data.data);
        
        clearInterval(timer);
        
        // 登录成功后，快速跑完剩余进度到 100
        const finishTimer = setInterval(() => {
          progress += 5;
          if (progress >= 100) {
            progress = 100;
            loadingStore.setProgress(100);
            clearInterval(finishTimer);
            
            setTimeout(() => {
              loadingStore.hide();
              router.push('/home');
              ElMessage.success(data.msg);
            }, 300);
          } else {
            loadingStore.setProgress(progress);
          }
        }, 10);

      } catch (e) {
        clearInterval(timer);
        loadingStore.hide();
        throw e;
      }
    } else {
      const data=await register(formData);
      ElMessage.success(data.msg);
      toggleMode();
    }
  } catch (error) {
    ElMessage.error('操作失败: ' + (error.message || '未知错误'));
  }
};

onMounted(() => {
  const canvas = document.getElementById('tech-grid');
  const ctx = canvas.getContext('2d');
  let width = (canvas.width = window.innerWidth);
  let height = (canvas.height = window.innerHeight);

  const particles = Array.from({ length: 100 }, () => ({
    x: Math.random() * width,
    y: Math.random() * height,
    vx: (Math.random() - 0.5) * 1.2,
    vy: (Math.random() - 0.5) * 1.2,
    r: Math.random() * 3 + 1,
    color: `hsl(${Math.random() * 360}, 70%, 60%)`
  }));

  function draw() {
    ctx.clearRect(0, 0, width, height);
    particles.forEach((p, i) => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > width) p.vx *= -1;
      if (p.y < 0 || p.y > height) p.vy *= -1;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.fill();

      for (let j = i + 1; j < particles.length; j++) {
        const q = particles[j];
        const dx = p.x - q.x;
        const dy = p.y - q.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 150) {
          ctx.strokeStyle = `rgba(255,255,255,${1 - dist / 150})`;
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(q.x, q.y);
          ctx.stroke();
        }
      }
    });
    requestAnimationFrame(draw);
  }

  draw();
  window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    width = canvas.width;
    height = canvas.height;
  });
});
</script>

<template>
  <div class="app-container">
    <!-- 粒子背景 -->
    <canvas id="tech-grid"></canvas>

    <!-- 登录/注册卡片 -->
    <div class="form-container"> <!-- 修复宽度问题 -->
      <el-card class="form-card">
        <div class="form-header" :class="{ 'header-transition': isTransitioning }">
          <h2>{{ isLoginMode ? '欢迎登录' : '创建账号' }}</h2>
          <p>{{ isLoginMode ? '请输入您的账号信息' : '注册新账号开始您的旅程' }}</p>
        </div>

        <el-form ref="formRef" :model="formData" :rules="rules" class="form-body" :class="{ 'body-transition': isTransitioning }" @keydown.enter="handleSubmit">
          <!-- 统一表单项样式 -->
          <el-form-item label="用户名" prop="username" class="uniform-form-item">
            <el-input v-model="formData.name" placeholder="请输入用户名" :prefix-icon="User" />
          </el-form-item>
          <el-form-item label="密码" prop="password" class="uniform-form-item">
            <el-input v-model="formData.password" type="password" placeholder="请输入密码" :prefix-icon="Lock" />
          </el-form-item>
          <el-form-item v-if="!isLoginMode" label="确认密码" prop="confirmPassword" class="uniform-form-item">
            <el-input v-model="formData.confirmPassword" type="password" placeholder="请再次输入密码" :prefix-icon="Lock" />
          </el-form-item>

          <el-button type="primary" class="submit-btn" @click="handleSubmit">
            {{ isLoginMode ? '登录' : '注册' }}
            <ArrowRight class="ml-2" />
          </el-button>

          <div class="switch-mode">
            <el-button type="text" @click="toggleMode">
              {{ isLoginMode ? '没有账号？立即注册' : '已有账号？立即登录' }}
            </el-button>
            <el-button type="text" @click="router.push('/intro')">
              了解产品
            </el-button>
          </div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
/* 页面背景容器 */
.app-container {
  width: 100%;
  height: 100%;
  position: relative;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(-45deg, #0f172a, #1e1b4b, #1e40af, #4c1d95);
  background-size: 300% 300%;
  animation: gradientBG 15s ease infinite;
  overflow: hidden;
}

/* 背景渐变动画 */
@keyframes gradientBG {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* 粒子背景 canvas */
#tech-grid {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
  display: block;
  filter: blur(1px) contrast(1.2);
}

/* 表单容器 */
.form-container {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 600px; /* 卡片更大 */
  padding: 30px;
  margin: auto;
}

/* 科技感卡片 */
.form-card {
  border-radius: 20px;
  padding: 40px 36px;
  background: rgba(30, 25, 60, 0.75); /* 半透明深紫蓝 */
  border: 1px solid rgba(99, 102, 241, 0.5);
  box-shadow: 0 0 25px rgba(99, 102, 241, 0.5),
  inset 0 0 25px rgba(236, 72, 153, 0.25);
  backdrop-filter: blur(20px);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  animation: cardEnter 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 卡片边框炫光动画 */
.form-card::before {
  content: "";
  position: absolute;
  inset: -2px;
  border-radius: 22px;
  padding: 2px;
  background: linear-gradient(135deg, #6366f1, #ec4899, #06b6d4, #8b5cf6);
  background-size: 400% 400%;
  animation: borderFlow 6s linear infinite;
  mask:
    linear-gradient(#000 0 0) content-box,
    linear-gradient(#000 0 0);
  -webkit-mask:
      linear-gradient(#000 0 0) content-box,
      linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  z-index: -1;
}

@keyframes borderFlow {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* 表单头部过渡 */
.form-header.header-transition {
  animation: headerSwitch 0.6s ease-in-out;
}

@keyframes headerSwitch {
  0% {
    opacity: 1;
    transform: translateY(0px) rotateX(0deg);
  }
  50% {
    opacity: 0;
    transform: translateY(-10px) rotateX(90deg);
  }
  100% {
    opacity: 1;
    transform: translateY(0px) rotateX(0deg);
  }
}

/* 表单体过渡 */
.form-body.body-transition {
  animation: bodyShift 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes bodyShift {
  0% {
    opacity: 1;
    transform: translateX(0px) scale(1);
  }
  50% {
    opacity: 0;
    transform: translateX(20px) scale(0.98);
  }
  100% {
    opacity: 1;
    transform: translateX(0px) scale(1);
  }
}


/* 表单头部 */
.form-header {
  text-align: center;
  margin-bottom: 28px;
}

.form-header h2 {
  font-size: 30px;
  font-weight: bold;
  color: #60a5fa;
  text-shadow: 0 0 12px rgba(96,165,250,0.8);
}

.form-header p {
  font-size: 16px;
  color: #9ca3af;
}

/* 表单体 */
.form-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 使用 :deep() 保证 scoped 下对 Element Plus 样式生效 */
:deep(.el-form-item__label) {
  width: 120px; /* 标签宽度 */
  text-align: left;
  color: #73ade8;
  font-weight: 500;
  padding-right: 40px;
}

:deep(.el-input__wrapper) {
  width: calc(100% - 120px); /* 与标签宽度对应 */
  background: rgba(30, 41, 59, 0.9);
  border: 1px solid rgba(99, 102, 241, 0.4);
  box-shadow: inset 0 0 6px rgba(99, 102, 241, 0.2);
  border-radius: 12px;
  transition: all 0.3s ease;
  padding: 10px 14px; /* 增加垂直内边距，更大输入框 */
  position: relative;
  animation: inputEnter 0.5s ease-out backwards;
}

:deep(.el-form-item:nth-child(1) .el-input__wrapper) {
  animation-delay: 0.1s;
}

:deep(.el-form-item:nth-child(2) .el-input__wrapper) {
  animation-delay: 0.2s;
}

:deep(.el-form-item:nth-child(3) .el-input__wrapper) {
  animation-delay: 0.3s;
}

@keyframes inputEnter {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

:deep(.el-input__wrapper:focus-within) {
  border-color: #ec4899;
  box-shadow: 0 0 12px rgba(236, 72, 153, 0.6),
              inset 0 0 8px rgba(236, 72, 153, 0.2);
  background: rgba(30, 41, 59, 0.95);
  transform: scale(1.01);
}

/* 提交按钮 */
.submit-btn {
  position: relative;
  width: 100%;
  height: 50px;
  padding: 0;
  font-size: 18px;
  font-weight: bold;
  border-radius: 12px;
  border: 2px solid transparent;
  color: white;
  cursor: pointer;
  background: linear-gradient(135deg, #6366f1, #ec4899, #06b6d4) border-box;
  background-clip: padding-box;
  transition: all 0.3s ease-in-out;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.6),
              inset 0 0 15px rgba(99, 102, 241, 0.2);
  animation: buttonGlow 3s ease-in-out infinite;
}

.submit-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
  z-index: 1;
}

.submit-btn:hover::before {
  left: 100%;
}

.submit-btn::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 10px;
  padding: 2px;
  background: linear-gradient(45deg, #6366f1, #ec4899, #06b6d4, #8b5cf6, #6366f1);
  background-size: 300% 300%;
  animation: gradientBorder 3s ease-in-out infinite;
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  z-index: -1;
  opacity: 0.8;
}

.submit-btn:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 8px 25px rgba(236, 72, 153, 0.8),
              0 0 35px rgba(6, 182, 212, 0.6),
              inset 0 0 20px rgba(99, 102, 241, 0.4);
  animation: buttonGlowHover 0.6s ease-in-out;
}

.submit-btn:active {
  transform: translateY(-1px) scale(0.98);
}

@keyframes buttonGlow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.6),
                inset 0 0 15px rgba(99, 102, 241, 0.2);
  }
  50% {
    box-shadow: 0 0 30px rgba(236, 72, 153, 0.7),
                inset 0 0 20px rgba(99, 102, 241, 0.3);
  }
}

@keyframes buttonGlowHover {
  0% {
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.6);
  }
  50% {
    box-shadow: 0 8px 35px rgba(236, 72, 153, 0.9),
                0 0 40px rgba(6, 182, 212, 0.7);
  }
  100% {
    box-shadow: 0 8px 25px rgba(236, 72, 153, 0.8),
                0 0 35px rgba(6, 182, 212, 0.6);
  }
}

@keyframes gradientBorder {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* 切换模式按钮 */
.switch-mode {
  margin-top: 18px;
  text-align: center;
  animation: fadeIn 0.8s ease-out 0.6s backwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.switch-mode .el-button {
  color: #a3b2e5;
  transition: all 0.3s ease;
  position: relative;
  font-size: 14px;
}

.switch-mode .el-button::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #6366f1, #ec4899);
  transition: width 0.3s ease;
}

.switch-mode .el-button:hover {
  color: #f472b6;
}

.switch-mode .el-button:hover::after {
  width: 100%;
}
</style>


