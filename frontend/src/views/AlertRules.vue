<template>
  <div class="alert-rules-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>告警规则</span>
          <el-button type="primary" @click="showDialog = true">
            <el-icon><Plus /></el-icon>
            新增规则
          </el-button>
        </div>
      </template>
      
      <el-table :data="rules" v-loading="loading" stripe>
        <el-table-column prop="dorm_number" label="宿舍号" width="120" />
        <el-table-column prop="kthreshold" label="空调阈值（度）" width="150">
          <template #default="{ row }">
            <span v-if="row.kthreshold !== null && row.kthreshold !== undefined">
              {{ row.kthreshold.toFixed(2) }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="zthreshold" label="照明阈值（度）" width="150">
          <template #default="{ row }">
            <span v-if="row.zthreshold !== null && row.zthreshold !== undefined">
              {{ row.zthreshold.toFixed(2) }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="启用状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="email_enabled" label="邮件告警" width="120">
          <template #default="{ row }">
            <div>
              <el-tag :type="row.email_enabled ? 'success' : 'info'" style="margin-bottom: 5px; display: block;">
                {{ row.email_enabled ? '启用' : '禁用' }}
              </el-tag>
              <span v-if="row.email_enabled && row.email_address" style="font-size: 12px; color: #909399;">
                {{ row.email_address }}
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="qq_enabled" label="QQ告警" width="100">
          <template #default="{ row }">
            <el-tag :type="row.qq_enabled ? 'success' : 'info'">
              {{ row.qq_enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_alert_time" label="最后告警时间" width="180">
          <template #default="{ row }">
            {{ row.last_alert_time ? formatTime(row.last_alert_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="editRule(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteRule(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="editingRule ? '编辑告警规则' : '新增告警规则'"
      width="500px"
    >
      <el-form :model="ruleForm" label-width="140px" :rules="formRules" ref="formRef">
        <el-form-item label="宿舍号">
          <el-input v-model="ruleForm.dorm_number" :disabled="!!editingRule" />
        </el-form-item>
        <el-form-item label="空调告警阈值（度）">
          <el-input-number v-model="ruleForm.kthreshold" :min="0" :precision="2" style="width: 100%" />
          <div style="font-size: 12px; color: #909399; margin-top: 5px;">
            当空调余量低于此值时触发告警
          </div>
        </el-form-item>
        <el-form-item label="照明告警阈值（度）">
          <el-input-number v-model="ruleForm.zthreshold" :min="0" :precision="2" style="width: 100%" />
          <div style="font-size: 12px; color: #909399; margin-top: 5px;">
            当照明余量低于此值时触发告警
          </div>
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="ruleForm.enabled" />
        </el-form-item>
        <el-form-item label="邮件告警">
          <el-switch v-model="ruleForm.email_enabled" />
        </el-form-item>
        <el-form-item 
          label="接收邮箱" 
          v-if="ruleForm.email_enabled"
          prop="email_address"
        >
          <el-input 
            v-model="ruleForm.email_address" 
            placeholder="请输入接收告警邮件的邮箱地址，多个邮箱用逗号分隔"
            type="textarea"
            :rows="2"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 5px;">
            多个邮箱地址请用逗号（,）分隔
          </div>
        </el-form-item>
        <el-form-item label="QQ告警">
          <el-switch v-model="ruleForm.qq_enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveRule">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getAllAlertRules, createAlertRule, updateAlertRule, deleteAlertRule } from '../api/alert'
import dayjs from 'dayjs'

const loading = ref(false)
const rules = ref([])
const showDialog = ref(false)
const editingRule = ref(null)
const ruleForm = ref({
  dorm_number: '',
  kthreshold: 20.0,
  zthreshold: 20.0,
  threshold: null,
  enabled: true,
  email_enabled: false,
  email_address: '',
  qq_enabled: false
})

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const loadRules = async () => {
  loading.value = true
  try {
    const data = await getAllAlertRules()
    // 确保email_address字段存在，处理null和undefined值
    rules.value = data.map(rule => {
      // 处理email_address字段，将null/undefined转换为空字符串
      const emailAddress = (rule.email_address !== null && 
                            rule.email_address !== undefined && 
                            rule.email_address !== '') 
        ? String(rule.email_address).trim() 
        : ''
      return {
        ...rule,
        email_address: emailAddress
      }
    })
  } catch (error) {
    ElMessage.error('加载规则失败：' + error.message)
  } finally {
    loading.value = false
  }
}

const formRef = ref(null)

const formRules = {
  email_address: [
    { 
      validator: (rule, value, callback) => {
        if (ruleForm.value.email_enabled) {
          if (!value || !value.trim()) {
            callback(new Error('启用邮件告警时必须输入接收邮箱地址'))
          } else {
            // 验证邮箱格式（支持多个邮箱，用逗号分隔）
            const emails = value.split(',').map(e => e.trim()).filter(e => e)
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
            for (const email of emails) {
              if (!emailRegex.test(email)) {
                callback(new Error(`邮箱格式不正确: ${email}`))
                return
              }
            }
            callback()
          }
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const editRule = async (rule) => {
  editingRule.value = rule
  
  // 确保email_address字段存在，处理null、undefined和空字符串
  // 注意：API返回的null可能在前端显示为undefined或null，需要统一处理
  let emailAddress = ''
  if (rule.email_address !== null && 
      rule.email_address !== undefined && 
      rule.email_address !== '') {
    const emailStr = String(rule.email_address).trim()
    if (emailStr !== '' && emailStr !== 'null' && emailStr !== 'undefined') {
      emailAddress = emailStr
    }
  }
  
  // 重新创建表单对象，确保响应式更新
  ruleForm.value = {
    dorm_number: rule.dorm_number || '',
    kthreshold: rule.kthreshold !== null && rule.kthreshold !== undefined ? rule.kthreshold : 20.0,
    zthreshold: rule.zthreshold !== null && rule.zthreshold !== undefined ? rule.zthreshold : 20.0,
    threshold: rule.threshold,
    enabled: rule.enabled !== null && rule.enabled !== undefined ? rule.enabled : true,
    email_enabled: rule.email_enabled !== null && rule.email_enabled !== undefined ? rule.email_enabled : false,
    email_address: emailAddress,
    qq_enabled: rule.qq_enabled !== null && rule.qq_enabled !== undefined ? rule.qq_enabled : false
  }
  
  showDialog.value = true
  
  // 使用nextTick确保DOM更新后再清除验证
  await nextTick()
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const saveRule = async () => {
  // 表单验证
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    // 如果禁用邮件告警，清空邮箱地址
    if (!ruleForm.value.email_enabled) {
      ruleForm.value.email_address = ''
    }
    
    if (editingRule.value) {
      await updateAlertRule(editingRule.value.dorm_number, ruleForm.value)
      ElMessage.success('更新成功')
    } else {
      await createAlertRule(ruleForm.value)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    editingRule.value = null
    ruleForm.value = {
      dorm_number: '',
      kthreshold: 20.0,
      zthreshold: 20.0,
      threshold: null,
      enabled: true,
      email_enabled: false,
      email_address: '',
      qq_enabled: false
    }
    if (formRef.value) {
      formRef.value.clearValidate()
    }
    await loadRules()
  } catch (error) {
    if (error !== false) { // 表单验证失败时error为false
      ElMessage.error('保存失败：' + (error.message || error))
    }
  }
}

const deleteRule = async (rule) => {
  try {
    await ElMessageBox.confirm('确定要删除这条规则吗？', '提示', {
      type: 'warning'
    })
    await deleteAlertRule(rule.dorm_number)
    ElMessage.success('删除成功')
    await loadRules()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + error.message)
    }
  }
}

onMounted(() => {
  loadRules()
})
</script>

<style scoped>
.alert-rules-page {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
