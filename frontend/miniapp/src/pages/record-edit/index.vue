<script setup lang="ts">
import type { MealRecordPayload, MealSourceType } from '@/api/meal-records/type'
import type { RecipeListItem } from '@/api/recipes/type'
import type { StoreItem } from '@/api/stores/type'
import { fileApi } from '@/api/files'
import { mealRecordApi } from '@/api/meal-records'
import { recipeApi } from '@/api/recipes'
import { storeApi } from '@/api/stores'
import { formatDateTimePayload, formatDateTimeText, parseLocalDate } from '@/utils/date'
import { getImageTakenAt } from '@/utils/image-exif'
import { getErrorMessage } from '@/utils/request'

definePage({
  name: 'record-edit',
  style: {
    navigationStyle: 'custom',
  },
})

interface EditableImage {
  previewUrl: string
  originalObjectKey?: string
  processedObjectKey?: string | null
  pendingPath?: string
}

interface SelectedRecordImagesPayload {
  imagePaths: string[]
  takenAt: number | null
  photoTimeMissing: boolean
}

const pageInstance = getCurrentInstance()?.proxy as {
  getOpenerEventChannel?: () => UniNamespace.EventChannel
} | null

const recordId = ref('')
const loading = ref(false)
const loadError = ref('')

const eatenAt = ref(Date.now())
const showDatePicker = ref(false)
const photoTimeMissing = ref(false)

const sourceType = ref<MealSourceType>('SELF_MADE')
const dishName = ref('')
const note = ref('')

const selectedRecipeId = ref('')
const recipeOptions = ref<RecipeListItem[]>([])
const showSuggestions = ref(false)
const filteredRecipes = computed(() => {
  const keyword = dishName.value.trim()
  if (!keyword)
    return recipeOptions.value.slice(0, 5)
  return recipeOptions.value.filter(recipe => recipe.name.includes(keyword)).slice(0, 5)
})

const loadRecipes = async () => {
  try {
    const page = await recipeApi.list({ current_page: 1, page_size: 50 })
    recipeOptions.value = page.list
  }
  catch (error) {
    useGlobalToast().error(getErrorMessage(error))
  }
}

const chooseRecipe = (recipe: RecipeListItem) => {
  selectedRecipeId.value = recipe.id
  dishName.value = recipe.name
  showSuggestions.value = false
}

const clearRecipeSelection = () => {
  selectedRecipeId.value = ''
}

const selectedStore = ref<StoreItem>()
const showStorePicker = ref(false)
const stores = ref<StoreItem[]>([])
const storesLoading = ref(false)
const storesError = ref('')
const storeKeyword = ref('')
let storeRequestSequence = 0

const loadStores = async () => {
  const sequence = ++storeRequestSequence
  storesLoading.value = true
  storesError.value = ''
  try {
    const page = await storeApi.list({
      current_page: 1,
      page_size: 50,
      keyword: storeKeyword.value.trim() || undefined,
    })
    if (sequence !== storeRequestSequence)
      return
    stores.value = page.list
  }
  catch (error) {
    if (sequence === storeRequestSequence)
      storesError.value = getErrorMessage(error)
  }
  finally {
    if (sequence === storeRequestSequence)
      storesLoading.value = false
  }
}

let storeSearchTimer: ReturnType<typeof setTimeout> | undefined
watch(storeKeyword, () => {
  if (storeSearchTimer)
    clearTimeout(storeSearchTimer)
  if (!showStorePicker.value)
    return
  storeSearchTimer = setTimeout(loadStores, 300)
})
onUnmounted(() => {
  if (storeSearchTimer)
    clearTimeout(storeSearchTimer)
})

const openStorePicker = () => {
  showStorePicker.value = true
  loadStores()
}

const chooseStore = (store: StoreItem) => {
  selectedStore.value = store
  showStorePicker.value = false
}

const mapSaving = ref(false)
const saveMapStore = async (location: UniNamespace.ChooseLocationSuccess) => {
  if (!location.name.trim()) {
    useGlobalToast().warning('请选择具体店铺')
    return
  }

  mapSaving.value = true
  try {
    const store = await storeApi.create({
      name: location.name,
      address: location.address.trim() || null,
      latitude: location.latitude,
      longitude: location.longitude,
    })
    selectedStore.value = store
    showStorePicker.value = false
  }
  catch (error) {
    useGlobalToast().error(getErrorMessage(error))
  }
  finally {
    mapSaving.value = false
  }
}

