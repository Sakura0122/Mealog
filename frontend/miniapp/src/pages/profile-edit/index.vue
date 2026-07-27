<script setup lang="ts">
import type { UserProfile } from '@/api/users/type'
import { fileApi } from '@/api/files'
import { userApi } from '@/api/users'
import { getErrorMessage } from '@/utils/request'

definePage({
  name: 'profile-edit',
  style: {
    navigationStyle: 'custom',
  },
})

const profile = ref<UserProfile>()
const nickname = ref('')
const avatarObjectKey = ref<string | null>(null)
const avatarPreviewUrl = ref('')
const pendingAvatarPath = ref('')

const loading = ref(false)
const loadError = ref('')
const loadProfile = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const data = await userApi.profile()
    profile.value = data
    nickname.value = data.nickname ?? ''
    avatarObjectKey.value = data.avatar_object_key
    avatarPreviewUrl.value = data.avatar_url ?? ''
  }
  catch (error) {
    loadError.value = getErrorMessage(error)
  }
  finally {
    loading.value = false
  }
}
onLoad(loadProfile)

interface ChooseAvatarEvent {
  detail: {
    avatarUrl: string
  }
}

// 微信返回的是临时头像路径，保存资料前需先上传并换成对象存储键。
const chooseAvatar = (event: ChooseAvatarEvent) => {
  pendingAvatarPath.value = event.detail.avatarUrl
  avatarPreviewUrl.value = event.detail.avatarUrl
}

const saving = ref(false)
const saveProfile = async () => {
  const trimmedNickname = nickname.value.trim()
  if (!trimmedNickname) {
    useGlobalToast().warning('请输入昵称')
    return
  }

  saving.value = true
  try {
    let avatarKey = avatarObjectKey.value
    if (pendingAvatarPath.value) {
      const uploadedAvatar = await fileApi.uploadAvatar(pendingAvatarPath.value)
      avatarKey = uploadedAvatar.object_key
    }

    await userApi.updateProfile({
      nickname: trimmedNickname,
      avatar_object_key: avatarKey,
    })
    uni.navigateBack({
      success: () => useGlobalToast().success('个人信息已更新'),
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
  <view class="min-h-screen bg-[#f8fafc] pb-8">
    <AppTopBar />

    <view class="px-5">
      <text class="block text-2xl text-[#1c1c1a] font-semibold">
        个人信息
      </text>

      <view v-if="loading" class="h-80 flex items-center justify-center">
        <wd-loading text="加载个人信息" color="#71836b" />
      </view>

      <view v-else-if="loadError" class="py-20 text-center">
        <wd-empty icon="warning" :tip="loadError" />
        <button class="mx-auto mt-4 border-0 rounded-full bg-[#d5e8cb] px-6 py-2 text-sm text-[#24331f] after:border-0" @click="loadProfile">
          重新加载
        </button>
      </view>

      <template v-else-if="profile">
        <view class="mt-10 flex flex-col items-center">
          <button open-type="chooseAvatar" class="relative m-0 h-28 w-28 overflow-hidden border-0 rounded-full bg-[#edf1ea] p-0 after:border-0" @chooseavatar="chooseAvatar">
            <image :src="avatarPreviewUrl || '/static/images/profile-avatar.jpg'" mode="aspectFill" class="h-full w-full" />
            <view class="absolute inset-x-0 bottom-0 h-8 flex items-center justify-center bg-black/45">
              <wd-icon name="camera" size="17px" color="#ffffff" />
            </view>
          </button>
        </view>

        <view class="mt-10 border border-[#e5e2df] rounded-lg bg-white px-4">
          <view class="h-16 flex items-center">
            <text class="w-20 text-base text-[#4f564c]">
              昵称
            </text>
            <input v-model="nickname" type="nickname" maxlength="64" class="min-w-0 flex-1 text-right text-base text-[#1c1c1a]" placeholder="请输入昵称" placeholder-class="text-[#a9ada7]">
          </view>
        </view>

        <button :disabled="saving" class="mt-8 h-14 w-full flex items-center justify-center border-0 rounded-full bg-[#d5e8cb] text-base text-[#24331f] font-medium after:border-0 disabled:opacity-60" @click="saveProfile">
          <wd-loading v-if="saving" size="20px" color="#24331f" />
          <text :class="saving ? 'ml-2' : ''">
            {{ saving ? '保存中' : '保存' }}
          </text>
        </button>
      </template>
    </view>
  </view>
</template>
