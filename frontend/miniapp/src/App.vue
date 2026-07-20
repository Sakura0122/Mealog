<script setup lang="ts">
defineOptions({
  name: 'App',
})
</script>

<style lang="scss">
@use '@wot-ui/ui/styles/theme/index' as *;

.page-wraper {
  min-height: calc(100vh - var(--window-top));
  box-sizing: border-box;
  background: var(--wot-filled-content);
}

// .wot-theme-dark.page-wraper {
//   background: #222;
// }
</style>
