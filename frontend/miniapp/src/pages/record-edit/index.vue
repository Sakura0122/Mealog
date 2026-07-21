<script setup lang="ts">
definePage({
  name: 'record-edit',
  style: {
    navigationStyle: 'custom',
  },
})

const sourceType = ref<'self' | 'outside'>('self')
const showSuggestions = ref(true)
const recipeName = ref('')
const shopName = ref('')
const dishName = ref('')
const note = ref('')

const chooseSource = (type: 'self' | 'outside') => {
  sourceType.value = type
  showSuggestions.value = type === 'self'
}

const chooseRecipe = (name: string) => {
  recipeName.value = name
  showSuggestions.value = false
}

const saveRecord = () => {
  uni.navigateTo({ url: '/pages/record-detail/index' })
}
</script>

<template>
  <view class="min-h-screen bg-[#fcf9f6] pb-8">
    <AppTopBar close />

    <view class="mx-auto mt-6 w-[176px] rotate-[-1deg] bg-white p-2 pb-7 shadow-[0_4px_12px_rgba(0,0,0,0.08)]">
      <image src="/static/images/record-salad.jpg" mode="aspectFill" class="h-[176px] w-full" />
      <view class="mx-auto mt-2 h-1 w-12 rounded-full bg-[#dfddda]" />
    </view>

    <view class="mx-5 mt-3 overflow-visible border border-[#e5e2df] rounded-3xl bg-white shadow-[0_8px_20px_rgba(0,0,0,0.04)]">
      <button class="m-0 h-[57px] w-full flex items-center border-0 border-b border-[#ebe8e4] bg-transparent px-5 text-left after:border-0">
        <wd-icon name="calendar-line" size="19px" color="#5c6949" />
        <text class="ml-4 text-base text-[#1c1c1a]">
          6月14日 12:45 PM
        </text>
        <wd-icon name="arrow-right" size="15px" color="#c6c8c3" custom-class="ml-auto" />
      </button>

      <view class="h-[76px] flex items-center border-b border-[#ebe8e4] px-5">
        <wd-icon name="store" size="19px" color="#5c6949" />
        <view class="ml-4 flex rounded-full bg-[#f6f3f0] p-1">
          <button class="m-0 h-10 border-0 rounded-full px-5 text-base after:border-0" :class="sourceType === 'self' ? 'bg-white text-[#52634c] shadow-sm' : 'bg-transparent text-[#8f8f8a]'" @click="chooseSource('self')">
            自己做
          </button>
          <button class="m-0 h-10 border-0 rounded-full px-5 text-base after:border-0" :class="sourceType === 'outside' ? 'bg-white text-[#1c1c1a] shadow-sm' : 'bg-transparent text-[#8f8f8a]'" @click="chooseSource('outside')">
            外面买
          </button>
        </view>
      </view>

      <template v-if="sourceType === 'self'">
        <view class="relative">
          <view class="h-[57px] flex items-center border-b border-[#ebe8e4] px-5">
            <wd-icon name="book" size="18px" color="#5c6949" />
            <input v-model="recipeName" class="ml-4 min-w-0 flex-1 text-base text-[#1c1c1a]" placeholder="选择已有菜谱或直接输入新菜" placeholder-class="text-[#c7c7c1]" @focus="showSuggestions = true">
          </view>
          <view v-if="showSuggestions" class="absolute left-1 right-1 top-[56px] z-20 border border-[#d5d3ce] rounded-lg bg-white px-14 shadow-[0_8px_18px_rgba(0,0,0,0.12)]">
            <button class="m-0 h-[59px] w-full flex items-center border-0 border-b border-[#eceae6] bg-transparent p-0 text-left after:border-0" @click="chooseRecipe('暖阳牛油果')">
              <view>
                <view class="flex items-center gap-2">
                  <text class="text-sm text-[#1c1c1a] font-medium">
                    暖阳牛油果
                  </text>
                  <text class="rounded bg-[#d5e8cb] px-1.5 py-0.5 text-[10px] text-[#52634c]">
                    已完善
                  </text>
                </view>
                <text class="mt-1 block text-[10px] text-[#777973]">
                  做过 12 次
                </text>
              </view>
            </button>
            <button class="m-0 h-[59px] w-full flex items-center border-0 border-b border-[#eceae6] bg-transparent p-0 text-left after:border-0" @click="chooseRecipe('经典凯撒沙拉')">
              <view>
                <view class="flex items-center gap-2">
                  <text class="text-sm text-[#1c1c1a] font-medium">
                    经典凯撒沙拉
                  </text>
                  <text class="rounded bg-[#e7e5e2] px-1.5 py-0.5 text-[10px] text-[#666761]">
                    草稿
                  </text>
                </view>
                <text class="mt-1 block text-[10px] text-[#777973]">
                  做过 5 次
                </text>
              </view>
            </button>
            <button class="m-0 h-[59px] w-full flex items-center border-0 bg-transparent p-0 text-left after:border-0" @click="chooseRecipe('牛油果吐司')">
              <view>
                <view class="flex items-center gap-2">
                  <text class="text-sm text-[#1c1c1a] font-medium">
                    牛油果吐司
                  </text>
                  <text class="rounded bg-[#d5e8cb] px-1.5 py-0.5 text-[10px] text-[#52634c]">
                    已完善
                  </text>
                </view>
                <text class="mt-1 block text-[10px] text-[#777973]">
                  做过 28 次
                </text>
              </view>
            </button>
          </view>
        </view>
      </template>

      <template v-else>
        <view class="h-[57px] flex items-center border-b border-[#ebe8e4] px-5">
          <wd-icon name="store" size="19px" color="#5c6949" />
          <input v-model="shopName" class="ml-4 min-w-0 flex-1 text-base text-[#1c1c1a]" placeholder="选择店铺" placeholder-class="text-[#c7c7c1]">
        </view>
        <view class="h-[57px] flex items-center border-b border-[#ebe8e4] px-5">
          <wd-icon name="book" size="18px" color="#5c6949" />
          <input v-model="dishName" class="ml-4 min-w-0 flex-1 text-base text-[#1c1c1a]" placeholder="输入菜品名称" placeholder-class="text-[#c7c7c1]">
        </view>
      </template>

      <view class="min-h-[112px] flex items-start px-5 py-4">
        <wd-icon name="edit" size="18px" color="#5c6949" custom-class="mt-1" />
        <textarea v-model="note" class="ml-4 h-20 min-w-0 flex-1 text-base text-[#1c1c1a] leading-6" placeholder="个人备注..." placeholder-class="text-[#c7c7c1]" />
      </view>
    </view>

    <button class="mx-5 mt-7 h-14 flex items-center justify-center border-0 rounded-full bg-[#d5e8cb] text-sm text-[#101f0d] shadow-[0_5px_10px_rgba(80,100,72,0.14)] after:border-0" @click="saveRecord">
      保存
    </button>
  </view>
</template>
