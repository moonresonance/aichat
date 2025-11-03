import { computed, ref, watch } from "vue";
import { defineStore } from "pinia";
import { usePreferredDark } from "@vueuse/core";

export type ThemeMode = "light" | "dark" | "system";

const applyThemeToDom = (isDark: boolean) => {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  root.dataset.theme = isDark ? "dark" : "light";
  root.style.colorScheme = isDark ? "dark" : "light";
};

export const useThemeStore = defineStore(
  "theme",
  () => {
    const preferredDark = usePreferredDark({ window: typeof window !== "undefined" ? window : undefined });
    const theme = ref<ThemeMode>("system");

    const isDark = computed(() => {
      if (theme.value === "dark") return true;
      if (theme.value === "light") return false;
      return preferredDark.value;
    });

    const setTheme = (next: ThemeMode) => {
      theme.value = next;
    };

    const toggleTheme = () => {
      setTheme(isDark.value ? "light" : "dark");
    };

    watch(
      () => isDark.value,
      (value) => {
        applyThemeToDom(value);
      },
      { immediate: true }
    );

    watch(
      () => theme.value,
      () => {
        if (theme.value === "system") {
          applyThemeToDom(isDark.value);
        }
      }
    );

    return {
      theme,
      isDark,
      setTheme,
      toggleTheme,
    };
  },
  {
    persist: true,
  }
);
