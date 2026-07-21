<script setup lang="ts">
definePage({
  name: 'record-detail',
  style: {
    navigationStyle: 'custom',
  },
})

const editRecord = () => {
  uni.navigateTo({ url: '/pages/record-edit/index' })
}

const goBack = () => {
  uni.navigateBack()
}
</script>

<template>
  <view class="min-h-screen bg-[#fcf9f6] pb-8">
    <view class="h-16 flex items-center px-5">
      <button class="m-0 h-8 w-8 flex items-center justify-center border-0 bg-transparent p-0 after:border-0" aria-label="返回" @click="goBack">
        <wd-icon name="arrow-left" size="22px" color="#1c1c1a" />
      </button>
      <button class="ml-auto mr-3 h-8 w-8 flex items-center justify-center border-0 bg-transparent p-0 after:border-0" aria-label="编辑" @click="editRecord">
        <wd-icon name="edit" size="21px" color="#1c1c1a" />
      </button>
      <button class="m-0 h-8 w-8 flex items-center justify-center border-0 bg-transparent p-0 after:border-0" aria-label="更多">
        <wd-icon name="more-vertical" size="21px" color="#5d5d5b" />
      </button>
    </view>

    <view class="mx-auto mt-10 w-[176px] rotate-[-1deg] bg-white p-2 pb-7 shadow-[0_4px_12px_rgba(0,0,0,0.08)]">
      <image src="/static/images/record-salad.jpg" mode="aspectFill" class="h-[176px] w-full" />
      <view class="mx-auto mt-2 h-1 w-12 rounded-full bg-[#dfddda]" />
    </view>

    <view class="mx-5 mt-4 overflow-hidden border border-[#e5e2df] rounded-3xl bg-white shadow-[0_8px_20px_rgba(0,0,0,0.04)]">
      <view class="h-[57px] flex items-center border-b border-[#ebe8e4] px-5">
        <wd-icon name="calendar-line" size="19px" color="#5c6949" />
        <text class="ml-4 text-base text-[#1c1c1a]">
          6月14日 12:45 PM
        </text>
        <wd-icon name="arrow-right" size="15px" color="#c6c8c3" custom-class="ml-auto" />
      </view>
      <view class="h-[76px] flex items-center border-b border-[#ebe8e4] px-5">
        <wd-icon name="store" size="19px" color="#5c6949" />
        <view class="ml-4 flex rounded-full bg-[#f6f3f0] p-1">
          <text class="rounded-full bg-white px-5 py-2 text-base text-[#52634c] shadow-sm">
            自己做
          </text>
          <text class="px-5 py-2 text-base text-[#8f8f8a]">
            外面买
          </text>
        </view>
      </view>
      <view class="h-[57px] flex items-center border-b border-[#ebe8e4] bg-[#fbfcf8] px-5">
        <wd-icon name="book" size="18px" color="#5c6949" />
        <text class="ml-4 text-base text-[#52634c]">
          暖阳牛油果
        </text>
        <text class="ml-2 rounded bg-[#d5e8cb] px-2 py-1 text-[10px] text-[#52634c]">
          已完善
        </text>
        <wd-icon name="check-circle" size="18px" color="#687454" custom-class="ml-auto" />
      </view>
      <view class="min-h-[112px] flex items-start px-5 py-4">
        <wd-icon name="edit" size="18px" color="#5c6949" custom-class="mt-1" />
        <text class="ml-4 text-base text-[#c7c7c1] leading-6">
          个人备注...
        </text>
      </view>
    </view>

    <button class="mx-5 mt-20 h-14 flex items-center justify-center border-0 rounded-full bg-[#d5e8cb] text-sm text-[#101f0d] shadow-[0_5px_10px_rgba(80,100,72,0.14)] after:border-0" @click="editRecord">
      保存
    </button>
  </view>
</template>
