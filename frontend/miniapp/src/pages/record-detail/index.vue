<script setup lang="ts">
import type { MealRecordDetail } from '@/api/meal-records/type'
import { mealRecordApi } from '@/api/meal-records'
import { formatDateTimeText } from '@/utils/date'
import { getErrorMessage } from '@/utils/request'

definePage({
  name: 'record-detail',
  style: {
    navigationStyle: 'custom',
  },
})

const recordId = ref('')
const loadError = ref('')
onLoad((options) => {
  recordId.value = typeof options?.id === 'string' ? options.id : ''
  if (!recordId.value)
    loadError.value = '缺少饮食记录 ID'
})

const record = ref<MealRecordDetail>()
const loading = ref(false)
const loadRecord = async () => {
  if (!recordId.value)
    return

  loading.value = true
  loadError.value = ''
  try {
    record.value = await mealRecordApi.detail(recordId.value)
  }
  catch (error) {
    loadError.value = getErrorMessage(error)
  }
  finally {
    loading.value = false
  }
}
onShow(loadRecord)

const editRecord = () => {
  uni.navigateTo({ url: `/pages/record-edit/index?id=${recordId.value}` })
}

const previewImage = (current: string) => {
  if (!record.value)
    return
  uni.previewImage({
    current,
    urls: record.value.images.map(image => image.original_url),
  })
}

