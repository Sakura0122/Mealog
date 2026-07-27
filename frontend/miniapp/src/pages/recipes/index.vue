<script setup lang="ts">
import type { RecipeListItem, RecipeStatus } from '@/api/recipes/type'
import { recipeApi } from '@/api/recipes'
import { getErrorMessage } from '@/utils/request'

definePage({
  name: 'recipes',
  style: {
    navigationStyle: 'custom',
  },
})

const filters: { label: string, status?: RecipeStatus }[] = [
  { label: '全部' },
  { label: '草稿', status: 'DRAFT' },
  { label: '已完善', status: 'COMPLETED' },
]
const activeStatus = ref<RecipeStatus>()

const keyword = ref('')
const recipes = ref<RecipeListItem[]>([])
const currentPage = ref(1)
const pageCount = ref(0)
const loading = ref(false)
const loadError = ref('')
let requestSequence = 0

const loadRecipes = async (reset = false) => {
  if (loading.value && !reset)
    return

  const targetPage = reset ? 1 : currentPage.value + 1
  const sequence = ++requestSequence
  if (reset) {
    recipes.value = []
    currentPage.value = 1
    pageCount.value = 0
  }
  loading.value = true
  loadError.value = ''
  try {
    const page = await recipeApi.list({
      current_page: targetPage,
      page_size: 20,
      keyword: keyword.value.trim() || undefined,
      status: activeStatus.value,
    })
    // 搜索条件快速变化时，只接收最后一次请求的结果。
    if (sequence !== requestSequence)
      return
    recipes.value = reset ? page.list : [...recipes.value, ...page.list]
    currentPage.value = targetPage
    pageCount.value = page.page_count
  }
  catch (error) {
    if (sequence === requestSequence)
      loadError.value = getErrorMessage(error)
  }
  finally {
    if (sequence === requestSequence)
      loading.value = false
  }
}

let searchTimer: ReturnType<typeof setTimeout> | undefined
watch(keyword, () => {
  if (searchTimer)
    clearTimeout(searchTimer)
  searchTimer = setTimeout(() => loadRecipes(true), 300)
})
onUnmounted(() => {
  if (searchTimer)
    clearTimeout(searchTimer)
})

const chooseFilter = (status?: RecipeStatus) => {
  if (activeStatus.value === status)
    return
  activeStatus.value = status
  loadRecipes(true)
}

const loadMore = () => {
  if (!loading.value && currentPage.value < pageCount.value)
    loadRecipes()
}

onShow(() => loadRecipes(true))
onReachBottom(loadMore)

const openRecipe = (recipeId: string) => {
  uni.navigateTo({ url: `/pages/recipe-detail/index?id=${recipeId}` })
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
        <input v-model="keyword" class="ml-3 min-w-0 flex-1 text-sm text-[#1c1c1a]" placeholder="搜索菜谱..." placeholder-class="text-[#777b76]">
      </view>

      <view class="mt-6 flex gap-3">
        <button
          v-for="filter in filters"
          :key="filter.label"
          class="m-0 h-8 flex items-center justify-center border-0 rounded-full px-6 text-xs after:border-0"
          :class="activeStatus === filter.status ? 'bg-[#8ca486] text-white' : 'bg-[#e7e5e2] text-[#454844]'"
          @click="chooseFilter(filter.status)"
        >
          {{ filter.label }}
        </button>
      </view>

      <view v-if="loading && recipes.length === 0" class="h-64 flex items-center justify-center">
        <wd-loading text="加载菜谱中" color="#71836b" />
      </view>

      <view v-else-if="loadError && recipes.length === 0" class="py-16 text-center">
        <wd-empty icon="warning" :tip="loadError" />
        <button class="mx-auto mt-4 border-0 rounded-full bg-[#d5e8cb] px-6 py-2 text-sm text-[#24331f] after:border-0" @click="loadRecipes(true)">
          重新加载
        </button>
      </view>

      <wd-empty v-else-if="recipes.length === 0" custom-class="mt-16" icon="book" tip="还没有符合条件的菜谱" />

      <template v-else>
        <view class="grid grid-cols-2 mt-6 items-start gap-x-5 gap-y-4">
          <button
            v-for="recipe in recipes"
            :key="recipe.id"
            class="m-0 w-full overflow-hidden border-0 rounded-lg bg-white p-2 pb-3 text-left shadow-[0_8px_20px_rgba(0,0,0,0.05)] after:border-0"
            @click="openRecipe(recipe.id)"
          >
            <view class="relative h-[150px] overflow-hidden rounded-md bg-[#e7e5e2]">
              <image v-if="recipe.cover_url" :src="recipe.cover_url" mode="aspectFill" class="h-full w-full" />
              <view v-else class="h-full flex flex-col items-center justify-center text-[#4f574d]">
                <wd-icon name="book" size="42px" color="#4f574d" />
                <text class="mt-2 text-[10px]">
                  暂无封面
                </text>
              </view>
              <text class="absolute right-1 top-1 rounded-full px-2 py-1 text-[10px] text-white" :class="recipe.status === 'COMPLETED' ? 'bg-[#71836b]' : 'bg-[#7d6847]'">
                {{ recipe.status === 'COMPLETED' ? '已完善' : '草稿' }}
              </text>
            </view>
            <text class="mt-2 block truncate text-sm text-[#1c1c1a] font-medium leading-5">
              {{ recipe.name }}
            </text>
            <view class="mt-1 flex items-center text-[10px] text-[#4d514c]">
              <wd-icon name="list" size="12px" color="#4d514c" />
              <text class="ml-1">
                做过 {{ recipe.usage_count }} 次
              </text>
            </view>
          </button>
        </view>

        <wd-loadmore
          v-if="loading || loadError || currentPage >= pageCount"
          :state="loading ? 'loading' : loadError ? 'error' : 'finished'"
          loading-text="加载更多菜谱"
          error-text="加载失败"
          finished-text="没有更多菜谱了"
          custom-class="mt-5"
          @reload="loadMore"
        />
      </template>
    </view>

    <button class="fixed bottom-[calc(env(safe-area-inset-bottom)+110px)] right-8 z-20 h-14 w-14 flex items-center justify-center border-0 rounded-full bg-[#e1e6c2] p-0 shadow-[0_6px_16px_rgba(0,0,0,0.12)] after:border-0" aria-label="新增菜谱" @click="createRecipe">
      <wd-icon name="plus" size="28px" color="#1c2919" />
    </button>

    <AppBottomNav active="profile" />
  </view>
</template>