const chooseMapStore = () => {
  uni.chooseLocation({
    success: location => saveMapStore(location),
    fail: ({ errMsg }) => {
      if (!errMsg.includes('cancel'))
        useGlobalToast().error('无法打开地图，请检查定位权限')
    },
  })
}

const chooseSource = (type: MealSourceType) => {
  sourceType.value = type
  showSuggestions.value = type === 'SELF_MADE'
  if (type === 'SELF_MADE')
    selectedStore.value = undefined
  else
    selectedRecipeId.value = ''
}

const images = ref<EditableImage[]>([])
const chooseImages = (sourceTypeOption?: 'camera' | 'album') => {
  const remaining = 9 - images.value.length
  if (remaining === 0) {
    useGlobalToast().warning('最多添加 9 张图片')
    return
  }

  uni.chooseImage({
    count: remaining,
    // 首张原图用于读取拍摄时间，上传前仍由统一文件服务压缩。
    sizeType: ['original'],
    sourceType: sourceTypeOption ? [sourceTypeOption] : ['album', 'camera'],
    success: async ({ tempFilePaths }) => {
      // 部分 uni-app 平台声明单图结果为字符串，提交前统一成路径数组。
      const paths = Array.isArray(tempFilePaths) ? tempFilePaths : [tempFilePaths]
      const shouldUseTakenAt = !recordId.value && images.value.length === 0 && Boolean(paths[0])
      const takenAt = shouldUseTakenAt ? await getImageTakenAt(paths[0]) : null
      images.value.push(...paths.map(path => ({ previewUrl: path, pendingPath: path })))
      if (shouldUseTakenAt) {
        if (takenAt !== null) {
          eatenAt.value = takenAt
          photoTimeMissing.value = false
        }
        else if (sourceTypeOption === 'camera') {
          eatenAt.value = Date.now()
          photoTimeMissing.value = false
        }
        else {
          // 相册图可能被转存或清除元数据，不能把临时文件生成时间冒充拍摄时间。
          photoTimeMissing.value = true
          useGlobalToast().warning('照片不含拍摄时间，请手动选择')
        }
      }
    },
  })
}

const removeImage = (index: number) => {
  images.value.splice(index, 1)
  if (images.value.length === 0)
    photoTimeMissing.value = false
}

const previewImages = (current: string) => {
  uni.previewImage({
    current,
    urls: images.value.map(image => image.previewUrl),
  })
}

const loadRecord = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const record = await mealRecordApi.detail(recordId.value)
    eatenAt.value = parseLocalDate(record.eaten_at).getTime()
    sourceType.value = record.source_type ?? 'SELF_MADE'
    dishName.value = record.dish_name
    note.value = record.note ?? ''
    selectedRecipeId.value = record.recipe_id ?? ''
    if (record.store_id && record.store_name) {
      selectedStore.value = {
        id: record.store_id,
        name: record.store_name,
        address: record.store_address,
        latitude: null,
        longitude: null,
        usage_count: 0,
        updated_at: record.updated_at,
      }
    }
    images.value = record.images.map(image => ({
      previewUrl: image.original_url,
      originalObjectKey: image.original_object_key,
      processedObjectKey: image.processed_object_key,
    }))
  }
  catch (error) {
    loadError.value = getErrorMessage(error)
  }
  finally {
    loading.value = false
  }
}

onLoad((options) => {
  loadRecipes()
  const id = typeof options?.id === 'string' ? options.id : ''
  if (id) {
    recordId.value = id
    loadRecord()
  }

  const imagePath = typeof options?.image === 'string' ? options.image : ''
  if (imagePath) {
    const decodedPath = decodeURIComponent(imagePath)
    images.value.push({ previewUrl: decodedPath, pendingPath: decodedPath })
  }

  const takenAt = Number(options?.takenAt)
  if (!id && Number.isFinite(takenAt) && takenAt > 0)
    eatenAt.value = takenAt
  photoTimeMissing.value = !id && options?.photoTimeMissing === '1'

  const eventChannel = pageInstance?.getOpenerEventChannel?.()
  eventChannel?.once('selectedRecordImages', (payload: SelectedRecordImagesPayload) => {
    // 首页最多传入 9 张临时图片，新增页沿用现有图片列表和上传流程。
    images.value.push(...payload.imagePaths.map(path => ({ previewUrl: path, pendingPath: path })))
    if (payload.takenAt !== null)
      eatenAt.value = payload.takenAt
    photoTimeMissing.value = payload.photoTimeMissing
  })
})

const openDatePicker = () => {
  // 收起输入态内容，避免菜谱建议层和键盘盖住时间选择器。
  showSuggestions.value = false
  uni.hideKeyboard()
  showDatePicker.value = true
}