const showActions = ref(false)
const actions = [{ name: '删除记录', color: '#d14343' }]
const deleting = ref(false)
const removeRecord = async () => {
  deleting.value = true
  try {
    await mealRecordApi.remove(recordId.value)
    uni.navigateBack({
      success: () => useGlobalToast().success('饮食记录已删除'),
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
  showActions.value = false
  useGlobalDialog().confirm({
    title: '删除饮食记录',
    msg: '删除后无法恢复，确认删除吗？',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    success: (result) => {
      if (result.action === 'confirm')
        removeRecord()
    },
  })
}
</script>

<template>
  <view class="min-h-screen bg-[#fcf9f6] pb-8">
    <!-- 头部只保留返回和更多操作，编辑统一通过页面底部主按钮进入。 -->
    <AppTopBar :more="Boolean(record)" @more="showActions = true" />

    <view v-if="loading && !record" class="h-96 flex items-center justify-center">
      <wd-loading text="加载饮食记录" color="#71836b" />
    </view>

    <view v-else-if="loadError && !record" class="py-20 text-center">
      <wd-empty icon="warning" :tip="loadError" />
      <button v-if="recordId" class="mx-auto mt-4 border-0 rounded-full bg-[#d5e8cb] px-6 py-2 text-sm text-[#24331f] after:border-0" @click="loadRecord">
        重新加载
      </button>
    </view>

    <template v-else-if="record">
      <view class="mx-auto mt-5 w-[196px] rotate-[-1deg] bg-white p-2 pb-7 shadow-[0_4px_12px_rgba(0,0,0,0.08)]">
        <button v-if="record.images[0]" class="m-0 h-[180px] w-full overflow-hidden border-0 bg-[#e8e7e2] p-0 after:border-0" @click="previewImage(record.images[0].original_url)">
          <image :src="record.images[0].original_url" mode="aspectFill" class="h-full w-full" />
        </button>
        <view v-else class="h-[180px] flex flex-col items-center justify-center bg-[#e8e7e2] text-[#777973]">
          <wd-icon name="image" size="36px" color="#777973" />
          <text class="mt-2 text-sm">
            暂无照片
          </text>
        </view>
        <view class="mx-auto mt-2 h-1 w-12 rounded-full bg-[#dfddda]" />
      </view>

      <view v-if="record.images.length > 1" class="mx-5 mt-4 flex gap-2 overflow-x-auto">
        <button v-for="image in record.images" :key="image.id" class="m-0 h-14 w-14 shrink-0 overflow-hidden border-0 rounded-md bg-[#e8e7e2] p-0 after:border-0" @click="previewImage(image.original_url)">
          <image :src="image.original_url" mode="aspectFill" class="h-full w-full" />
        </button>
      </view>

      <view class="mx-5 mt-4 overflow-hidden border border-[#e5e2df] rounded-3xl bg-white shadow-[0_8px_20px_rgba(0,0,0,0.04)]">
        <view class="h-[57px] flex items-center border-b border-[#ebe8e4] px-5">
          <wd-icon name="calendar-line" size="19px" color="#5c6949" />
          <text class="ml-4 text-base text-[#1c1c1a]">
            {{ formatDateTimeText(record.eaten_at) }}
          </text>
        </view>
        <view class="h-[76px] flex items-center border-b border-[#ebe8e4] px-5">
          <wd-icon name="store" size="19px" color="#5c6949" />
          <view class="ml-4 flex rounded-full bg-[#f6f3f0] p-1">
            <text class="rounded-full px-5 py-2 text-base" :class="record.source_type === 'SELF_MADE' ? 'bg-white text-[#52634c] shadow-sm' : 'text-[#8f8f8a]'">
              自己做
            </text>
            <text class="rounded-full px-5 py-2 text-base" :class="record.source_type === 'DINING_OUT' ? 'bg-white text-[#52634c] shadow-sm' : 'text-[#8f8f8a]'">
              外面买
            </text>
          </view>
        </view>

        <view v-if="record.source_type === 'DINING_OUT'" class="min-h-[57px] flex items-center border-b border-[#ebe8e4] bg-[#fbfcf8] px-5 py-3">
          <wd-icon name="location" size="18px" color="#5c6949" />
          <view class="ml-4 min-w-0 flex-1">
            <text class="block truncate text-base" :class="record.store_name ? 'text-[#52634c]' : 'text-[#8f8f8a]'">
              {{ record.store_name || '未关联店铺' }}
            </text>
            <text v-if="record.store_address" class="mt-1 block truncate text-[10px] text-[#777973]">
              {{ record.store_address }}
            </text>
          </view>
        </view>

        <view v-if="record.source_type === 'SELF_MADE' && record.recipe_name" class="h-[57px] flex items-center border-b border-[#ebe8e4] bg-[#fbfcf8] px-5">
          <wd-icon name="book" size="18px" color="#5c6949" />
          <text class="ml-4 text-base text-[#52634c]">
            {{ record.recipe_name }}
          </text>
          <text class="ml-2 rounded px-2 py-1 text-[10px]" :class="record.recipe_status === 'COMPLETED' ? 'bg-[#d5e8cb] text-[#52634c]' : 'bg-[#e7e5e2] text-[#666761]'">
            {{ record.recipe_status === 'COMPLETED' ? '已完善' : '草稿' }}
          </text>
        </view>

        <view class="h-[57px] flex items-center border-b border-[#ebe8e4] px-5">
          <wd-icon name="list" size="18px" color="#5c6949" />
          <text class="ml-4 text-base text-[#1c1c1a]">
            {{ record.dish_name }}
          </text>
        </view>
        <view class="min-h-[112px] flex items-start px-5 py-4">
          <wd-icon name="edit" size="18px" color="#5c6949" custom-class="mt-1" />
          <text class="ml-4 text-base leading-6" :class="record.note ? 'text-[#1c1c1a]' : 'text-[#a5a59f]'">
            {{ record.note || '暂无个人备注' }}
          </text>
        </view>
      </view>

      <button class="mx-5 mt-8 h-14 flex items-center justify-center border-0 rounded-full bg-[#d5e8cb] text-sm text-[#101f0d] shadow-[0_5px_10px_rgba(80,100,72,0.14)] after:border-0" @click="editRecord">
        编辑记录
      </button>

      <wd-action-sheet v-model="showActions" :actions="actions" cancel-text="取消" root-portal @select="confirmDelete" />
      <view v-if="deleting" class="fixed inset-0 z-50 flex items-center justify-center bg-black/20">
        <view class="rounded-lg bg-white px-6 py-4 shadow-lg">
          <wd-loading text="正在删除" color="#71836b" />
        </view>
      </view>
    </template>
  </view>
</template>
