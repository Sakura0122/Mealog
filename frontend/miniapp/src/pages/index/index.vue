<script setup lang="ts">
definePage({
  name: 'home',
  style: {
    navigationStyle: 'custom',
  },
})

const showSourcePicker = ref(false)

const calendarDays = [
  null,
  1,
  2,
  3,
  4,
  5,
  6,
  7,
  8,
  9,
  'photo',
  11,
  12,
  13,
  14,
  15,
  16,
  17,
  18,
  19,
  20,
  21,
  22,
  23,
  24,
  25,
  26,
  27,
  28,
  29,
  30,
]

const openRecordEditor = () => {
  showSourcePicker.value = false
  uni.navigateTo({ url: '/pages/record-edit/index' })
}

const openRecordDetail = () => {
  uni.navigateTo({ url: '/pages/record-detail/index' })
}
</script>

<template>
  <view class="min-h-screen bg-[#f8fafc] pb-32">
    <view class="h-20 flex items-center justify-between bg-[#fcf9f6]/80 px-5 backdrop-blur-sm">
      <text class="text-[28px] text-[#52634c] font-bold leading-7">
        Mealog
      </text>
      <view class="h-10 w-10 flex items-center justify-center border-2 border-[#e5e2df] rounded-full bg-[#e1e6c2] text-base text-[#1a1d07] font-semibold">
        M
      </view>
    </view>

    <view class="mx-auto max-w-[448px] flex flex-col gap-[11px] px-5 pt-4">
      <view class="flex flex-col gap-4 rounded-[32px] bg-white px-6 pb-6 pt-[10px] shadow-[0_4px_20px_rgba(0,0,0,0.03)]">
        <text class="text-center text-base text-[#1c1c1a] leading-6">
          2026年6月
        </text>
        <view class="grid grid-cols-7 pt-2 text-center text-xs text-[#c4c8be] leading-4">
          <text v-for="week in ['周日', '周一', '周二', '周三', '周四', '周五', '周六']" :key="week">
            {{ week }}
          </text>
        </view>
        <view class="grid grid-cols-7 gap-2">
          <view v-for="(day, index) in calendarDays" :key="index" class="aspect-[0.76] min-w-0">
            <view v-if="day === 'photo'" class="h-full overflow-hidden rounded-xl shadow-[2px_4px_8px_rgba(82,99,76,0.12)]">
              <image src="/static/images/home-latte.jpg" mode="aspectFill" class="h-full w-full" />
            </view>
            <view v-else-if="day" class="h-full flex items-center justify-center rounded-xl bg-[#f6f3f0] text-base text-[#444841]">
              {{ day }}
            </view>
          </view>
        </view>
        <view class="grid grid-cols-[1fr_1px_1fr] items-center border-t border-[#c4c8be]/20 pt-4 text-center">
          <view class="flex flex-col gap-1">
            <text class="text-[10px] text-[#c4c8be] leading-[14px]">
              本月记录
            </text>
            <text class="text-xl text-[#52634c] font-semibold leading-7">
              18
            </text>
          </view>
          <view class="h-8 bg-[#c4c8be]/20" />
          <view class="flex flex-col gap-1">
            <text class="text-[10px] text-[#c4c8be] leading-[14px]">
              记录天数
            </text>
            <text class="text-xl text-[#52634c] font-semibold leading-7">
              9
            </text>
          </view>
        </view>
      </view>

      <button class="m-0 h-12 w-full flex items-center justify-center border-0 rounded-full bg-[#d5e8cb] p-0 text-xs text-[#101f0d] font-medium after:border-0" @click="showSourcePicker = true">
        新增记录
      </button>

      <view class="flex flex-col gap-1.5 pt-1">
        <text class="px-2 text-xs text-[#c4c8be] leading-4">
          今日记录
        </text>
        <view class="flex flex-col gap-4">
          <button class="m-0 h-24 w-full flex items-center border-0 rounded-3xl bg-white px-4 py-[14px] text-left shadow-[0_10px_25px_-5px_rgba(82,99,76,0.08)] after:border-0" @click="openRecordDetail">
            <view class="w-[55px] flex shrink-0 flex-col items-center border-r border-[#c4c8be]/30 pr-4">
              <text class="text-[10px] text-[#c4c8be] leading-[14px]">
                上午
              </text>
              <text class="text-sm text-[#1c1c1a] font-semibold leading-5">
                09:30
              </text>
            </view>
            <view class="min-w-0 flex-1 pl-4">
              <text class="block text-base text-[#1c1c1a] font-medium leading-6">
                冰拿铁
              </text>
              <text class="block text-sm text-[#444841] leading-5">
                开启清爽的一天，少冰无糖。
              </text>
            </view>
            <view class="ml-3 h-16 w-16 shrink-0 rotate-3 overflow-hidden border-2 border-white rounded-xl shadow-[2px_4px_8px_rgba(82,99,76,0.12)]">
              <image src="/static/images/home-latte.jpg" mode="aspectFill" class="h-full w-full" />
            </view>
          </button>

          <button class="m-0 h-24 w-full flex items-center border-0 rounded-3xl bg-white px-4 py-[14px] text-left shadow-[0_10px_25px_-5px_rgba(82,99,76,0.08)] after:border-0" @click="openRecordDetail">
            <view class="w-[55px] flex shrink-0 flex-col items-center border-r border-[#c4c8be]/30 pr-4">
              <text class="text-[10px] text-[#c4c8be] leading-[14px]">
                下午
              </text>
              <text class="text-sm text-[#1c1c1a] font-semibold leading-5">
                14:20
              </text>
            </view>
            <view class="min-w-0 flex-1 pl-4">
              <text class="block text-base text-[#1c1c1a] font-medium leading-6">
                抹茶拿铁
              </text>
              <text class="block text-sm text-[#444841] leading-5">
                午后的小憩，口感醇厚。
              </text>
            </view>
            <view class="ml-3 h-16 w-16 shrink-0 overflow-hidden border-2 border-white rounded-xl shadow-[2px_4px_8px_rgba(82,99,76,0.12)] -rotate-3">
              <image src="/static/images/home-matcha.jpg" mode="aspectFill" class="h-full w-full" />
            </view>
          </button>
        </view>
      </view>
    </view>

    <AppBottomNav active="home" />

    <wd-popup v-model="showSourcePicker" position="bottom" :z-index="50" root-portal custom-style="background: transparent; padding: 0 24px calc(env(safe-area-inset-bottom) + 60px);">
      <view class="flex flex-col gap-4 pb-16">
        <button class="m-0 h-[114px] w-full flex items-center border-0 rounded-3xl bg-white px-6 text-left shadow-[0_12px_25px_rgba(0,0,0,0.12)] after:border-0" @click="openRecordEditor">
          <view class="mr-6 h-16 w-16 flex items-center justify-center rounded-2xl bg-[#e1e6c2]">
            <wd-icon name="camera" size="30px" color="#5f6848" />
          </view>
          <text class="text-xl text-[#1c1c1a]">
            拍照
          </text>
        </button>
        <button class="m-0 h-[114px] w-full flex items-center border-0 rounded-3xl bg-white px-6 text-left shadow-[0_12px_25px_rgba(0,0,0,0.12)] after:border-0" @click="openRecordEditor">
          <view class="mr-6 h-16 w-16 flex items-center justify-center rounded-2xl bg-[#ffd29a]">
            <wd-icon name="image" size="30px" color="#6d5d6e" />
          </view>
          <text class="text-xl text-[#1c1c1a]">
            从相册选择
          </text>
        </button>
        <button class="mx-auto mt-4 h-14 w-14 flex items-center justify-center border-0 rounded-full bg-[#1c1c1a] p-0 after:border-0" aria-label="关闭" @click="showSourcePicker = false">
          <wd-icon name="close" size="24px" color="#ffffff" />
        </button>
      </view>
    </wd-popup>
  </view>
</template>
