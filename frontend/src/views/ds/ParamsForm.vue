<script lang="ts" setup>
	import { nextTick, ref } from 'vue'
	import DatasourceForm from './DatasourceForm.vue'
	import icon_close_outlined from '@/assets/svg/operate/ope-close.svg'
	
	const datasourceFormRef = ref()
	const datasourceConfigVisible = ref(false)
	const drawerDsType = ref('')
	const beforeClose = () => {
	  datasourceConfigVisible.value = false
	  drawerDsType.value = ''
	}
	
	const emit = defineEmits(['refresh'])
	const refresh = () => {
	  emit('refresh')
	}
	const changeActiveStep = (val: any) => {
	  if (val === 0) {
	    datasourceConfigVisible.value = false
	  } else {
	    drawerActiveStep.value = val
	  }
	}
	const save = () => {
	  datasourceFormRef.value.tableListSave()
	}
	
	const drawerActiveStep = ref(2)
	const open = (item: any, step: number = 2) => {
	  drawerDsType.value = item?.type || ''
	  drawerActiveStep.value = step
	  datasourceConfigVisible.value = true
	  nextTick(() => {
	    datasourceFormRef.value.initForm(item, step === 2)
	  })
	}
	
	defineExpose({
	  open,
	})
	</script>
	
	<template>
	  <el-drawer
	    v-model="datasourceConfigVisible"
	    :close-on-click-modal="false"
	    size="calc(100% - 100px)"
	    modal-class="datasource-drawer-fullscreen"
	    direction="btt"
	    :before-close="beforeClose"
	    :show-close="false"
	  >
		    <template #header="{ close }">
		      <span style="white-space: nowrap">{{
		        drawerActiveStep === 1
		          ? $t('ds.form.title.edit')
		          : drawerDsType === 'api'
		            ? $t('ds.form.confirm_endpoints')
		            : $t('ds.form.choose_tables')
		      }}</span>
	      <el-icon style="cursor: pointer" @click="close">
	        <icon_close_outlined></icon_close_outlined>
	      </el-icon>
	    </template>
		    <DatasourceForm
		      ref="datasourceFormRef"
		      :active-step="drawerActiveStep"
		      active-name=""
		      active-type=""
		      is-data-table
		      @change-active-step="changeActiveStep"
		      @refresh="refresh"
		    ></DatasourceForm>
	    <template #footer>
	      <el-button secondary @click="beforeClose"> {{ $t('common.cancel') }} </el-button>
	      <el-button type="primary" @click="save"> {{ $t('common.save') }} </el-button>
	    </template>
	  </el-drawer>
	</template>
	
	<style lang="less" scoped></style>
