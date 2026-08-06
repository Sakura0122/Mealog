<script setup lang="ts">
import type { MealRecordCalendarDay, MealRecordListItem } from '@/api/meal-records/type'
import { mealRecordApi } from '@/api/meal-records'
import { formatDateParam, formatMonthParam, formatPeriodText, formatTimeText } from '@/utils/date'
import { getErrorMessage } from '@/utils/request'

definePage({
  name: 'home',
  style: {
    navigationStyle: 'custom',
  },
})

interface CalendarCell {
  day: number | null
  date: string
  summary?: MealRecordCalendarDay
}

const monthDate = ref(new Date(new Date().getFullYear(), new Date().getMonth(), 1))
const selectedDate = ref(formatDateParam(new Date()))
const calendarDays = ref<MealRecordCalendarDay[]>([])
const monthTotal = ref(0)
const recordedDays = ref(0)
const records = ref<MealRecordListItem[]>([])
const loading = ref(false)
const loadError = ref('')
let requestSequence = 0

const monthText = computed(() => {
  return `${monthDate.value.getFullYear()}年${monthDate.value.getMonth() + 1}月`
})

const calendarCells = computed<CalendarCell[]>(() => {
  const year = monthDate.value.getFullYear()
  const month = monthDate.value.getMonth()
  const leadingEmptyCount = new Date(year, month, 1).getDay()
  const dayCount = new Date(year, month + 1, 0).getDate()
  const summaries = new Map(calendarDays.value.map(day => [day.date, day]))
  const cells: CalendarCell[] = Array.from({ length: leadingEmptyCount }, () => ({ day: null, date: '' }))

  for (let day = 1; day <= dayCount; day += 1) {
    const date = formatDateParam(new Date(year, month, day))
    cells.push({ day, date, summary: summaries.get(date) })
  }
  return cells
})

const selectedDateText = computed(() => {
  const today = formatDateParam(new Date())
  if (selectedDate.value === today)
    return '今日记录'
  const [, month, day] = selectedDate.value.split('-')
  return `${Number(month)}月${Number(day)}日记录`
})

