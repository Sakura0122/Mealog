<script setup lang="ts">
import type { RecipePayload } from '@/api/recipes/type'
import { fileApi } from '@/api/files'
import { recipeApi } from '@/api/recipes'
import { getErrorMessage } from '@/utils/request'

definePage({
  name: 'recipe-create',
  style: {
    navigationStyle: 'custom',
  },
})

const recipeId = ref('')
const loading = ref(false)
const loadError = ref('')

const recipeName = ref('')
const ingredients = ref('')
const steps = ref('')

const coverObjectKey = ref<string | null>(null)
const coverPreviewUrl = ref('')
const pendingCoverPath = ref('')
const loadRecipe = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const recipe = await recipeApi.detail(recipeId.value)
    recipeName.value = recipe.name
    ingredients.value = recipe.ingredients.join('\n')
    steps.value = recipe.steps ?? ''
    coverObjectKey.value = recipe.cover_object_key
    coverPreviewUrl.value = recipe.cover_url ?? ''
  }
  catch (error) {
    loadError.value = getErrorMessage(error)
  }
  finally {
    loading.value = false
  }
}
onLoad((options) => {
  const id = typeof options?.id === 'string' ? options.id : ''
  if (!id)
    return
  recipeId.value = id
  loadRecipe()
})

const chooseCover = () => {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: ({ tempFilePaths }) => {
      const [filePath] = tempFilePaths
      if (filePath) {
        pendingCoverPath.value = filePath
        coverPreviewUrl.value = filePath
      }
    },
  })
}

const removeCover = () => {
  coverObjectKey.value = null
  coverPreviewUrl.value = ''
  pendingCoverPath.value = ''
}

const saving = ref(false)

const buildPayload = (coverKey: string | null): RecipePayload => ({
  name: recipeName.value.trim(),
  cover_object_key: coverKey,
  // 编辑框以换行表达食材顺序，提交时忽略用户输入的空白行。
  ingredients: ingredients.value.split(/\r?\n/).map(item => item.trim()).filter(Boolean),
  steps: steps.value.trim() || null,
})

const saveRecipe = async () => {
  if (!recipeName.value.trim()) {
    useGlobalToast().warning('请输入菜名')
    return
  }

  saving.value = true
  try {
    let coverKey = coverObjectKey.value
    if (pendingCoverPath.value) {
      const uploadedCover = await fileApi.uploadImage(pendingCoverPath.value)
      coverKey = uploadedCover.object_key
    }

    const payload = buildPayload(coverKey)
    if (recipeId.value)
      await recipeApi.update(recipeId.value, payload)
    else
      await recipeApi.create(payload)

    const message = recipeId.value ? '菜谱已更新' : '菜谱已保存'
    uni.navigateBack({
      success: () => useGlobalToast().success(message),
    })
  }
  catch (error) {
    useGlobalToast().error(getErrorMessage(error))
  }
  finally {
    saving.value = false
  }
}
</script>

<template>
  <view class="min-h-screen bg-[#fcf9f6] pb-8">
    <AppTopBar />

    <view v-if="loading" class="h-96 flex items-center justify-center">
      <wd-loading text="加载菜谱中" color="#71836b" />
    </view>

    <view v-else-if="loadError" class="py-20 text-center">
      <wd-empty icon="warning" :tip="loadError" />
      <button class="mx-auto mt-4 border-0 rounded-full bg-[#d5e8cb] px-6 py-2 text-sm text-[#24331f] after:border-0" @click="loadRecipe">
        重新加载
      </button>
    </view>

    <template v-else>
      <view class="relative mx-auto mt-3 w-[280px] rotate-1 bg-white p-3 pb-8 shadow-[0_5px_12px_rgba(0,0,0,0.12)]">
        <button class="m-0 h-[250px] w-full overflow-hidden border-0 bg-[#e5e3e0] p-0 after:border-0" @click="chooseCover">
          <image v-if="coverPreviewUrl" :src="coverPreviewUrl" mode="aspectFill" class="h-full w-full" />
          <view v-else class="h-full w-full flex flex-col items-center justify-center text-[#4f5650]">
            <wd-icon name="camera" size="38px" color="#4f5650" />
            <text class="mt-2 text-sm">
              添加封面图
            </text>
          </view>
        </button>
        <button v-if="coverPreviewUrl" class="absolute right-5 top-5 m-0 h-8 w-8 flex items-center justify-center border-0 rounded-full bg-black/50 p-0 after:border-0" aria-label="移除封面" @click="removeCover">
          <wd-icon name="close" size="16px" color="#ffffff" />
        </button>
        <text class="mx-auto mt-4 block w-max bg-[#dbe4d5] px-4 py-1 text-[10px] text-[#475244] shadow-sm">
          菜谱时刻
        </text>
      </view>

      <view class="mx-5 mt-6 overflow-hidden border border-[#e5e2df] rounded-3xl bg-white shadow-[0_8px_18px_rgba(0,0,0,0.06)]">
        <view class="h-[57px] flex items-center border-b border-[#ebe8e4] px-5">
          <wd-icon name="book" size="18px" color="#5c6949" />
          <input v-model="recipeName" maxlength="100" class="ml-4 min-w-0 flex-1 text-base text-[#1c1c1a]" placeholder="菜名" placeholder-class="text-[#c7c7c1]">
        </view>
        <view class="min-h-[96px] flex items-start border-b border-[#ebe8e4] px-5 py-4">
          <wd-icon name="list" size="18px" color="#777a77" custom-class="mt-1" />
          <textarea v-model="ingredients" class="ml-4 h-20 min-w-0 flex-1 text-base text-[#1c1c1a] leading-6" placeholder="每行输入一种食材" placeholder-class="text-[#c7c7c1]" />
        </view>
        <view class="min-h-[136px] flex items-start px-5 py-4">
          <wd-icon name="file" size="18px" color="#777a77" custom-class="mt-1" />
          <textarea v-model="steps" class="ml-4 h-28 min-w-0 flex-1 text-base text-[#1c1c1a] leading-6" placeholder="制作步骤" placeholder-class="text-[#c7c7c1]" />
        </view>
      </view>

      <button :disabled="saving" class="mx-5 mt-6 h-14 flex items-center justify-center border-0 rounded-full bg-[#d5e8cb] text-base text-[#24331f] font-medium shadow-[0_6px_12px_rgba(0,0,0,0.1)] after:border-0 disabled:opacity-60" @click="saveRecipe">
        <wd-loading v-if="saving" size="20px" color="#24331f" />
        <text :class="saving ? 'ml-2' : ''">
          {{ saving ? '保存中' : recipeId ? '更新菜谱' : '保存菜谱' }}
        </text>
      </button>
    </template>
  </view>
</template>
