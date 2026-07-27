<script setup lang="ts">
definePage({
  name: 'privacy',
  style: {
    navigationStyle: 'custom',
  },
})
</script>

<template>
  <view class="min-h-screen bg-[#f8fafc] pb-12">
    <AppTopBar />

    <view class="px-5">
      <view class="mt-5">
        <view class="h-12 w-12 flex items-center justify-center rounded-full bg-[#e5f0df]">
          <wd-icon name="lock" size="25px" color="#52634c" />
        </view>
        <text class="mt-5 block text-3xl text-[#1c1c1a] font-semibold leading-10">
          隐私说明
        </text>
        <text class="mt-2 block text-sm text-[#7a8177] leading-6">
          更新日期：2026 年 7 月 27 日
        </text>
        <text class="mt-5 block text-base text-[#4f554d] leading-7">
          Mealog 重视你的个人信息与使用感受。以下内容说明我们在提供饮食记录服务时，会处理哪些信息，以及这些信息的用途。
        </text>
      </view>

      <!-- 各章节与实际业务数据逐项对应，避免对尚未提供的能力作额外承诺。 -->
      <view class="mt-10 border-t border-[#e1e5df] py-7">
        <view class="flex items-start">
          <text class="w-9 shrink-0 text-sm text-[#71836b] font-semibold leading-7">
            01
          </text>
          <view class="min-w-0 flex-1">
            <text class="block text-lg text-[#20251e] font-semibold leading-7">
              我们收集的信息
            </text>
            <text class="mt-3 block text-[15px] text-[#565d54] leading-7">
              为完成微信登录，我们会处理微信提供的用户标识。你主动设置个人资料时，我们会保存昵称和头像。
            </text>
            <text class="mt-3 block text-[15px] text-[#565d54] leading-7">
              你创建饮食记录或菜谱时，我们会保存你填写的用餐时间、来源、店铺、菜品、备注、食材、步骤和上传的图片。
            </text>
          </view>
        </view>
      </view>

      <view class="border-t border-[#e1e5df] py-7">
        <view class="flex items-start">
          <text class="w-9 shrink-0 text-sm text-[#71836b] font-semibold leading-7">
            02
          </text>
          <view class="min-w-0 flex-1">
            <text class="block text-lg text-[#20251e] font-semibold leading-7">
              权限使用
            </text>
            <text class="mt-3 block text-[15px] text-[#565d54] leading-7">
              仅当你主动拍摄或选择图片时，我们才会使用相机或相册能力；仅当你主动从地图选择店铺时，我们才会使用位置选择能力。
            </text>
            <text class="mt-3 block text-[15px] text-[#565d54] leading-7">
              拒绝相关授权不会影响其他功能，你仍可手动填写不依赖该权限的内容。
            </text>
          </view>
        </view>
      </view>

      <view class="border-t border-[#e1e5df] py-7">
        <view class="flex items-start">
          <text class="w-9 shrink-0 text-sm text-[#71836b] font-semibold leading-7">
            03
          </text>
          <view class="min-w-0 flex-1">
            <text class="block text-lg text-[#20251e] font-semibold leading-7">
              信息如何使用
            </text>
            <text class="mt-3 block text-[15px] text-[#565d54] leading-7">
              这些信息用于登录识别、展示个人资料、保存和回顾饮食记录、管理个人菜谱，以及呈现你主动生成的菜谱分享内容。
            </text>
            <text class="mt-3 block text-[15px] text-[#565d54] leading-7">
              我们不会将你的个人信息用于与上述服务无关的用途，也不会出售你的个人信息。
            </text>
          </view>
        </view>
      </view>

      <view class="border-t border-[#e1e5df] py-7">
        <view class="flex items-start">
          <text class="w-9 shrink-0 text-sm text-[#71836b] font-semibold leading-7">
            04
          </text>
          <view class="min-w-0 flex-1">
            <text class="block text-lg text-[#20251e] font-semibold leading-7">
              存储与保护
            </text>
            <text class="mt-3 block text-[15px] text-[#565d54] leading-7">
              登录凭证会保存在你的设备本地，用于保持登录状态；业务数据和上传图片会存储在服务端及对象存储中。
            </text>
            <text class="mt-3 block text-[15px] text-[#565d54] leading-7">
              我们会采取合理措施保护信息安全，并仅在实现服务所需的期限内保留相关信息。
            </text>
          </view>
        </view>
      </view>

      <view class="border-y border-[#e1e5df] py-7">
        <view class="flex items-start">
          <text class="w-9 shrink-0 text-sm text-[#71836b] font-semibold leading-7">
            05
          </text>
          <view class="min-w-0 flex-1">
            <text class="block text-lg text-[#20251e] font-semibold leading-7">
              你的选择
            </text>
            <text class="mt-3 block text-[15px] text-[#565d54] leading-7">
              你可以在小程序内修改昵称和头像，也可以编辑或删除自己创建的饮食记录。系统权限可随时在微信的小程序设置中调整。
            </text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>
