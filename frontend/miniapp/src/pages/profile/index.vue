<script setup lang="ts">
import type { UserProfile, UserStatistics } from '@/api/users/type'
import { userApi } from '@/api/users'
import { getErrorMessage } from '@/utils/request'

definePage({
  name: 'profile',
  style: {
    navigationStyle: 'custom',
  },
})

const profile = ref<UserProfile>()
const statistics = ref<UserStatistics>()
const loading = ref(false)
const loadError = ref('')
const loadProfile = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const [profileData, statisticsData] = await Promise.all([
      userApi.profile(),
      userApi.statistics(),
    ])
    profile.value = profileData
    statistics.value = statisticsData
  }
  catch (error) {
    loadError.value = getErrorMessage(error)
  }
  finally {
    loading.value = false
  }
}
onShow(loadProfile)

const formatCount = (count: number | undefined) => {
  return count === undefined ? '--' : count.toLocaleString('zh-CN')
}

const editProfile = () => {
  uni.navigateTo({ url: '/pages/profile-edit/index' })
}

const openRecipes = () => {
  uni.navigateTo({ url: '/pages/recipes/index' })
}
</script>

<template>
  <view class="min-h-screen bg-[#f8fafc] pb-32">
    <view class="px-5 pt-8">
      <text class="text-[28px] text-[#52634c] font-bold leading-7">
        Mealog
      </text>

      <view v-if="loading && !profile" class="mt-7 h-24 flex items-center">
        <wd-loading text="加载个人信息" color="#71836b" />
      </view>

      <view v-else class="mt-7 flex items-center">
        <button class="m-0 h-24 w-24 shrink-0 overflow-hidden border-0 rounded-full bg-[#edf1ea] p-0 after:border-0" aria-label="编辑头像" @click="editProfile">
          <image :src="profile?.avatar_url || '/static/images/profile-avatar.jpg'" mode="aspectFill" class="h-full w-full" />
        </button>
        <button class="m-0 ml-4 min-w-0 border-0 bg-transparent p-0 text-left after:border-0" @click="editProfile">
          <text class="block truncate text-2xl text-[#1c1c1a] font-medium">
            {{ profile?.nickname || '设置昵称' }}
          </text>
        </button>
      </view>

      <button v-if="loadError" class="m-0 mt-3 border-0 bg-transparent p-0 text-sm text-[#a14444] after:border-0" @click="loadProfile">
        {{ loadError }}，点击重试
      </button>

      <view class="grid grid-cols-2 mt-7 gap-4">
        <view class="rounded-3xl bg-[#f3f6ef] px-4 py-2.5">
          <text class="block text-xs text-[#6f7b68] leading-4">
            累计记录
          </text>
          <text class="mt-1 block text-2xl text-[#1d2a19] font-semibold leading-8">
            {{ formatCount(statistics?.total_records) }}
          </text>
        </view>
        <view class="rounded-3xl bg-[#f3f6ef] px-4 py-2.5">
          <text class="block text-xs text-[#6f7b68] leading-4">
            记录天数
          </text>
          <text class="mt-1 block text-2xl text-[#1d2a19] font-semibold leading-8">
            {{ formatCount(statistics?.recorded_days) }}
          </text>
        </view>
      </view>

      <view class="mt-11 overflow-hidden border border-[#e5e2df] rounded-3xl bg-white">
        <button class="m-0 h-[89px] w-full flex items-center border-0 border-b border-[#e5e2df] bg-transparent px-4 text-left after:border-0" @click="openRecipes">
          <view class="h-10 w-10 flex items-center justify-center rounded-full bg-[#f8faf7]">
            <wd-icon name="book" size="23px" color="#59604f" />
          </view>
          <text class="ml-4 text-base text-[#1c1c1a] font-medium">
            我的菜谱
          </text>
          <text class="ml-3 rounded-full bg-[#d5e8cb] px-2 py-1 text-xs text-[#42543d]">
            18
          </text>
          <wd-icon name="arrow-right" size="18px" color="#7e847b" custom-class="ml-auto" />
        </button>
        <button class="m-0 h-[89px] w-full flex items-center border-0 border-b border-[#e5e2df] bg-transparent px-4 text-left after:border-0">
          <view class="h-10 w-10 flex items-center justify-center rounded-full bg-[#f8faf7]">
            <wd-icon name="lock" size="22px" color="#59604f" />
          </view>
          <text class="ml-4 text-base text-[#1c1c1a] font-medium">
            隐私说明
          </text>
          <wd-icon name="arrow-right" size="18px" color="#7e847b" custom-class="ml-auto" />
        </button>
        <button class="m-0 h-[89px] w-full flex items-center border-0 bg-transparent px-4 text-left after:border-0">
          <view class="h-10 w-10 flex items-center justify-center rounded-full bg-[#f8faf7]">
            <wd-icon name="info-circle" size="22px" color="#59604f" />
          </view>
          <text class="ml-4 text-base text-[#1c1c1a] font-medium">
            关于
          </text>
          <wd-icon name="arrow-right" size="18px" color="#7e847b" custom-class="ml-auto" />
        </button>
      </view>
    </view>

    <AppBottomNav active="profile" />
  </view>
</template>
