# 前端组件目录

本目录用于存放可复用的Vue组件。

## 目录结构

```
components/
├── README.md          # 本说明文件
└── (未来可添加的组件)
    ├── PowerCard.vue      # 电费卡片组件
    ├── AlertRuleForm.vue  # 告警规则表单组件
    └── ...
```

## 组件开发规范

1. **命名规范**: 使用PascalCase命名（如：`PowerCard.vue`）
2. **组件结构**: 遵循Vue 3 Composition API规范
3. **Props定义**: 使用TypeScript类型或PropTypes定义
4. **文档**: 每个组件应包含使用说明

## 使用示例

```vue
<script setup>
import PowerCard from '@/components/PowerCard.vue'
</script>

<template>
  <PowerCard :dorm-number="320" />
</template>
```
