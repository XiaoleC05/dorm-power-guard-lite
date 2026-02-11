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
        <el-table-column prop="room_id" label="房间ID" width="120">
          <template #default="{ row }">
            {{ row.room_id || '-' }}
          </template>
        </el-table-column>
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
        <el-table-column prop="qq_enabled" label="QQ告警" width="200">
          <template #default="{ row }">
            <div>
              <el-tag :type="row.qq_enabled ? 'success' : 'info'" style="margin-bottom: 5px; display: block;">
                {{ row.qq_enabled ? '启用' : '禁用' }}
              </el-tag>
              <div v-if="row.qq_enabled" style="font-size: 12px; color: #909399;">
                <span v-if="row.qq_receiver_id && row.qq_receiver_id.trim() !== ''" style="display: block;">
                  <el-icon style="margin-right: 3px;"><User /></el-icon>
                  接收者：{{ row.qq_receiver_id }}
                </span>
                <span v-else style="color: #c0c4cc; font-style: italic;">
                  未配置接收QQ号
                </span>
              </div>
              <div v-if="!row.qq_enabled" style="font-size: 12px; color: #c0c4cc;">
                QQ告警已禁用
              </div>
            </div>
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
        <el-form-item label="房间ID（room_id）">
          <el-input 
            v-model="ruleForm.room_id" 
            placeholder="请输入房间ID（通过抓包获取，如：5699）"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 5px;">
            用于查询电费数据，需要通过抓包工具获取
          </div>
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
        <el-form-item 
          label="QQ接收者" 
          v-if="ruleForm.qq_enabled"
          prop="qq_receiver_id"
        >
          <el-input 
            v-model="ruleForm.qq_receiver_id" 
            placeholder="请输入QQ号（私聊）或群号（群聊），留空使用全局配置"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 5px;">
            输入QQ号发送私聊消息，输入群号发送群消息。留空则使用全局配置
          </div>
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
import { Plus, User } from '@element-plus/icons-vue'
import { getAllAlertRules, createAlertRule, updateAlertRule, deleteAlertRule } from '../api/alert'
import dayjs from 'dayjs'

const loading = ref(false)
const rules = ref([])
const showDialog = ref(false)
const editingRule = ref(null)
const ruleForm = ref({
  dorm_number: '',
  room_id: '',
  kthreshold: 20.0,
  zthreshold: 20.0,
  threshold: null,
  enabled: true,
  email_enabled: false,
  email_address: '',
  qq_enabled: false,
  qq_receiver_id: ''
})


const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const loadRules = async () => {
  loading.value = true
  try {
    const data = await getAllAlertRules()
    // 确保字段存在，处理null和undefined值，从数据库加载数据
    rules.value = data.map(rule => {
      // 处理room_id字段，从数据库加载
      const roomId = (rule.room_id !== null && 
                      rule.room_id !== undefined && 
                      rule.room_id !== '') 
        ? String(rule.room_id).trim() 
        : ''
      // 处理email_address字段，从数据库加载
      const emailAddress = (rule.email_address !== null && 
                            rule.email_address !== undefined && 
                            rule.email_address !== '') 
        ? String(rule.email_address).trim() 
        : ''
      // 处理qq_receiver_id字段，从数据库加载
      const qqReceiverId = (rule.qq_receiver_id !== null && 
                            rule.qq_receiver_id !== undefined && 
                            rule.qq_receiver_id !== '') 
        ? String(rule.qq_receiver_id).trim() 
        : ''
      return {
        ...rule,
        room_id: roomId,
        email_address: emailAddress,
        qq_receiver_id: qqReceiverId
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
  ],
  qq_receiver_id: [
    {
      validator: (rule, value, callback) => {
        if (ruleForm.value.qq_enabled) {
          if (!value || !value.trim()) {
            callback(new Error('启用QQ告警时必须输入接收QQ号或群号'))
          } else {
            // 验证QQ号格式（纯数字，支持群号和用户QQ号）
            const qqStr = value.trim()
            const qqRegex = /^\d+$/
            if (!qqRegex.test(qqStr)) {
              callback(new Error('QQ号或群号必须是数字'))
              return
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
  
  // 处理room_id字段
  let roomId = ''
  if (rule.room_id !== null && 
      rule.room_id !== undefined && 
      rule.room_id !== '') {
    const roomIdStr = String(rule.room_id).trim()
    if (roomIdStr !== '' && roomIdStr !== 'null' && roomIdStr !== 'undefined') {
      roomId = roomIdStr
    }
  }
  
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
  
  // 处理qq_receiver_id字段
  let qqReceiverId = ''
  if (rule.qq_receiver_id !== null && 
      rule.qq_receiver_id !== undefined && 
      rule.qq_receiver_id !== '') {
    const qqStr = String(rule.qq_receiver_id).trim()
    if (qqStr !== '' && qqStr !== 'null' && qqStr !== 'undefined') {
      qqReceiverId = qqStr
    }
  }
  
  // 重新创建表单对象，确保响应式更新
  ruleForm.value = {
    dorm_number: rule.dorm_number || '',
    room_id: roomId,
    kthreshold: rule.kthreshold !== null && rule.kthreshold !== undefined ? rule.kthreshold : 20.0,
    zthreshold: rule.zthreshold !== null && rule.zthreshold !== undefined ? rule.zthreshold : 20.0,
    threshold: rule.threshold,
    enabled: rule.enabled !== null && rule.enabled !== undefined ? rule.enabled : true,
    email_enabled: rule.email_enabled !== null && rule.email_enabled !== undefined ? rule.email_enabled : false,
    email_address: emailAddress,
    qq_enabled: rule.qq_enabled !== null && rule.qq_enabled !== undefined ? rule.qq_enabled : false,
    qq_receiver_id: qqReceiverId
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
    
    // 如果禁用QQ告警，清空QQ接收者ID
    if (!ruleForm.value.qq_enabled) {
      ruleForm.value.qq_receiver_id = ''
    }
    
    // 准备发送的数据，确保空字符串转换为null
    const submitData = {
      ...ruleForm.value,
      // 处理room_id：如果为空字符串，转换为null
      room_id: ruleForm.value.room_id && ruleForm.value.room_id.trim() 
        ? ruleForm.value.room_id.trim() 
        : null,
      // 处理email_address：如果为空字符串，转换为null
      email_address: ruleForm.value.email_address && ruleForm.value.email_address.trim() 
        ? ruleForm.value.email_address.trim() 
        : null,
      // 处理qq_receiver_id：如果为空字符串，转换为null
      qq_receiver_id: ruleForm.value.qq_receiver_id && ruleForm.value.qq_receiver_id.trim() 
        ? ruleForm.value.qq_receiver_id.trim() 
        : null
    }
    
    if (editingRule.value) {
      await updateAlertRule(editingRule.value.dorm_number, submitData)
      ElMessage.success('更新成功')
    } else {
      await createAlertRule(submitData)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    editingRule.value = null
    ruleForm.value = {
      dorm_number: '',
      room_id: '',
      kthreshold: 20.0,
      zthreshold: 20.0,
      threshold: null,
      enabled: true,
      email_enabled: false,
      email_address: '',
      qq_enabled: false,
      qq_receiver_id: ''
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
