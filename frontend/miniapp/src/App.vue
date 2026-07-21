<script setup lang="ts">
defineOptions({
  name: 'App',
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
