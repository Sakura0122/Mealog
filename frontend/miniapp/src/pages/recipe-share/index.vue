<script setup lang="ts">
import type { RecipeShareDetail } from '@/api/recipes/type'
import { recipeApi } from '@/api/recipes'
import { getErrorMessage } from '@/utils/request'

definePage({
  name: 'recipe-share',
  style: {
    navigationStyle: 'custom',
  },
})

const recipeId = ref('')
const ownerPreview = ref(false)
const loadError = ref('')
onLoad((options) => {
  recipeId.value = typeof options?.id === 'string' ? options.id : ''
  ownerPreview.value = options?.owner === '1'
  if (!recipeId.value)
    loadError.value = '缺少分享菜谱 ID'
})

const recipe = ref<RecipeShareDetail>()
const loading = ref(false)
const loadRecipe = async () => {
  if (!recipeId.value)
    return

  loading.value = true
  loadError.value = ''
  try {
    recipe.value = await recipeApi.sharedDetail(recipeId.value)
  }
  catch (error) {
    loadError.value = getErrorMessage(error)
  }
  finally {
    loading.value = false
  }
}
onShow(loadRecipe)

const saving = ref(false)
const saveRecipe = async () => {
  if (ownerPreview.value || saving.value)
    return

  saving.value = true
  try {
    const savedRecipe = await recipeApi.saveShared(recipeId.value)
    uni.redirectTo({
      url: `/pages/recipe-detail/index?id=${savedRecipe.id}`,
      success: () => useGlobalToast().success('已保存至我的菜谱'),
    })
  }
  catch (error) {
    useGlobalToast().error(getErrorMessage(error))
  }
  finally {
    saving.value = false
  }
}

// 分享路径不携带预览标记，接收方打开后进入可保存状态。
onShareAppMessage(() => ({
  title: recipe.value ? `${recipe.value.name} - Mealog 菜谱` : 'Mealog 菜谱',
  path: `/pages/recipe-share/index?id=${recipeId.value}`,
  imageUrl: recipe.value?.cover_url ?? undefined,
}))
</script>

<template>
  <view v-if="loading && !recipe" class="min-h-screen bg-[#fcf9f6]">
    <AppTopBar close :show-back="false" />
    <view class="h-96 flex items-center justify-center">
      <wd-loading text="加载分享菜谱中" color="#71836b" />
    </view>
  </view>

  <view v-else-if="loadError && !recipe" class="min-h-screen bg-[#fcf9f6]">
    <AppTopBar close :show-back="false" />
    <view class="py-20 text-center">
      <wd-empty icon="warning" :tip="loadError" />
      <button v-if="recipeId" class="mx-auto mt-4 border-0 rounded-full bg-[#d5e8cb] px-6 py-2 text-sm text-[#24331f] after:border-0" @click="loadRecipe">
        重新加载
      </button>
    </view>
  </view>

  <RecipeDetailContent
    v-else-if="recipe"
    :recipe="recipe"
    shared
    :action-label="ownerPreview ? '转发给朋友' : saving ? '保存中' : '保存至我的菜谱'"
    :action-open-type="ownerPreview ? 'share' : undefined"
    @action="saveRecipe"
  />
</template>