const loadHome = async () => {
  const sequence = ++requestSequence
  const month = formatMonthParam(monthDate.value)
  const targetDate = selectedDate.value
  loading.value = true
  loadError.value = ''
  try {
    const [calendar, recordPage] = await Promise.all([
      mealRecordApi.calendar(month),
      mealRecordApi.list({ current_page: 1, page_size: 50, date: targetDate }),
    ])
    // 日期快速切换时只接收最后一次请求，避免旧日期记录覆盖当前选择。
    if (sequence !== requestSequence)
      return
    calendarDays.value = calendar.days
    monthTotal.value = calendar.total
    recordedDays.value = calendar.recorded_days
    records.value = recordPage.list
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

const skipNextHomeLoad = ref(false)
onShow(() => {
  // 原生相册或相机返回也会触发 onShow，此时首页数据没有变化，无需重复请求。
  if (skipNextHomeLoad.value) {
    skipNextHomeLoad.value = false
    return
  }
  loadHome()
})

const changeMonth = (offset: number) => {
  const nextMonth = new Date(monthDate.value.getFullYear(), monthDate.value.getMonth() + offset, 1)
  monthDate.value = nextMonth
  calendarDays.value = []
  monthTotal.value = 0
  recordedDays.value = 0
  records.value = []
  const now = new Date()
  selectedDate.value = now.getFullYear() === nextMonth.getFullYear()
    && now.getMonth() === nextMonth.getMonth()
    ? formatDateParam(now)
    : formatDateParam(nextMonth)
  loadHome()
}

const selectDate = (cell: CalendarCell) => {
  if (!cell.day || cell.date === selectedDate.value)
    return
  selectedDate.value = cell.date
  records.value = []
  loadHome()
}

const showSourcePicker = ref(false)
const getDefaultEatenAt = () => {
  const now = new Date()
  if (selectedDate.value === formatDateParam(now))
    return now.getTime()

  const [year, month, day] = selectedDate.value.split('-').map(Number)
  // 补记非当天饮食时默认使用正午，既保留所选日期，也避免沿用当前时刻造成误解。
  return new Date(year, month - 1, day, 12).getTime()
}

const chooseRecordImage = (sourceType: 'camera' | 'album') => {
  skipNextHomeLoad.value = true
  uni.chooseImage({
    count: 9,
    sizeType: ['original'],
    sourceType: [sourceType],
    success: ({ tempFilePaths }) => {
      // 部分 uni-app 平台声明单图结果为字符串，进入编辑页前统一成路径数组。
      const imagePaths = Array.isArray(tempFilePaths) ? tempFilePaths : [tempFilePaths]
      if (!imagePaths[0])
        return
      showSourcePicker.value = false
      uni.navigateTo({
        url: '/pages/record-edit/index',
        success: ({ eventChannel }) => {
          // 临时路径不拼接到 URL，避免多图路径超过页面地址长度限制。
          eventChannel.emit('selectedRecordImages', {
            imagePaths,
            takenAt: getDefaultEatenAt(),
          })
        },
      })
    },
  })
}

const openRecordEditor = (recordId: string) => {
  uni.navigateTo({ url: `/pages/record-edit/index?id=${recordId}` })
}
</script>

<template>
  <view class="min-h-screen bg-[#f8fafc] pb-32">
    <!-- 首页只保留品牌标题，右侧留给微信胶囊按钮。 -->
    <wd-navbar safe-area-inset-top custom-style="background: rgba(252, 249, 246, 0.8);">
      <template #left>
        <text class="text-[28px] text-[#52634c] font-bold leading-7">
          Mealog
        </text>
      </template>
    </wd-navbar>

    <view class="mx-auto max-w-[448px] flex flex-col gap-[11px] px-5 pt-4">
      <view class="flex flex-col gap-4 rounded-[32px] bg-white px-6 pb-6 pt-[10px] shadow-[0_4px_20px_rgba(0,0,0,0.03)]">
        <view class="h-8 flex items-center justify-between">
          <button class="m-0 h-8 w-8 flex items-center justify-center border-0 bg-transparent p-0 after:border-0" aria-label="上个月" @click="changeMonth(-1)">
            <wd-icon name="arrow-left" size="18px" color="#52634c" />
          </button>
          <text class="text-center text-base text-[#1c1c1a] leading-6">
            {{ monthText }}
          </text>
          <button class="m-0 h-8 w-8 flex items-center justify-center border-0 bg-transparent p-0 after:border-0" aria-label="下个月" @click="changeMonth(1)">
            <wd-icon name="arrow-right" size="18px" color="#52634c" />
          </button>
        </view>
        <view class="grid grid-cols-7 pt-2 text-center text-xs text-[#8b9187] leading-4">
          <text v-for="week in ['周日', '周一', '周二', '周三', '周四', '周五', '周六']" :key="week">
            {{ week }}
          </text>
        </view>
        <view class="grid grid-cols-7 gap-2">
          <view v-for="(cell, index) in calendarCells" :key="cell.date || `empty-${index}`" class="aspect-[0.76] min-w-0">
            <button
              v-if="cell.day"
              class="relative m-0 h-full w-full overflow-hidden border-0 rounded-xl p-0 after:border-0"
              :class="cell.date === selectedDate ? 'ring-2 ring-[#71836b]' : ''"
              @click="selectDate(cell)"
            >
              <image v-if="cell.summary?.cover_url" :src="cell.summary.cover_url" mode="aspectFill" class="h-full w-full" />
              <view v-else class="h-full flex items-center justify-center bg-[#f6f3f0] text-base text-[#444841]">
                {{ cell.day }}
              </view>
              <text v-if="cell.summary?.cover_url" class="absolute left-1 top-0 rounded-sm bg-black/45 px-1 text-xs text-white">
                {{ cell.day }}
              </text>
              <text v-if="cell.summary && cell.summary.record_count > 1" class="absolute bottom-0 right-0 min-w-4 rounded-tl-md bg-black/55 px-1 text-[9px] text-white">
                {{ cell.summary.record_count }}
              </text>
            </button>
          </view>
        </view>
        <view class="grid grid-cols-[1fr_1px_1fr] items-center border-t border-[#c4c8be]/20 pt-4 text-center">
          <view class="flex flex-col gap-1">
            <text class="text-[10px] text-[#8b9187] leading-[14px]">
              本月记录
            </text>
            <text class="text-xl text-[#52634c] font-semibold leading-7">
              {{ monthTotal }}
            </text>
          </view>
          <view class="h-8 bg-[#c4c8be]/20" />
          <view class="flex flex-col gap-1">
            <text class="text-[10px] text-[#8b9187] leading-[14px]">
              记录天数
            </text>
            <text class="text-xl text-[#52634c] font-semibold leading-7">
              {{ recordedDays }}
            </text>
          </view>
        </view>
      </view>

      <button class="m-0 h-12 w-full flex items-center justify-center border-0 rounded-full bg-[#d5e8cb] p-0 text-xs text-[#101f0d] font-medium after:border-0" @click="showSourcePicker = true">
        新增记录
      </button>

      <view class="flex flex-col gap-1.5 pt-1">
        <text class="px-2 text-xs text-[#8b9187] leading-4">
          {{ selectedDateText }}
        </text>

        <view v-if="loading" class="h-32 flex items-center justify-center">
          <wd-loading text="加载饮食记录" color="#71836b" />
        </view>
        <view v-else-if="loadError" class="py-8 text-center">
          <wd-empty icon="warning" :tip="loadError" />
          <button class="mx-auto mt-3 border-0 rounded-full bg-[#d5e8cb] px-5 py-2 text-sm after:border-0" @click="loadHome">
            重新加载
          </button>
        </view>
        <wd-empty v-else-if="records.length === 0" custom-class="mt-4" icon="calendar" tip="这一天还没有饮食记录" />
        <view v-else class="flex flex-col gap-4">
          <button v-for="record in records" :key="record.id" class="m-0 h-24 w-full flex items-center border-0 rounded-3xl bg-white px-4 py-[14px] text-left shadow-[0_10px_25px_-5px_rgba(82,99,76,0.08)] after:border-0" @click="openRecordEditor(record.id)">
            <view class="w-[55px] flex shrink-0 flex-col items-center border-r border-[#c4c8be]/30 pr-4">
              <text class="text-[10px] text-[#8b9187] leading-[14px]">
                {{ formatPeriodText(record.eaten_at) }}
              </text>
              <text class="text-sm text-[#1c1c1a] font-semibold leading-5">
                {{ formatTimeText(record.eaten_at) }}
              </text>
            </view>
            <view class="min-w-0 flex-1 pl-4">
              <text class="block truncate text-base text-[#1c1c1a] font-medium leading-6">
                {{ record.dish_name }}
              </text>
              <text class="block truncate text-sm text-[#5f645e] leading-5">
                {{ record.note || '暂无备注' }}
              </text>
            </view>
            <view class="ml-3 h-16 w-16 shrink-0 overflow-hidden border-2 border-white rounded-xl bg-[#e8e7e2] shadow-[2px_4px_8px_rgba(82,99,76,0.12)]">
              <image v-if="record.cover_url" :src="record.cover_url" mode="aspectFill" class="h-full w-full" />
              <view v-else class="h-full flex items-center justify-center">
                <wd-icon name="image" size="24px" color="#8b9187" />
              </view>
            </view>
          </button>
        </view>
      </view>
    </view>

    <AppBottomNav active="home" />

    <wd-popup v-model="showSourcePicker" position="bottom" :z-index="50" root-portal modal-style="background: rgba(28, 28, 26, 0.72); -webkit-backdrop-filter: blur(32px); backdrop-filter: blur(32px);" custom-style="background: transparent; padding: 0 24px calc(env(safe-area-inset-bottom) + 60px);">
      <view class="flex flex-col gap-4 pb-16">
        <button class="m-0 h-[114px] w-full flex items-center border-0 rounded-3xl bg-white px-6 text-left shadow-[0_12px_25px_rgba(0,0,0,0.12)] after:border-0" @click="chooseRecordImage('camera')">
          <view class="mr-6 h-16 w-16 flex items-center justify-center rounded-2xl bg-[#e1e6c2]">
            <wd-icon name="camera" size="30px" color="#5f6848" />
          </view>
          <text class="text-xl text-[#1c1c1a]">
            拍照
          </text>
        </button>
        <button class="m-0 h-[114px] w-full flex items-center border-0 rounded-3xl bg-white px-6 text-left shadow-[0_12px_25px_rgba(0,0,0,0.12)] after:border-0" @click="chooseRecordImage('album')">
          <view class="mr-6 h-16 w-16 flex items-center justify-center rounded-2xl bg-[#ffd29a]">
            <wd-icon name="image" size="30px" color="#6d5d6e" />
          </view>
          <text class="text-xl text-[#1c1c1a]">
            从相册选择
          </text>
        </button>
        <button class="mx-auto mt-2 h-14 w-14 flex items-center justify-center border-0 rounded-full bg-[#1c1c1a] p-0 after:border-0" aria-label="关闭" @click="showSourcePicker = false">
          <wd-icon name="close" size="24px" color="#ffffff" />
        </button>
      </view>
    </wd-popup>
  </view>
</template>
