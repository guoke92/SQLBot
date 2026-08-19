<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import {
  knowledgeApi,
  type KnowledgeDeployment,
  type KnowledgeUnitPage,
  type PageResult,
} from '@/api/knowledge'
import KnowledgePackageWorkbench from './components/KnowledgePackageWorkbench.vue'
import KnowledgeReviewCenter from './components/KnowledgeReviewCenter.vue'
import RuntimeKnowledgeList from './components/RuntimeKnowledgeList.vue'

type RuntimeDeployment = KnowledgeDeployment & {
  unit_id: number
  unit_key: string
  unit_title: string
  unit_domain: string
  revision: number
  datasource_id: number
  binding_status: string
}

const activeTab = ref('reviews')
const loading = ref(false)
const reviewPage = ref<KnowledgeUnitPage | null>(null)
const runtimePage = ref<PageResult<RuntimeDeployment> | null>(null)
const lastReviewQuery = ref({
  keyword: '',
  lifecycle: 'IN_REVIEW',
  validation: '',
  page: 1,
  pageSize: 15,
})

async function loadReviews(query = lastReviewQuery.value) {
  lastReviewQuery.value = { ...query }
  loading.value = true
  try {
    reviewPage.value = (await knowledgeApi.getUnits({
      keyword: query.keyword || undefined,
      lifecycle: query.lifecycle || undefined,
      validation: query.validation || undefined,
      page: query.page,
      page_size: query.pageSize,
    })) as KnowledgeUnitPage
  } finally {
    loading.value = false
  }
}

async function loadRuntime(query = { status: 'ACTIVE', page: 1, pageSize: 15 }) {
  loading.value = true
  try {
    runtimePage.value = (await knowledgeApi.getDeployments({
      status: query.status || undefined,
      page: query.page,
      page_size: query.pageSize,
    })) as PageResult<RuntimeDeployment>
  } finally {
    loading.value = false
  }
}

function onTabChange(name: string | number) {
  if (name === 'reviews') void loadReviews(lastReviewQuery.value)
  if (name === 'runtime') void loadRuntime()
}

onMounted(() => void loadReviews())
</script>

<template>
  <main class="knowledge-page">
    <el-tabs v-model="activeTab" class="knowledge-tabs" @tab-change="onTabChange">
      <el-tab-pane label="审核中心" name="reviews">
        <KnowledgeReviewCenter :page="reviewPage" :loading="loading" @load="loadReviews" />
      </el-tab-pane>
      <el-tab-pane label="运行时知识" name="runtime">
        <RuntimeKnowledgeList :page="runtimePage" :loading="loading" @load="loadRuntime" />
      </el-tab-pane>
      <el-tab-pane label="知识包" name="packages" lazy>
        <KnowledgePackageWorkbench />
      </el-tab-pane>
    </el-tabs>
  </main>
</template>

<style scoped>
.knowledge-page {
  width: 100%;
  min-height: 100%;
  padding: 16px 24px 24px;
  box-sizing: border-box;
  background: var(--el-bg-color);
}

.knowledge-tabs :deep(.el-tabs__header) {
  margin-bottom: 18px;
}

.knowledge-tabs :deep(.el-tabs__item) {
  height: 46px;
  padding: 0 22px;
  font-size: 16px;
  font-weight: 600;
}

@media (max-width: 760px) {
  .knowledge-page {
    padding: 10px 12px 18px;
  }

  .knowledge-tabs :deep(.el-tabs__item) {
    padding: 0 12px;
  }
}
</style>
