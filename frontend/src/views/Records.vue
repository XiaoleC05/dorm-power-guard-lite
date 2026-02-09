<template>
  <div class="records-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>电费记录</span>
          <el-button type="primary" @click="loadRecords">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <el-table :data="records" v-loading="loading" stripe>
        <el-table-column prop="dorm_number" label="宿舍号" width="120" />
        <el-table-column prop="balance" label="余额（元）" width="120">
          <template #default="{ row }">
            <span :class="getBalanceClass(row.balance)">{{ row.balance }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="power_consumption" label="用电量（度）" width="120" />
        <el-table-column prop="record_time" label="记录时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.record_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadRecords"
        @current-change="loadRecords"
        style="margin-top: 20px"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getRecords } from '../api/power'
import { usePowerStore } from '../stores/power'
import dayjs from 'dayjs'

const powerStore = usePowerStore()
const loading = ref(false)
const records = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const getBalanceClass = (balance) => {
  if (balance < 10) return 'balance-low'
  if (balance < 20) return 'balance-warning'
  return 'balance-normal'
}

const loadRecords = async () => {
  loading.value = true
  try {
    const dormNumber = powerStore.dormNumber || '101'
    const data = await getRecords(dormNumber, pageSize.value)
    records.value = data
    total.value = data.length
  } catch (error) {
    ElMessage.error('加载记录失败：' + error.message)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRecords()
})
</script>

<style scoped>
.records-page {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.balance-low {
  color: #f56c6c;
  font-weight: bold;
}

.balance-warning {
  color: #e6a23c;
  font-weight: bold;
}

.balance-normal {
  color: #67c23a;
}
</style>
