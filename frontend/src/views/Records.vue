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
        <el-table-column prop="dorm_number" label="宿舍号" width="100" fixed="left" />
        <el-table-column prop="record_time" label="记录时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.record_time) }}
          </template>
        </el-table-column>
        <el-table-column label="空调" width="150">
          <el-table-column prop="kbalance" label="余量（度）" width="120">
            <template #default="{ row }">
              <span :class="getBalanceClass(row.kbalance || row.balance)">
                {{ row.kbalance !== null && row.kbalance !== undefined ? row.kbalance.toFixed(2) : (row.balance ? row.balance.toFixed(2) : '-') }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="kpower_consumption" label="用电量（度）" width="120">
            <template #default="{ row }">
              <span v-if="row.kpower_consumption !== null && row.kpower_consumption !== undefined">
                {{ row.kpower_consumption > 0 ? '+' : '' }}{{ row.kpower_consumption.toFixed(2) }}
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
        </el-table-column>
        <el-table-column label="照明" width="150">
          <el-table-column prop="zbalance" label="余量（度）" width="120">
            <template #default="{ row }">
              <span v-if="row.zbalance !== null && row.zbalance !== undefined" :class="getBalanceClass(row.zbalance)">
                {{ row.zbalance.toFixed(2) }}
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="zpower_consumption" label="用电量（度）" width="120">
            <template #default="{ row }">
              <span v-if="row.zpower_consumption !== null && row.zpower_consumption !== undefined">
                {{ row.zpower_consumption > 0 ? '+' : '' }}{{ row.zpower_consumption.toFixed(2) }}
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
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
import { getConfig } from '../api/system'
import dayjs from 'dayjs'

const loading = ref(false)
const records = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dormNumber = ref(null)

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const getBalanceClass = (balance) => {
  if (balance === null || balance === undefined) return ''
  if (balance < 10) return 'balance-low'
  if (balance < 20) return 'balance-warning'
  return 'balance-normal'
}

const loadRecords = async () => {
  if (!dormNumber.value) {
    ElMessage.warning('未配置宿舍号')
    return
  }
  
  loading.value = true
  try {
    const data = await getRecords(dormNumber.value, pageSize.value)
    records.value = data
    total.value = data.length
  } catch (error) {
    if (error.response?.status !== 404) {
      ElMessage.error('加载记录失败：' + (error.response?.data?.detail || error.message))
    }
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  // 获取配置中的宿舍号
  try {
    const config = await getConfig()
    dormNumber.value = config.dorm_number
    await loadRecords()
  } catch (error) {
    ElMessage.error('获取配置失败：' + (error.response?.data?.detail || error.message))
  }
})
</script>

<style scoped>
.records-page {
  max-width: 1400px;
  margin: 0 auto;
}

.records-page :deep(.el-card) {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
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
