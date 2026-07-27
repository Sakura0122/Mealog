<script setup lang="ts">
definePage({
  name: 'about',
  style: {
    navigationStyle: 'custom',
  },
})
</script>

<template>
  <view class="min-h-screen bg-[#f8fafc] pb-12">
    <AppTopBar />

    <view class="px-5">
      <view class="relative mt-5 h-56 overflow-hidden rounded-3xl">
        <image src="/static/images/home-matcha.jpg" mode="aspectFill" class="h-full w-full" />
        <view class="absolute inset-0 bg-[rgba(24,32,22,0.34)]" />
        <view class="absolute inset-x-0 bottom-0 p-6">
          <text class="block text-4xl text-white font-bold leading-10">
            Mealog
          </text>
          <text class="mt-2 block text-base text-white leading-6">
            好好吃饭，也记得每一餐。
          </text>
        </view>
      </view>

      <view class="mt-10">
        <text class="block text-xl text-[#20251e] font-semibold leading-8">
          一本属于你的饮食日记
        </text>
        <text class="mt-4 block text-[15px] text-[#565d54] leading-7">
          Mealog 希望用简单、安静的方式，帮你留下每一次认真吃饭的痕迹。时间久了，散落的照片、店铺和菜谱会连成一份只属于你的生活记录。
        </text>
      </view>

      <view class="mt-10 border-y border-[#e1e5df]">
        <view class="min-h-20 flex items-center border-b border-[#e1e5df] py-4">
          <view class="h-10 w-10 flex shrink-0 items-center justify-center rounded-full bg-[#e5f0df]">
            <wd-icon name="calendar-line" size="21px" color="#52634c" />
          </view>
          <view class="ml-4 min-w-0 flex-1">
            <text class="block text-base text-[#20251e] font-medium leading-6">
              留住日常
            </text>
            <text class="mt-1 block text-sm text-[#737a70] leading-5">
              从日历里回看每天吃过的味道
            </text>
          </view>
        </view>
        <view class="min-h-20 flex items-center border-b border-[#e1e5df] py-4">
          <view class="h-10 w-10 flex shrink-0 items-center justify-center rounded-full bg-[#eef0e8]">
            <wd-icon name="book" size="21px" color="#59604f" />
          </view>
          <view class="ml-4 min-w-0 flex-1">
            <text class="block text-base text-[#20251e] font-medium leading-6">
              收好灵感
            </text>
            <text class="mt-1 block text-sm text-[#737a70] leading-5">
              把做过的菜整理成自己的菜谱
            </text>
          </view>
        </view>
        <view class="min-h-20 flex items-center py-4">
          <view class="h-10 w-10 flex shrink-0 items-center justify-center rounded-full bg-[#f2ece5]">
            <wd-icon name="heart" size="21px" color="#7a5c4f" />
          </view>
          <view class="ml-4 min-w-0 flex-1">
            <text class="block text-base text-[#20251e] font-medium leading-6">
              认真生活
            </text>
            <text class="mt-1 block text-sm text-[#737a70] leading-5">
              在一餐一饭里看见生活的节奏
            </text>
          </view>
        </view>
      </view>

      <view class="mt-10 flex items-center justify-between border-b border-[#e1e5df] pb-5">
        <text class="text-sm text-[#737a70]">
          当前版本
        </text>
        <text class="text-sm text-[#30352f] font-medium">
          1.0.0
        </text>
      </view>

      <text class="mt-10 block text-center text-xs text-[#9ba097] leading-5">
        Made for everyday meals
      </text>
    </view>
  </view>
</template>
