<script setup lang="ts">
import type { RecipeDetail } from '@/api/recipes/type'

definePage({
  name: 'recipe-share',
  style: {
    navigationStyle: 'custom',
  },
})

// 分享接口不在本次 CRUD 范围内，暂时保留原型页的展示数据。
const sharedRecipe: RecipeDetail = {
  id: 'preview',
  name: '三文鱼能量碗',
  cover_object_key: null,
  cover_url: '/static/images/recipe-soup.jpg',
  ingredients: ['三文鱼', '羽衣甘蓝', '彩椒', '牛油果', '鸡蛋', '菌菇'],
  steps: '1. 挖牛油果\n2. 煎三文鱼或空气炸锅\n3. 蔬菜烫熟炒制\n4. 加入酱油芥末搅拌',
  status: 'COMPLETED',
  usage_count: 0,
  created_at: '',
  updated_at: '',
}
</script>

<template>
  <RecipeDetailContent :recipe="sharedRecipe" shared />
</template>
