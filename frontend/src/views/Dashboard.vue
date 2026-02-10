<template>
  <div class="dashboard">
    <!-- 余量卡片 -->
    <el-row :gutter="20">
      <el-col :xs="24" :sm="24" :md="12" :lg="12" v-if="latestRecord">
        <el-card class="balance-card" shadow="hover">
          <div class="balance-header">
            <div class="balance-icon ac-icon">
              <el-icon><WindPower /></el-icon>
            </div>
            <div class="balance-info">
              <div class="balance-label">空调余量</div>
              <div :class="['balance-value', getBalanceClass(latestRecord.kbalance || latestRecord.balance)]">
                {{ latestRecord.kbalance !== null && latestRecord.kbalance !== undefined ? latestRecord.kbalance.toFixed(2) : latestRecord.balance.toFixed(2) }} 度
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="12" v-if="latestRecord && latestRecord.zbalance !== null && latestRecord.zbalance !== undefined">
        <el-card class="balance-card" shadow="hover">
          <div class="balance-header">
            <div class="balance-icon light-icon">
              <el-icon><Sunny /></el-icon>
            </div>
            <div class="balance-info">
              <div class="balance-label">照明余量</div>
              <div :class="['balance-value', getBalanceClass(latestRecord.zbalance)]">
                {{ latestRecord.zbalance.toFixed(2) }} 度
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细信息卡片 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card class="dashboard-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                <el-icon class="title-icon"><InfoFilled /></el-icon>
                <span>详细信息</span>
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
          <div v-else-if="latestRecord" class="status-content">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="宿舍号">
                <el-tag type="info" size="large">{{ latestRecord.dorm_number }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="记录时间">
                <el-icon><Clock /></el-icon>
                <span style="margin-left: 5px;">{{ formatTime(latestRecord.record_time) }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="空调余量">
                <span :class="getBalanceClass(latestRecord.kbalance || latestRecord.balance)">
                  {{ latestRecord.kbalance !== null && latestRecord.kbalance !== undefined ? latestRecord.kbalance.toFixed(2) : latestRecord.balance.toFixed(2) }} 度
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="照明余量" v-if="latestRecord.zbalance !== null && latestRecord.zbalance !== undefined">
                <span :class="getBalanceClass(latestRecord.zbalance)">
                  {{ latestRecord.zbalance.toFixed(2) }} 度
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="用电量" v-if="latestRecord.power_consumption">
                <el-tag>{{ latestRecord.power_consumption }} 度</el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>
          <el-empty v-else description="暂无数据" :image-size="120">
            <el-button type="primary" @click="reloadData">立即获取数据</el-button>
          </el-empty>
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
import { usePowerStore } from '../stores/power'
import * as echarts from 'echarts'
import dayjs from 'dayjs'

const powerStore = usePowerStore()
const loading = ref(false)
const chartLoading = ref(false)
const reloading = ref(false)
const latestRecord = ref(null)
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
  await loadLatestRecord()
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

const loadLatestRecord = async () => {
  loading.value = true
  try {
    // 这里需要从配置或store获取宿舍号
    const dormNumber = powerStore.dormNumber || '320'
    const data = await getLatestRecord(dormNumber)
    latestRecord.value = data
  } catch (error) {
    // 如果是404错误（没有数据），不显示错误提示，只清空数据
    if (error.response?.status === 404) {
      latestRecord.value = null
      console.log('暂无电费记录数据')
    } else {
      ElMessage.error('获取数据失败：' + (error.response?.data?.detail || error.message))
    }
  } finally {
    loading.value = false
  }
}

const hasChartData = ref(false)

const loadChartData = async () => {
  chartLoading.value = true
  hasChartData.value = false
  try {
    const dormNumber = powerStore.dormNumber || '320'
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
