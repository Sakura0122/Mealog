<script setup lang="ts">
type ThemeMode = 'light' | 'dark'

const theme = ref<ThemeMode>('light')

const setTheme = (value?: string) => {
  if (value === 'light' || value === 'dark')
    theme.value = value
}

const handleThemeChange: Parameters<typeof uni.onThemeChange>[0] = (result) => {
  setTheme(result.theme)
}

onBeforeMount(() => {
  // #ifdef MP-WEIXIN
  setTheme(uni.getAppBaseInfo().theme)
  // #endif
  // #ifndef MP-WEIXIN
  setTheme(uni.getSystemInfoSync().theme)
  // #endif
  uni.onThemeChange(handleThemeChange)
})

onUnmounted(() => {
  uni.offThemeChange(handleThemeChange)
})
</script>

<template>
  <wd-config-provider :theme="theme" :custom-class="`page-wraper ${theme}`">
    <ku-root-view />
    <global-toast />
    <global-dialog />
  </wd-config-provider>
</template>
