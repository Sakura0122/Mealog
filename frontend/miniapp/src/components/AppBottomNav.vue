<script setup lang="ts">
defineProps<{
  active: 'home' | 'profile'
}>()

const switchPage = (page: 'home' | 'profile') => {
  const url = page === 'home' ? '/pages/index/index' : '/pages/profile/index'
  uni.redirectTo({ url })
}
</script>

<template>
  <view class="fixed bottom-[calc(env(safe-area-inset-bottom)+21px)] left-1/2 z-30 h-16 w-[280px] flex items-center justify-around rounded-full bg-[#f6f3f0]/90 shadow-[0_4px_16px_rgba(0,0,0,0.06)] backdrop-blur-md -translate-x-1/2">
    <button
      class="m-0 h-12 w-12 flex items-center justify-center border-0 rounded-full p-0 after:border-0"
      :class="active === 'home' ? 'bg-[#d5e8cb]' : 'bg-transparent'"
      aria-label="饮食日历"
      @click="switchPage('home')"
    >
      <wd-icon name="calendar-line" size="21px" color="#1c2919" />
    </button>
    <button
      class="m-0 h-12 w-12 flex items-center justify-center border-0 rounded-full p-0 after:border-0"
      :class="active === 'profile' ? 'bg-[#d5e8cb]' : 'bg-transparent'"
      aria-label="我的"
      @click="switchPage('profile')"
    >
      <wd-icon name="user" size="20px" color="#1c2919" />
    </button>
  </view>
</template>
