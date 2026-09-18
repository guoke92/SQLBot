---
type: table
title: 异步导入导出任务
page_key: async_io_task
belong: tables
status: draft
anchors: [async_io_task]
sources: ['database_schema:lowcode_pplatform.async_io_task']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [async_io_task__task_type, async_io_task__menu_code, async_io_task__status,
  async_io_task__is_deleted, async_io_task__enable]
---

# 异步导入导出任务

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: async_io_task
database: lowcode_pplatform
desc: 异步导入导出任务
inactive: false
primary_key: [id]
grain: 一异步导入导出任务一行
name_anchors: [task_name, menu_code, menu_name, file_name, user_name, code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: task_no
  type: number
  desc: 任务号
  nullable: false
- name: task_type
  type: string
  desc: 任务类型
  dict: [IMPORT, EXPORT]
- name: task_name
  type: string
  desc: 任务名称
- name: menu_code
  type: string
  desc: 业务菜单标识
  dict: [PROJECT_REPORT_STATISTICS, WECHAT_PROJECT_APPROVAL, CUST_PROJECT_REL_BATCH,
    TENANT_PROJECT_CONFIG, CUST_INPUT_BATCH, PROJECT_ONLINE_APPROVAL]
- name: menu_name
  type: string
  desc: 业务菜单名称
- name: biz_class
  type: string
  desc: Controller Bean 全限定名
- name: biz_method
  type: string
  desc: 方法签名 name(paramTypes)
- name: biz_args_json
  type: string
  desc: 参数 JSON
- name: ctx_json
  type: string
  desc: 上下文：userId/custId/companyType/dbTenantCode 等
- name: status
  type: string
  desc: 状态
  dict: [SUCCESS, FAILED, RUNNING]
- name: result_text
  type: string
  desc: 业务返回
- name: file_url
  type: string
  desc: 成功:结果文件 / 失败:错误文件 的下载地址
- name: file_name
  type: string
  desc: 文件名
- name: error_msg
  type: string
  desc: 失败原因
- name: user_id
  type: number
  desc: 用户ID
- name: user_name
  type: string
  desc: 发起人姓名
- name: is_deleted
  type: string
  desc: 软删除：0 否 1 是
  dict: ['0', '1']
  label: [否, 是]
- name: start_time
  type: temporal
  desc: 任务开始时间
- name: end_time
  type: temporal
  desc: 任务结束时间
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: enable
  type: string
  desc: enable
  dict: [Y]
- name: remark
  type: string
  desc: remark
- name: create_by
  type: string
  desc: 创建人id
- name: create_user
  type: string
  desc: 创建人名称
- name: create_time
  type: temporal
  desc: 创建时间
  nullable: false
- name: update_by
  type: string
  desc: 更新人id
- name: update_user
  type: string
  desc: 更新人名称
- name: update_time
  type: temporal
  desc: 更新时间
  nullable: false
- name: act_procinst_id
  type: string
  desc: 流程实例ID
- name: app_tenant_code
  type: string
  desc: 逻辑租户标识
- name: db_tenant_code
  type: string
  desc: 数据租户标识
- name: act_procinst_no
  type: string
  desc: 流程申请编号
- name: act_procinst_status
  type: string
  desc: 当前审批状态
- name: act_procinst_date
  type: temporal
  desc: 审批结束时间
- name: organization_id
  type: string
  desc: 机构编号
```

## 页面链接

### 字典

- [[dicts/async_io_task__task_type]]（`async_io_task.task_type`）
- [[dicts/async_io_task__menu_code]]（`async_io_task.menu_code`）
- [[dicts/async_io_task__status]]（`async_io_task.status`）
- [[dicts/async_io_task__is_deleted]]（`async_io_task.is_deleted`）
- [[dicts/async_io_task__enable]]（`async_io_task.enable`）
