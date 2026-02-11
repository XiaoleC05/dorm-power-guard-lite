<template>
  <div class="dashboard">
    <!-- 多个宿舍信息卡片 -->
    <el-row :gutter="20" v-if="dormRecords.length > 0">
      <el-col 
        :xs="24" 
        :sm="12" 
        :md="8" 
        :lg="6" 
        v-for="record in dormRecords" 
        :key="record.dorm_number"
        style="margin-bottom: 20px;"
      >
        <el-card class="dorm-card" shadow="hover">
          <template #header>
            <div class="dorm-header">
              <el-tag type="info" size="large">{{ record.dorm_number }}</el-tag>
              <el-tag 
                :type="getDormStatusType(record)" 
                size="small"
                style="margin-left: 8px;"
              >
                {{ getDormStatusText(record) }}
              </el-tag>
            </div>
          </template>
          <div class="dorm-content">
            <div class="dorm-balance-item" v-if="record.kbalance !== null && record.kbalance !== undefined">
              <div class="balance-item-label">
                <el-icon><WindPower /></el-icon>
                <span>空调</span>
              </div>
              <div :class="['balance-item-value', getBalanceClass(record.kbalance)]">
                {{ record.kbalance.toFixed(2) }} 度
              </div>
            </div>
            <div class="dorm-balance-item" v-if="record.zbalance !== null && record.zbalance !== undefined">
              <div class="balance-item-label">
                <el-icon><Sunny /></el-icon>
                <span>照明</span>
              </div>
              <div :class="['balance-item-value', getBalanceClass(record.zbalance)]">
                {{ record.zbalance.toFixed(2) }} 度
              </div>
            </div>
            <div class="dorm-balance-item" v-if="record.kbalance === null && record.kbalance === undefined && record.balance !== null">
              <div class="balance-item-label">
                <el-icon><WindPower /></el-icon>
                <span>余量</span>
              </div>
              <div :class="['balance-item-value', getBalanceClass(record.balance)]">
                {{ record.balance.toFixed(2) }} 度
              </div>
            </div>
            <div class="dorm-time" v-if="record.record_time">
              <el-icon><Clock /></el-icon>
              <span>{{ formatTime(record.record_time) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 如果没有数据，显示空状态 -->
    <el-empty v-if="dormRecords.length === 0 && !loading" description="暂无宿舍数据" :image-size="120">
      <el-button type="primary" @click="reloadData">立即获取数据</el-button>
    </el-empty>

    <!-- 操作栏 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card class="dashboard-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <el-icon class="title-icon"><InfoFilled /></el-icon>
                <span>监控面板</span>
              </div>
              <div class="header-actions">
                <el-button type="success" size="default" @click="reloadData" :loading="reloading" :icon="Refresh">
                  重新获取
                </el-button>
                <el-button type="primary" size="default" @click="refreshData" :icon="Refresh" plain>
                  刷新显示
                </el-button>
              </div>
            </div>
          </template>
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else class="status-content">
            <el-alert
              v-if="dormRecords.length === 0"
              title="暂无数据"
              description="请先添加告警规则，系统将自动监控这些宿舍的电费信息"
              type="info"
              :closable="false"
              show-icon
            />
            <div v-else>
              <el-statistic-group>
                <el-statistic title="监控宿舍数" :value="dormRecords.length" />
                <el-statistic title="有数据宿舍" :value="dormRecords.filter(r => r !== null).length" />
              </el-statistic-group>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 趋势图表 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card class="dashboard-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <el-icon class="title-icon"><TrendCharts /></el-icon>
                <span>电费趋势</span>
              </div>
            </div>
          </template>
          <div v-if="chartLoading" class="loading-container">
            <el-skeleton :rows="5" animated />
          </div>
          <div v-else-if="hasChartData" ref="chartContainer" class="chart-container"></div>
          <el-empty v-else description="暂无图表数据" :image-size="100" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Refresh, 
  WindPower, 
  Sunny, 
  InfoFilled, 
  Clock, 
  TrendCharts 
} from '@element-plus/icons-vue'
import { getLatestRecord, getRecords } from '../api/power'
import { manualCrawl } from '../api/system'
import { getAllAlertRules } from '../api/alert'
import { usePowerStore } from '../stores/power'
import * as echarts from 'echarts'
import dayjs from 'dayjs'

const powerStore = usePowerStore()
const loading = ref(false)
const chartLoading = ref(false)
const reloading = ref(false)
const latestRecord = ref(null)
const dormRecords = ref([])
const chartContainer = ref(null)
let chartInstance = null

const balanceClass = computed(() => {
  if (!latestRecord.value) return ''
  const balance = latestRecord.value.kbalance !== null && latestRecord.value.kbalance !== undefined 
    ? latestRecord.value.kbalance 
    : latestRecord.value.balance
  if (balance < 10) return 'balance-low'
  if (balance < 20) return 'balance-warning'
  return 'balance-normal'
})

const getBalanceClass = (balance) => {
  if (balance === null || balance === undefined) return ''
  if (balance < 10) return 'balance-low'
  if (balance < 20) return 'balance-warning'
  return 'balance-normal'
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const refreshData = async () => {
  await loadDormRecords()
  await loadChartData()
}

const reloadData = async () => {
  reloading.value = true
  try {
    const response = await manualCrawl()
    // 响应拦截器已经返回了 response.data，所以直接使用 response
    if (response.success) {
      ElMessage.success(response.message || '数据获取成功')
      // 等待一秒后刷新显示，确保数据已保存
      setTimeout(async () => {
        await refreshData()
      }, 1000)
    } else {
      ElMessage.error(response.message || '数据获取失败')
    }
  } catch (error) {
    ElMessage.error('重新获取数据失败：' + (error.response?.data?.detail || error.response?.data?.message || error.message))
  } finally {
    reloading.value = false
  }
}

const loadDormRecords = async () => {
  loading.value = true
  try {
    // 获取所有告警规则中的宿舍号
    const rules = await getAllAlertRules()
    const enabledRules = rules.filter(rule => rule.enabled)
    
    if (enabledRules.length === 0) {
      dormRecords.value = []
      latestRecord.value = null
      loading.value = false
      return
    }
    
    // 获取每个宿舍的最新记录
    const records = await Promise.allSettled(
      enabledRules.map(rule => getLatestRecord(rule.dorm_number))
    )
    
    dormRecords.value = records
      .map((result, index) => {
        if (result.status === 'fulfilled') {
          return result.value
        } else {
          // 如果获取失败（404等），返回null但保留宿舍号信息
          return {
            dorm_number: enabledRules[index].dorm_number,
            record_time: null,
            kbalance: null,
            zbalance: null,
            balance: null
          }
        }
      })
      .filter(record => record !== null)
    
    // 保留第一个记录作为latestRecord（兼容旧代码）
    if (dormRecords.value.length > 0) {
      latestRecord.value = dormRecords.value[0]
    } else {
      latestRecord.value = null
    }
  } catch (error) {
    ElMessage.error('获取数据失败：' + (error.response?.data?.detail || error.message))
    dormRecords.value = []
    latestRecord.value = null
  } finally {
    loading.value = false
  }
}

const loadLatestRecord = async () => {
  // 兼容旧代码，现在使用loadDormRecords
  await loadDormRecords()
}

const hasChartData = ref(false)

const loadChartData = async () => {
  chartLoading.value = true
  hasChartData.value = false
  try {
    // 使用第一个有数据的宿舍号来显示图表
    const firstDorm = dormRecords.value.find(r => r && r.dorm_number)
    if (!firstDorm) {
      hasChartData.value = false
      chartLoading.value = false
      return
    }
    
    const dormNumber = firstDorm.dorm_number
    const records = await getRecords(dormNumber, 30)
    
    await nextTick()
    if (chartContainer.value && records.length > 0) {
      initChart(records)
      hasChartData.value = true
    } else if (records.length === 0) {
      hasChartData.value = false
      console.log('暂无图表数据')
    }
  } catch (error) {
    hasChartData.value = false
    // 如果是404或其他错误，不显示错误提示
    if (error.response?.status !== 404) {
      ElMessage.error('加载图表数据失败：' + (error.response?.data?.detail || error.message))
    }
  } finally {
    chartLoading.value = false
  }
}

const getDormStatusType = (record) => {
  if (!record || !record.record_time) return 'info'
  const kbalance = record.kbalance !== null && record.kbalance !== undefined ? record.kbalance : record.balance
  const zbalance = record.zbalance
  const minBalance = Math.min(
    kbalance !== null && kbalance !== undefined ? kbalance : Infinity,
    zbalance !== null && zbalance !== undefined ? zbalance : Infinity
  )
  if (minBalance < 10) return 'danger'
  if (minBalance < 20) return 'warning'
  return 'success'
}

const getDormStatusText = (record) => {
  if (!record || !record.record_time) return '无数据'
  const kbalance = record.kbalance !== null && record.kbalance !== undefined ? record.kbalance : record.balance
  const zbalance = record.zbalance
  const minBalance = Math.min(
    kbalance !== null && kbalance !== undefined ? kbalance : Infinity,
    zbalance !== null && zbalance !== undefined ? zbalance : Infinity
  )
  if (minBalance < 10) return '低电量'
  if (minBalance < 20) return '警告'
  return '正常'
}

const initChart = (records) => {
  if (!chartContainer.value) return
  
  if (!chartInstance) {
    chartInstance = echarts.init(chartContainer.value)
  }
  
  const dates = records.map(r => dayjs(r.record_time).format('MM-DD HH:mm')).reverse()
  
  // 提取空调余量和照明余量
  const kbalances = records.map(r => r.kbalance !== null && r.kbalance !== undefined ? r.kbalance : r.balance).reverse()
  const zbalances = records.map(r => r.zbalance !== null && r.zbalance !== undefined ? r.zbalance : null).reverse()
  
  // 检查是否有照明余量数据
  const hasZBalance = zbalances.some(b => b !== null)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(50, 50, 50, 0.9)',
      borderColor: '#667eea',
      borderWidth: 1,
      textStyle: {
        color: '#fff'
      },
      formatter: (params) => {
        let result = `<div style="font-weight: bold; margin-bottom: 5px;">${params[0].name}</div>`
        params.forEach(param => {
          const color = param.color
          result += `<div style="margin: 3px 0;">
            <span style="display: inline-block; width: 10px; height: 10px; background: ${color}; border-radius: 50%; margin-right: 5px;"></span>
            ${param.seriesName}: <span style="font-weight: bold;">${param.value.toFixed(2)} 度</span>
          </div>`
        })
        return result
      }
    },
    legend: {
      data: hasZBalance ? ['空调余量', '照明余量'] : ['空调余量'],
      top: 10,
      textStyle: {
        fontSize: 12
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45,
        fontSize: 11
      },
      axisLine: {
        lineStyle: {
          color: '#e0e0e0'
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '余量（度）',
      nameTextStyle: {
        fontSize: 12
      },
      axisLabel: {
        formatter: '{value}'
      },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#e0e0e0'
        }
      }
    },
    series: [
      {
        name: '空调余量',
        data: kbalances,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
              { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
            ]
          }
        },
        lineStyle: {
          color: '#667eea',
          width: 2
        },
        itemStyle: {
          color: '#667eea',
          borderColor: '#fff',
          borderWidth: 2
        }
      }
    ]
  }
  
  // 如果有照明余量数据，添加照明余量系列
  if (hasZBalance) {
    option.series.push({
      name: '照明余量',
      data: zbalances,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
          ]
        }
      },
      lineStyle: {
        color: '#67c23a',
        width: 2
      },
      itemStyle: {
        color: '#67c23a',
        borderColor: '#fff',
        borderWidth: 2
      }
    })
  }
  
  chartInstance.setOption(option, true)
  
  // 响应式调整
  const resizeHandler = () => {
    chartInstance?.resize()
  }
  window.addEventListener('resize', resizeHandler)
  
  // 组件卸载时移除监听器
  onMounted(() => {
    return () => {
      window.removeEventListener('resize', resizeHandler)
    }
  })
}

