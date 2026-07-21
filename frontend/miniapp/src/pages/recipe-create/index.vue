<script setup lang="ts">
definePage({
  name: 'recipe-create',
  style: {
    navigationStyle: 'custom',
  },
})

const recipeName = ref('')
const ingredients = ref('')
const steps = ref('')

const saveRecipe = () => {
  uni.navigateBack()
}
</script>

<template>
  <view class="min-h-screen bg-[#fcf9f6] pb-8">
    <AppTopBar close />

    <button class="mx-auto mt-3 block w-[280px] rotate-1 border-0 bg-white p-3 pb-8 shadow-[0_5px_12px_rgba(0,0,0,0.12)] after:border-0">
      <view class="h-[250px] w-full flex flex-col items-center justify-center bg-[#e5e3e0] text-[#4f5650]">
        <wd-icon name="camera" size="38px" color="#4f5650" />
        <text class="mt-2 text-sm">
          添加封面图
        </text>
      </view>
      <text class="mx-auto mt-4 block w-max bg-[#dbe4d5] px-4 py-1 text-[10px] text-[#475244] shadow-sm">
        菜谱时刻
      </text>
    </button>

    <view class="mx-5 mt-6 overflow-hidden border border-[#e5e2df] rounded-3xl bg-white shadow-[0_8px_18px_rgba(0,0,0,0.06)]">
      <view class="h-[57px] flex items-center border-b border-[#ebe8e4] px-5">
        <wd-icon name="book" size="18px" color="#5c6949" />
        <input v-model="recipeName" class="ml-4 min-w-0 flex-1 text-base text-[#1c1c1a]" placeholder="菜名" placeholder-class="text-[#c7c7c1]">
      </view>
      <view class="min-h-[57px] flex items-start border-b border-[#ebe8e4] px-5 py-4">
        <wd-icon name="list" size="18px" color="#777a77" custom-class="mt-1" />
        <textarea v-model="ingredients" class="ml-4 h-12 min-w-0 flex-1 text-base text-[#1c1c1a] leading-6" placeholder="食材，录入一种食材后按回车键继续录入" placeholder-class="text-[#c7c7c1]" />
      </view>
      <view class="min-h-[112px] flex items-start px-5 py-4">
        <wd-icon name="file" size="18px" color="#777a77" custom-class="mt-1" />
        <textarea v-model="steps" class="ml-4 h-20 min-w-0 flex-1 text-base text-[#1c1c1a] leading-6" placeholder="制作步骤" placeholder-class="text-[#c7c7c1]" />
      </view>
    </view>

    <button class="mx-5 mt-6 h-14 flex items-center justify-center border-0 rounded-full bg-[#d5e8cb] text-base text-[#24331f] font-medium shadow-[0_6px_12px_rgba(0,0,0,0.1)] after:border-0" @click="saveRecipe">
      保存菜谱
    </button>
  </view>
</template>
