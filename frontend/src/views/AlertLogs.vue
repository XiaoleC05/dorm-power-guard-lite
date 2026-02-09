<template>
  <div class="alert-logs-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>告警日志</span>
          <el-button type="primary" @click="loadLogs">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <el-table :data="logs" v-loading="loading" stripe>
        <el-table-column prop="dorm_number" label="宿舍号" width="120" />
        <el-table-column prop="balance" label="余额（元）" width="120" />
        <el-table-column prop="threshold" label="阈值（元）" width="120" />
        <el-table-column prop="alert_type" label="告警类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.alert_type === 'email' ? 'primary' : 'success'">
              {{ row.alert_type === 'email' ? '邮件' : 'QQ' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="alert_status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.alert_status === 'success' ? 'success' : 'danger'">
              {{ row.alert_status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="alert_message" label="消息" show-overflow-tooltip />
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getAlertLogs } from '../api/alert'
import dayjs from 'dayjs'

const loading = ref(false)
const logs = ref([])

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const loadLogs = async () => {
  loading.value = true
  try {
    const data = await getAlertLogs(null, 100)
    logs.value = data
  } catch (error) {
    ElMessage.error('加载日志失败：' + error.message)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.alert-logs-page {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
