<template>
  <div class="theme-toggle" role="radiogroup" aria-label="主题模式">
    <button
      v-for="option in options"
      :key="option.value"
      class="theme-button"
      type="button"
      role="radio"
      :aria-checked="activeMode === option.value"
      :class="{ active: activeMode === option.value, dense }"
      @click="select(option.value)"
    >
      <span class="icon" aria-hidden="true" v-html="option.icon"></span>
      <span v-if="!dense" class="label">{{ option.label }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useThemeStore, type ThemeMode } from "@/stores/theme";

const props = withDefaults(defineProps<{ dense?: boolean }>(), {
  dense: false,
});

const themeStore = useThemeStore();
const activeMode = computed(() => themeStore.theme);

interface ToggleOption {
  value: ThemeMode;
  label: string;
  icon: string;
}

const options: ToggleOption[] = [
  {
    value: "light",
    label: "明亮",
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`,
  },
  {
    value: "dark",
    label: "深色",
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 0 1 11.21 3 7 7 0 1 0 21 12.79z"/></svg>`,
  },
  {
    value: "system",
    label: "系统",
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8"/><path d="M12 17v4"/></svg>`,
  },
];

const select = (mode: ThemeMode) => {
  if (mode !== activeMode.value) {
    themeStore.setTheme(mode);
  }
};
</script>

<style scoped>
.theme-toggle {
  display: inline-flex;
  align-items: center;
  background: var(--control-bg);
  border: 1px solid var(--control-border);
  border-radius: 999px;
  padding: 4px;
  gap: 4px;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.theme-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: none;
  border-radius: 999px;
  padding: 6px 14px;
  background: transparent;
  color: var(--control-muted);
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.02em;
  transition: color 0.2s ease, background 0.2s ease, transform 0.2s ease;
}

.theme-button.dense {
  padding: 6px;
}

.theme-button .icon {
  width: 16px;
  height: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.theme-button .icon svg {
  width: 100%;
  height: 100%;
}

.theme-button .label {
  white-space: nowrap;
}

.theme-button:hover {
  color: var(--accent-color);
  background: var(--accent-ghost);
}

.theme-button.active {
  color: var(--accent-contrast);
  background: var(--accent-color);
  box-shadow: 0 6px 14px rgba(59, 130, 246, 0.25);
}

.theme-button.active:hover {
  transform: translateY(-1px);
}

:global([data-theme="dark"]) .theme-toggle {
  background: var(--surface-overlay);
}
</style>