const confirmPhotoTime = () => {
  photoTimeMissing.value = false
}

const saving = ref(false)
const uploadImages = async () => {
  const payloadImages: MealRecordPayload['images'] = []
  for (const image of images.value) {
    if (image.pendingPath) {
      const uploaded = await fileApi.uploadImage(image.pendingPath)
      payloadImages.push({ original_object_key: uploaded.object_key, processed_object_key: null })
    }
    else if (image.originalObjectKey) {
      payloadImages.push({
        original_object_key: image.originalObjectKey,
        processed_object_key: image.processedObjectKey ?? null,
      })
    }
  }
  return payloadImages
}

const saveRecord = async () => {
  if (photoTimeMissing.value) {
    useGlobalToast().warning('请选择进食时间')
    return
  }
  if (!dishName.value.trim()) {
    useGlobalToast().warning('请输入菜品名称')
    return
  }

  saving.value = true
  try {
    const payload: MealRecordPayload = {
      dish_name: dishName.value.trim(),
      eaten_at: formatDateTimePayload(eatenAt.value),
      source_type: sourceType.value,
      store_id: sourceType.value === 'DINING_OUT' ? selectedStore.value?.id ?? null : null,
      recipe_id: sourceType.value === 'SELF_MADE' ? selectedRecipeId.value || null : null,
      note: note.value.trim() || null,
      images: await uploadImages(),
    }

    const isEditing = Boolean(recordId.value)
    if (isEditing)
      await mealRecordApi.update(recordId.value, payload)
    else
      await mealRecordApi.create(payload)

    // 保存后清空详情和编辑页栈，确保新增、编辑都直接回到首页。
    uni.reLaunch({
      url: '/pages/index/index',
      success: () => useGlobalToast().success(isEditing ? '饮食记录已更新' : '饮食记录已保存'),
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
    <AppTopBar home />

    <view v-if="loading" class="h-96 flex items-center justify-center">
      <wd-loading text="加载饮食记录" color="#71836b" />
    </view>

    <view v-else-if="loadError" class="py-20 text-center">
      <wd-empty icon="warning" :tip="loadError" />
      <button class="mx-auto mt-4 border-0 rounded-full bg-[#d5e8cb] px-6 py-2 text-sm text-[#24331f] after:border-0" @click="loadRecord">
        重新加载
      </button>
    </view>

    <template v-else>
      <view class="relative mx-auto mt-4 w-[196px] rotate-[-1deg] bg-white p-2 pb-7 shadow-[0_4px_12px_rgba(0,0,0,0.08)]">
        <view v-if="images[0]" class="relative h-[180px] w-full overflow-hidden bg-[#e5e3e0]" @click="previewImages(images[0].previewUrl)">
          <image :src="images[0].previewUrl" mode="aspectFill" class="h-full w-full" />
          <button class="absolute right-2 top-2 m-0 h-8 w-8 flex items-center justify-center border-0 rounded-full bg-black/50 p-0 after:border-0" aria-label="移除图片" @click.stop="removeImage(0)">
            <wd-icon name="close" size="16px" color="#ffffff" />
          </button>
        </view>
        <button v-else class="m-0 h-[180px] w-full flex flex-col items-center justify-center border-0 bg-[#e8e7e2] p-0 text-[#596455] after:border-0" @click="chooseImages()">
          <wd-icon name="camera" size="38px" color="#596455" />
          <text class="mt-2 text-sm">
            添加饮食照片
          </text>
        </button>
        <view class="mx-auto mt-2 h-1 w-12 rounded-full bg-[#dfddda]" />
        <button v-if="images.length && images.length < 9" class="absolute bottom-0 right-[-14px] m-0 h-11 w-11 flex items-center justify-center border-0 rounded-full bg-[#e1e6c2] p-0 shadow-[0_3px_8px_rgba(82,99,76,0.16)] after:border-0" aria-label="继续添加图片" @click="chooseImages()">
          <wd-icon name="camera" size="23px" color="#5f6848" />
          <view class="absolute right-0 top-0 h-3.5 w-3.5 flex items-center justify-center rounded-full bg-[#f7f5ef]">
            <wd-icon name="plus" size="10px" color="#5f6848" />
          </view>
        </button>
      </view>

      <view v-if="images.length" class="mx-5 mt-4 flex gap-2 overflow-x-auto">
        <view v-for="(image, index) in images.slice(1)" :key="image.previewUrl" class="relative h-14 w-14 shrink-0 overflow-hidden rounded-md bg-[#e8e7e2]" @click="previewImages(image.previewUrl)">
          <image :src="image.previewUrl" mode="aspectFill" class="h-full w-full" />
          <button class="absolute right-0 top-0 m-0 h-5 w-5 flex items-center justify-center border-0 rounded-full bg-black/50 p-0 after:border-0" aria-label="移除图片" @click.stop="removeImage(index + 1)">
            <wd-icon name="close" size="11px" color="#ffffff" />
          </button>
        </view>
      </view>

      <view class="mx-5 mt-4 overflow-visible border border-[#e5e2df] rounded-3xl bg-white shadow-[0_8px_20px_rgba(0,0,0,0.04)]">
        <button class="m-0 h-[57px] w-full flex items-center border-0 border-b border-[#ebe8e4] bg-transparent px-5 text-left after:border-0" @click="openDatePicker">
          <wd-icon name="calendar-line" size="19px" color="#5c6949" />
          <text class="ml-4 text-base" :class="photoTimeMissing ? 'text-[#a14444]' : 'text-[#1c1c1a]'">
            {{ photoTimeMissing ? '请选择进食时间' : formatDateTimeText(eatenAt) }}
          </text>
          <wd-icon name="arrow-right" size="15px" color="#c6c8c3" custom-class="ml-auto" />
        </button>

        <view class="h-[76px] flex items-center border-b border-[#ebe8e4] px-5">
          <wd-icon name="store" size="19px" color="#5c6949" />
          <view class="ml-4 flex rounded-full bg-[#f6f3f0] p-1">
            <button class="m-0 h-10 flex items-center justify-center border-0 rounded-full px-5 text-base after:border-0" :class="sourceType === 'SELF_MADE' ? 'bg-white text-[#52634c] shadow-sm' : 'bg-transparent text-[#8f8f8a]'" @click="chooseSource('SELF_MADE')">
              自己做
            </button>
            <button class="m-0 h-10 flex items-center justify-center border-0 rounded-full px-5 text-base after:border-0" :class="sourceType === 'DINING_OUT' ? 'bg-white text-[#1c1c1a] shadow-sm' : 'bg-transparent text-[#8f8f8a]'" @click="chooseSource('DINING_OUT')">
              外面买
            </button>
          </view>
        </view>

        <view v-if="sourceType === 'SELF_MADE'" class="relative">
          <view class="h-[57px] flex items-center border-b border-[#ebe8e4] px-5">
            <wd-icon name="book" size="18px" color="#5c6949" />
            <input v-model="dishName" maxlength="100" class="ml-4 min-w-0 flex-1 text-base text-[#1c1c1a]" placeholder="选择已有菜谱或输入菜品名称" placeholder-class="text-[#c7c7c1]" @focus="showSuggestions = true" @input="clearRecipeSelection">
          </view>
          <view v-if="showSuggestions && filteredRecipes.length" class="absolute left-1 right-1 top-[56px] z-20 border border-[#d5d3ce] rounded-lg bg-white px-8 shadow-[0_8px_18px_rgba(0,0,0,0.12)]">
            <button v-for="recipe in filteredRecipes" :key="recipe.id" class="m-0 min-h-[59px] w-full flex items-center border-0 border-b border-[#eceae6] bg-transparent py-2 text-left after:border-0 last:border-b-0" @click="chooseRecipe(recipe)">
              <view>
                <view class="flex items-center gap-2">
                  <text class="text-sm text-[#1c1c1a] font-medium">
                    {{ recipe.name }}
                  </text>
                  <text class="rounded px-1.5 py-0.5 text-[10px]" :class="recipe.status === 'COMPLETED' ? 'bg-[#d5e8cb] text-[#52634c]' : 'bg-[#e7e5e2] text-[#666761]'">
                    {{ recipe.status === 'COMPLETED' ? '已完善' : '草稿' }}
                  </text>
                </view>
                <text class="mt-1 block text-[10px] text-[#777973]">
                  做过 {{ recipe.usage_count }} 次
                </text>
              </view>
            </button>
          </view>
        </view>

        <template v-else>
          <button class="m-0 min-h-[57px] w-full flex items-center border-0 border-b border-[#ebe8e4] bg-transparent px-5 py-3 text-left after:border-0" @click="openStorePicker">
            <wd-icon name="location" size="19px" color="#5c6949" />
            <view class="ml-4 min-w-0 flex-1">
              <text class="block truncate text-base" :class="selectedStore ? 'text-[#1c1c1a]' : 'text-[#c7c7c1]'">
                {{ selectedStore?.name ?? '选择店铺' }}
              </text>
              <text v-if="selectedStore?.address" class="mt-1 block truncate text-[10px] text-[#8f8f8a]">
                {{ selectedStore.address }}
              </text>
            </view>
            <wd-icon name="arrow-right" size="15px" color="#c6c8c3" />
          </button>
          <view class="h-[57px] flex items-center border-b border-[#ebe8e4] px-5">
            <wd-icon name="book" size="18px" color="#5c6949" />
            <input v-model="dishName" maxlength="100" class="ml-4 min-w-0 flex-1 text-base text-[#1c1c1a]" placeholder="输入菜品名称" placeholder-class="text-[#c7c7c1]">
          </view>
        </template>

        <view class="min-h-[112px] flex items-start px-5 py-4">
          <wd-icon name="edit" size="18px" color="#5c6949" custom-class="mt-1" />
          <textarea v-model="note" maxlength="1000" class="ml-4 h-20 min-w-0 flex-1 text-base text-[#1c1c1a] leading-6" placeholder="个人备注..." placeholder-class="text-[#c7c7c1]" />
        </view>
      </view>

      <button :disabled="saving" class="mx-5 mt-7 h-14 flex items-center justify-center border-0 rounded-full bg-[#d5e8cb] text-sm text-[#101f0d] shadow-[0_5px_10px_rgba(80,100,72,0.14)] after:border-0 disabled:opacity-60" @click="saveRecord">
        <wd-loading v-if="saving" size="20px" color="#24331f" />
        <text :class="saving ? 'ml-2' : ''">
          {{ saving ? '保存中' : recordId ? '更新记录' : '保存记录' }}
        </text>
      </button>
    </template>

    <wd-datetime-picker v-model="eatenAt" v-model:visible="showDatePicker" :z-index="100" type="datetime" title="选择进食时间" root-portal @confirm="confirmPhotoTime" />

    <wd-popup v-model="showStorePicker" position="bottom" round safe-area-inset-bottom root-portal custom-style="max-height: 75vh; background: #fcf9f6;">
      <view class="px-5 pb-5 pt-4">
        <view class="flex items-center justify-between">
          <text class="text-lg text-[#1c1c1a] font-semibold">
            选择店铺
          </text>
          <button class="m-0 h-9 flex items-center border-0 rounded-full bg-[#d5e8cb] px-4 text-sm text-[#24331f] after:border-0" :disabled="mapSaving" @click="chooseMapStore">
            <wd-loading v-if="mapSaving" size="16px" color="#24331f" />
            <wd-icon v-else name="location" size="17px" color="#24331f" />
            <text class="ml-1">
              {{ mapSaving ? '保存中' : '地图选择' }}
            </text>
          </button>
        </view>

        <view class="mt-4 h-11 flex items-center rounded-full bg-white px-4">
          <wd-icon name="search-line" size="19px" color="#777973" />
          <input v-model="storeKeyword" class="ml-3 min-w-0 flex-1 text-sm text-[#1c1c1a]" placeholder="搜索吃过的店铺" placeholder-class="text-[#a5a59f]">
        </view>

        <view v-if="storesLoading" class="h-48 flex items-center justify-center">
          <wd-loading text="加载历史店铺" color="#71836b" />
        </view>
        <view v-else-if="storesError" class="py-10 text-center">
          <wd-empty icon="warning" :tip="storesError" />
          <button class="mx-auto mt-3 border-0 rounded-full bg-[#d5e8cb] px-5 py-2 text-sm after:border-0" @click="loadStores">
            重新加载
          </button>
        </view>
        <wd-empty v-else-if="stores.length === 0" custom-class="mt-8" icon="location" :tip="storeKeyword ? '没有找到相关店铺' : '还没有历史店铺，可从地图选择'" />
        <scroll-view v-else scroll-y class="mt-3 max-h-[48vh]">
          <button v-for="store in stores" :key="store.id" class="m-0 min-h-[64px] w-full flex items-center border-0 border-b border-[#ebe8e4] bg-transparent py-3 text-left after:border-0" @click="chooseStore(store)">
            <wd-icon name="store" size="20px" color="#5c6949" />
            <view class="ml-3 min-w-0 flex-1">
              <text class="block truncate text-sm text-[#1c1c1a] font-medium">
                {{ store.name }}
              </text>
              <text v-if="store.address" class="mt-1 block truncate text-[10px] text-[#777973]">
                {{ store.address }}
              </text>
            </view>
            <text class="ml-3 text-[10px] text-[#777973]">
              吃过 {{ store.usage_count }} 次
            </text>
          </button>
        </scroll-view>
      </view>
    </wd-popup>
  </view>
</template>