onMounted(async () => {
  await refreshData()
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
}

.dashboard-card {
  margin-bottom: 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.dashboard-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.header-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.title-icon {
  margin-right: 8px;
  font-size: 18px;
  color: #667eea;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.loading-container {
  padding: 40px 20px;
}

.status-content {
  padding: 10px;
}

/* 余量卡片样式 */
.balance-card {
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  border: none;
}

.balance-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.balance-header {
  display: flex;
  align-items: center;
  padding: 10px;
}

.balance-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin-right: 20px;
  flex-shrink: 0;
}

.ac-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.light-icon {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  color: white;
}

.balance-info {
  flex: 1;
}

.balance-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.balance-value {
  font-size: 32px;
  font-weight: bold;
  line-height: 1.2;
  font-family: 'Arial', sans-serif;
}

.balance-low {
  color: #f56c6c;
}

.balance-warning {
  color: #e6a23c;
}

.balance-normal {
  color: #67c23a;
}

/* 图表容器 */
.chart-container {
  height: 450px;
  width: 100%;
  min-height: 300px;
}

/* 宿舍卡片样式 */
.dorm-card {
  margin-bottom: 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.dorm-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.dorm-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.dorm-content {
  padding: 10px 0;
}

.dorm-balance-item {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.dorm-balance-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.balance-item-label {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.balance-item-label .el-icon {
  margin-right: 5px;
}

.balance-item-value {
  font-size: 24px;
  font-weight: bold;
  line-height: 1.2;
}

.dorm-time {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #909399;
  margin-top: 10px;
}

.dorm-time .el-icon {
  margin-right: 5px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard {
    padding: 0 10px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .balance-value {
    font-size: 24px;
  }
  
  .balance-icon {
    width: 50px;
    height: 50px;
    font-size: 24px;
    margin-right: 15px;
  }
  
  .chart-container {
    height: 350px;
  }
  
  .dorm-balance-item {
    margin-bottom: 12px;
    padding-bottom: 12px;
  }
  
  .balance-item-value {
    font-size: 20px;
  }
}

/* 描述列表优化 */
:deep(.el-descriptions__label) {
  font-weight: 600;
  color: #606266;
}

:deep(.el-descriptions__content) {
  color: #303133;
}

/* 标签样式 */
:deep(.el-tag) {
  font-weight: 500;
}
</style>
