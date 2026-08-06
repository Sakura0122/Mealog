<script setup lang="ts">
import type { RecipeDetail } from '@/api/recipes/type'
import { recipeApi } from '@/api/recipes'
import { getErrorMessage } from '@/utils/request'

definePage({
  name: 'recipe-detail',
  style: {
    navigationStyle: 'custom',
  },
})

const recipeId = ref('')
const loadError = ref('')
onLoad((options) => {
  recipeId.value = typeof options?.id === 'string' ? options.id : ''
  if (!recipeId.value)
    loadError.value = '缺少菜谱 ID'
})

const recipe = ref<RecipeDetail>()
const loading = ref(false)
const loadRecipe = async () => {
  if (!recipeId.value)
    return

  loading.value = true
  loadError.value = ''
  try {
    recipe.value = await recipeApi.detail(recipeId.value)
  }
  catch (error) {
    loadError.value = getErrorMessage(error)
  }
  finally {
    loading.value = false
  }
}
onShow(loadRecipe)

const editRecipe = () => {
  uni.navigateTo({ url: `/pages/recipe-create/index?id=${recipeId.value}` })
}

const deleting = ref(false)
const removeRecipe = async () => {
  deleting.value = true
  try {
    await recipeApi.remove(recipeId.value)
    uni.navigateBack({
      success: () => useGlobalToast().success('菜谱已删除'),
    })
  }
  catch (error) {
    useGlobalToast().error(getErrorMessage(error))
  }
  finally {
    deleting.value = false
  }
}

const confirmDelete = () => {
  useGlobalDialog().confirm({
    title: '删除菜谱',
    msg: '删除后无法在菜谱列表中恢复，确认删除吗？',
    confirmButtonText: '删除',
    // 删除属于不可恢复操作，使用组件库危险按钮样式强化提示。
    confirmButtonProps: { type: 'danger' },
    cancelButtonText: '取消',
    success: (result) => {
      if (result.action === 'confirm')
        removeRecipe()
    },
  })
}

onShareAppMessage(async () => {
  try {
    await recipeApi.share(recipeId.value)
  }
  catch (error) {
    useGlobalToast().error(getErrorMessage(error))
    throw error
  }

  // 微信会等待 Promise 完成，确保接收方打开链接前分享有效期已经生成。
  return {
    title: recipe.value ? `${recipe.value.name} - Mealog 菜谱` : 'Mealog 菜谱',
    path: `/pages/recipe-share/index?id=${recipeId.value}`,
    imageUrl: recipe.value?.cover_url ?? undefined,
  }
})
</script>

<template>
  <view v-if="loading && !recipe" class="min-h-screen bg-[#fcf9f6]">
    <AppTopBar />
    <view class="h-96 flex items-center justify-center">
      <wd-loading text="加载菜谱中" color="#71836b" />
    </view>
  </view>

  <view v-else-if="loadError && !recipe" class="min-h-screen bg-[#fcf9f6]">
    <AppTopBar />
    <view class="py-20 text-center">
      <wd-empty icon="warning" :tip="loadError" />
      <button v-if="recipeId" class="mx-auto mt-4 border-0 rounded-full bg-[#d5e8cb] px-6 py-2 text-sm text-[#24331f] after:border-0" @click="loadRecipe">
        重新加载
      </button>
    </view>
  </view>

  <template v-else-if="recipe">
    <RecipeDetailContent :recipe="recipe" action-open-type="share" @edit="editRecipe">
      <button :disabled="deleting" class="mx-auto mt-4 block border-0 bg-transparent p-0 text-sm text-[#8f8f8a] after:border-0 disabled:opacity-60" @click="confirmDelete">
        {{ deleting ? '删除中' : '删除菜谱' }}
      </button>
    </RecipeDetailContent>
  </template>
</template>
