<script setup lang="ts">
withDefaults(defineProps<{
  close?: boolean
  edit?: boolean
  more?: boolean
  showBack?: boolean
}>(), {
  close: false,
  edit: false,
  more: false,
  showBack: true,
})

const emit = defineEmits<{
  edit: []
  more: []
}>()

const goBack = () => {
  uni.navigateBack({
    // 分享卡片冷启动时没有上一页，关闭后应回到应用首页。
    fail: () => uni.reLaunch({ url: '/pages/index/index' }),
  })
}

const rightInset = ref(0)
// 微信原生胶囊位于导航栏右侧，操作按钮需要精确避开其占用区域。
// #ifdef MP-WEIXIN
const menuButtonRect = uni.getMenuButtonBoundingClientRect()
const systemInfo = uni.getSystemInfoSync()
rightInset.value = systemInfo.windowWidth - menuButtonRect.left
// #endif
</script>

<template>
  <!-- 统一使用组件库计算状态栏和导航栏高度，避免自定义导航内容进入系统区域。 -->
  <wd-navbar safe-area-inset-top custom-style="background: transparent;">
    <template #left>
      <button v-if="showBack" class="m-0 h-8 w-8 flex items-center justify-center border-0 bg-transparent p-0 after:border-0" aria-label="返回" @click="goBack">
        <wd-icon name="arrow-left" size="22px" color="#1c1c1a" />
      </button>
    </template>
    <template #right>
      <view class="flex items-center gap-3" :style="{ marginRight: `${rightInset}px` }">
        <button v-if="edit" class="m-0 h-8 w-8 flex items-center justify-center border-0 bg-transparent p-0 after:border-0" aria-label="编辑" @click="emit('edit')">
          <wd-icon name="edit" size="21px" color="#1c1c1a" />
        </button>
        <button v-if="more" class="m-0 h-8 w-8 flex items-center justify-center border-0 bg-transparent p-0 after:border-0" aria-label="更多" @click="emit('more')">
          <wd-icon name="more-vertical" size="21px" color="#5d5d5b" />
        </button>
        <button v-if="close" class="m-0 h-8 w-8 flex items-center justify-center border-0 bg-transparent p-0 after:border-0" aria-label="关闭" @click="goBack">
          <wd-icon name="close" size="21px" color="#1c1c1a" />
        </button>
      </view>
    </template>
  </wd-navbar>
</template>
