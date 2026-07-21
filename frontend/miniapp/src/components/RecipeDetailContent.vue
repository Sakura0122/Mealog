<script setup lang="ts">
const props = defineProps<{
  shared?: boolean
}>()

const recipeSteps = [
  '1.挖牛油果',
  '2.煎三文鱼或空气炸锅',
  '3.蔬菜烫熟炒制',
  '4.加入酱油芥末搅拌',
]

const handleAction = () => {
  if (!props.shared)
    uni.navigateTo({ url: '/pages/recipe-share/index' })
}
</script>

<template>
  <view class="min-h-screen bg-[#fcf9f6] pb-8">
    <AppTopBar :show-back="!shared" close />

    <view class="mx-auto mt-3 w-[280px] rotate-1 bg-white p-3 pb-8 shadow-[0_5px_12px_rgba(0,0,0,0.12)]">
      <image src="/static/images/recipe-soup.jpg" mode="aspectFill" class="h-[256px] w-full" />
      <text class="mx-auto mt-4 block w-max bg-[#dbe4d5] px-4 py-1 text-[10px] text-[#475244] shadow-sm">
        菜谱时刻
      </text>
    </view>

    <view class="mx-5 mt-6 overflow-hidden border border-[#e5e2df] rounded-3xl bg-white shadow-[0_8px_18px_rgba(0,0,0,0.06)]">
      <view class="h-[57px] flex items-center border-b border-[#ebe8e4] px-5">
        <wd-icon name="book" size="18px" color="#5c6949" />
        <text class="ml-4 text-base text-[#52634c] font-medium">
          三文鱼能量碗
        </text>
      </view>
      <view class="min-h-[52px] flex items-center border-b border-[#ebe8e4] px-5 py-3">
        <wd-icon name="list" size="18px" color="#777a77" />
        <view class="ml-3 flex flex-1 flex-wrap gap-1">
          <text v-for="item in ['三文鱼', '羽衣甘蓝', '彩椒', '牛油果', '鸡蛋', '菌菇']" :key="item" class="rounded-full bg-[#e1e6c2] px-1.5 py-1 text-[10px] text-[#59624d]">
            {{ item }}
          </text>
        </view>
      </view>
      <view class="min-h-[112px] flex items-start px-5 py-4">
        <wd-icon name="file" size="18px" color="#777a77" custom-class="mt-1" />
        <view class="ml-3 flex-1">
          <text v-for="step in recipeSteps" :key="step" class="block text-sm text-[#4e5848] leading-5">
            {{ step }}
          </text>
        </view>
      </view>
    </view>

    <button class="mx-5 mt-6 h-14 flex items-center justify-center border-0 rounded-full text-base font-medium shadow-[0_6px_12px_rgba(0,0,0,0.1)] after:border-0" :class="shared ? 'bg-[#d5e8cb] text-[#24331f]' : 'bg-[#ffd29a] text-[#343021]'" @click="handleAction">
      {{ shared ? '保存至我的菜谱' : '分享我的菜谱' }}
    </button>
  </view>
</template>
