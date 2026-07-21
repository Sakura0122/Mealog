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

const goBack = () => {
  uni.navigateBack()
}
</script>

<template>
  <view class="h-16 flex items-center px-5">
    <button v-if="showBack" class="m-0 h-8 w-8 flex items-center justify-center border-0 bg-transparent p-0 after:border-0" aria-label="返回" @click="goBack">
      <wd-icon name="arrow-left" size="22px" color="#1c1c1a" />
    </button>
    <view class="ml-auto flex items-center gap-3">
      <button v-if="edit" class="m-0 h-8 w-8 flex items-center justify-center border-0 bg-transparent p-0 after:border-0" aria-label="编辑">
        <wd-icon name="edit" size="21px" color="#1c1c1a" />
      </button>
      <button v-if="more" class="m-0 h-8 w-8 flex items-center justify-center border-0 bg-transparent p-0 after:border-0" aria-label="更多">
        <wd-icon name="more-vertical" size="21px" color="#5d5d5b" />
      </button>
      <button v-if="close" class="m-0 h-8 w-8 flex items-center justify-center border-0 bg-transparent p-0 after:border-0" aria-label="关闭" @click="goBack">
        <wd-icon name="close" size="21px" color="#1c1c1a" />
      </button>
    </view>
  </view>
</template>
