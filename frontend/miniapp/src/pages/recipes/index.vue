<script setup lang="ts">
definePage({
  name: 'recipes',
  style: {
    navigationStyle: 'custom',
  },
})

const keyword = ref('')
const activeFilter = ref<'全部' | '草稿' | '已完善'>('全部')

const filters = ['全部', '草稿', '已完善'] as const

const recipes = [
  { name: '暖阳牛油果', count: 12, status: '已完善', image: '/static/images/recipe-avocado.jpg' },
  { name: '雨日浓汤', count: 0, status: '草稿', image: '/static/images/recipe-soup.jpg' },
  { name: '丰收能量碗', count: 8, status: '已完善', image: '/static/images/recipe-bowl.jpg' },
  { name: '莓果酸奶杯', count: 24, status: '已完善', image: '/static/images/recipe-yogurt.jpg' },
  { name: '秘制意面酱', count: 0, status: '草稿', image: '' },
]

const isVisible = (recipe: typeof recipes[number]) => {
  const matchesFilter = activeFilter.value === '全部' || recipe.status === activeFilter.value
  const matchesKeyword = !keyword.value || recipe.name.includes(keyword.value)
  return matchesFilter && matchesKeyword
}

const openRecipe = () => {
  uni.navigateTo({ url: '/pages/recipe-detail/index' })
}

const createRecipe = () => {
  uni.navigateTo({ url: '/pages/recipe-create/index' })
}
</script>

<template>
  <view class="min-h-screen bg-[#fcf9f6] pb-32">
    <AppTopBar />

    <view class="px-5">
      <view class="h-12 flex items-center rounded-full bg-white px-4 shadow-[0_4px_15px_rgba(0,0,0,0.03)]">
        <wd-icon name="search-line" size="21px" color="#3f4640" />
        <input v-model="keyword" class="ml-3 min-w-0 flex-1 text-sm text-[#1c1c1a]" placeholder="搜索记忆..." placeholder-class="text-[#777b76]">
      </view>

      <view class="mt-6 flex gap-3">
        <button
          v-for="filter in filters"
          :key="filter"
          class="m-0 h-8 border-0 rounded-full px-6 text-xs after:border-0"
          :class="activeFilter === filter ? 'bg-[#8ca486] text-white' : 'bg-[#e7e5e2] text-[#454844]'"
          @click="activeFilter = filter"
        >
          {{ filter }}
        </button>
      </view>

      <view class="grid grid-cols-2 mt-6 items-start gap-x-5 gap-y-4">
        <button
          v-for="recipe in recipes"
          v-show="isVisible(recipe)"
          :key="recipe.name"
          class="m-0 w-full overflow-hidden border-0 rounded-lg bg-white p-2 pb-3 text-left shadow-[0_8px_20px_rgba(0,0,0,0.05)] after:border-0"
          @click="openRecipe"
        >
          <view class="relative h-[150px] overflow-hidden rounded-md bg-[#e7e5e2]">
            <image v-if="recipe.image" :src="recipe.image" mode="aspectFill" class="h-full w-full" />
            <view v-else class="h-full flex flex-col items-center justify-center text-[#4f574d]">
              <wd-icon name="book" size="42px" color="#4f574d" />
              <text class="mt-2 text-[10px]">
                点击添加封面
              </text>
            </view>
            <text class="absolute right-1 top-1 rounded-full px-2 py-1 text-[10px] text-white" :class="recipe.status === '已完善' ? 'bg-[#71836b]' : 'bg-[#7d6847]'">
              {{ recipe.status }}
            </text>
          </view>
          <text class="mt-2 block truncate text-sm text-[#1c1c1a] font-medium leading-5">
            {{ recipe.name }}
          </text>
          <view class="mt-1 flex items-center text-[10px] text-[#4d514c]">
            <wd-icon name="list" size="12px" color="#4d514c" />
            <text class="ml-1">
              做过 {{ recipe.count }} 次
            </text>
          </view>
        </button>
      </view>
    </view>

    <button class="fixed bottom-[calc(env(safe-area-inset-bottom)+110px)] right-8 z-20 h-14 w-14 flex items-center justify-center border-0 rounded-full bg-[#e1e6c2] p-0 shadow-[0_6px_16px_rgba(0,0,0,0.12)] after:border-0" aria-label="新增菜谱" @click="createRecipe">
      <wd-icon name="plus" size="28px" color="#1c2919" />
    </button>

    <AppBottomNav active="profile" />
  </view>
</template>
