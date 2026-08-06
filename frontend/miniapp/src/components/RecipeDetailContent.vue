<script setup lang="ts">
import type { RecipeShareDetail } from '@/api/recipes/type'

withDefaults(defineProps<{
  recipe: RecipeShareDetail
  shared?: boolean
  actionLabel?: string
  actionOpenType?: 'share'
}>(), {
  shared: false,
  actionLabel: '',
  actionOpenType: undefined,
})

const emit = defineEmits<{
  action: []
  edit: []
}>()
</script>

<template>
  <view class="min-h-screen bg-[#fcf9f6] pb-8">
    <!-- 分享预览没有返回入口，保留关闭按钮；普通详情页避免与返回按钮重复。 -->
    <AppTopBar :show-back="!shared" :edit="!shared" :close="shared" @edit="emit('edit')" />

    <view class="mx-auto mt-3 w-[280px] rotate-1 bg-white p-3 pb-8 shadow-[0_5px_12px_rgba(0,0,0,0.12)]">
      <image v-if="recipe.cover_url" :src="recipe.cover_url" mode="aspectFill" class="h-[256px] w-full" />
      <view v-else class="h-[256px] w-full flex flex-col items-center justify-center bg-[#e5e3e0] text-[#4f5650]">
        <wd-icon name="book" size="42px" color="#4f5650" />
        <text class="mt-2 text-xs">
          暂无封面
        </text>
      </view>
      <text class="mx-auto mt-4 block w-max bg-[#dbe4d5] px-4 py-1 text-[10px] text-[#475244] shadow-sm">
        菜谱时刻
      </text>
    </view>

    <view class="mx-5 mt-6 overflow-hidden border border-[#e5e2df] rounded-3xl bg-white shadow-[0_8px_18px_rgba(0,0,0,0.06)]">
      <view class="min-h-[57px] flex items-center border-b border-[#ebe8e4] px-5 py-3">
        <wd-icon name="book" size="18px" color="#5c6949" />
        <text class="ml-4 min-w-0 flex-1 break-words text-base text-[#52634c] font-medium">
          {{ recipe.name }}
        </text>
      </view>
      <view class="min-h-[52px] flex items-start border-b border-[#ebe8e4] px-5 py-3">
        <wd-icon name="list" size="18px" color="#777a77" custom-class="mt-1" />
        <view v-if="recipe.ingredients.length" class="ml-3 min-w-0 flex flex-1 flex-wrap gap-1">
          <text v-for="(item, index) in recipe.ingredients" :key="`${index}-${item}`" class="max-w-full break-words rounded-full bg-[#e1e6c2] px-2 py-1 text-[10px] text-[#59624d]">
            {{ item }}
          </text>
        </view>
        <text v-else class="ml-3 text-sm text-[#a4a59f]">
          暂未填写食材
        </text>
      </view>
      <view class="min-h-[112px] flex items-start px-5 py-4">
        <wd-icon name="file" size="18px" color="#777a77" custom-class="mt-1" />
        <text v-if="recipe.steps" class="ml-3 min-w-0 flex-1 whitespace-pre-wrap break-words text-sm text-[#4e5848] leading-6">
          {{ recipe.steps }}
        </text>
        <text v-else class="ml-3 text-sm text-[#a4a59f]">
          暂未填写制作步骤
        </text>
      </view>
    </view>

    <button :open-type="actionOpenType" class="mx-5 mt-6 h-14 flex items-center justify-center border-0 rounded-full text-base font-medium shadow-[0_6px_12px_rgba(0,0,0,0.1)] after:border-0" :class="shared ? 'bg-[#d5e8cb] text-[#24331f]' : 'bg-[#ffd29a] text-[#343021]'" @click="emit('action')">
      {{ actionLabel || (shared ? '保存至我的菜谱' : '分享我的菜谱') }}
    </button>
    <slot />
  </view>
</template>
