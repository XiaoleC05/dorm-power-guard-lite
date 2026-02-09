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
        <el-table-column prop="threshold" label="告警阈值（元）" width="150" />
        <el-table-column prop="enabled" label="启用状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">
              {{ row.enabled ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="email_enabled" label="邮件告警" width="100">
          <template #default="{ row }">
            <el-tag :type="row.email_enabled ? 'success' : 'info'">
              {{ row.email_enabled ? '启用' : '禁用' }}
            </el-tag>
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
      <el-form :model="ruleForm" label-width="120px">
        <el-form-item label="宿舍号">
          <el-input v-model="ruleForm.dorm_number" :disabled="!!editingRule" />
        </el-form-item>
        <el-form-item label="告警阈值（元）">
          <el-input-number v-model="ruleForm.threshold" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="ruleForm.enabled" />
        </el-form-item>
        <el-form-item label="邮件告警">
          <el-switch v-model="ruleForm.email_enabled" />
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
import { ref, onMounted } from 'vue'
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
  threshold: 20.0,
  enabled: true,
  email_enabled: false,
  qq_enabled: false
})

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const loadRules = async () => {
  loading.value = true
  try {
    const data = await getAllAlertRules()
    rules.value = data
  } catch (error) {
    ElMessage.error('加载规则失败：' + error.message)
  } finally {
    loading.value = false
  }
}

const editRule = (rule) => {
  editingRule.value = rule
  ruleForm.value = {
    dorm_number: rule.dorm_number,
    threshold: rule.threshold,
    enabled: rule.enabled,
    email_enabled: rule.email_enabled,
    qq_enabled: rule.qq_enabled
  }
  showDialog.value = true
}

const saveRule = async () => {
  try {
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
      threshold: 20.0,
      enabled: true,
      email_enabled: false,
      qq_enabled: false
    }
    await loadRules()
  } catch (error) {
    ElMessage.error('保存失败：' + error.message)
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
