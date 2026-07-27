<script setup lang="ts">
import { initializeAuth } from '@/utils/request'

defineOptions({
  name: 'App',
})

onLaunch(() => {
  // 页面请求会复用该 Promise 并等待登录，此处仅负责尽早启动登录。
  initializeAuth().catch(() => {})
})
</script>

<style lang="scss">
@use '@wot-ui/ui/styles/theme/index' as *;

page {
  background: #f8fafc;
  color: #1c1c1a;
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
}

.page-wraper {
  min-height: calc(100vh - var(--window-top));
  box-sizing: border-box;
  background: var(--wot-filled-content);
}

// .wot-theme-dark.page-wraper {
//   background: #222;
// }
</style>
