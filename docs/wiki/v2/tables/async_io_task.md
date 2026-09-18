---
type: table
title: 异步导入导出任务
page_key: async_io_task
belong: tables
status: draft
anchors: [async_io_task]
sources: ['database_schema:lowcode_pplatform.async_io_task']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [async_io_task__task_type, async_io_task__menu_code, async_io_task__status,
  async_io_task__is_deleted, async_io_task__enable]
---

# 异步导入导出任务

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `is_deleted`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### task

`task_no`, `task_type`, `task_name`

### menu

`menu_code`, `menu_name`

### execution

`biz_class`, `biz_method`, `biz_args_json`, `ctx_json`, `status`, `result_text`, `error_msg`, `start_time`, `end_time`

### file

`file_url`, `file_name`

### initiator

`user_id`, `user_name`

### process

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`organization_id`

## 字段

```ground:table
table: async_io_task
database: lowcode_pplatform
description: 异步导入导出任务
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [task_name, menu_code, menu_name, file_name, user_name, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: task
  title: 任务信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.async_io_task
- key: menu
  title: 业务菜单
  trust: proposed
  evidence: database_schema:lowcode_pplatform.async_io_task
- key: execution
  title: 执行与结果
  trust: proposed
  evidence: database_schema:lowcode_pplatform.async_io_task
- key: file
  title: 文件
  trust: proposed
  evidence: database_schema:lowcode_pplatform.async_io_task
- key: initiator
  title: 发起人
  trust: proposed
  evidence: database_schema:lowcode_pplatform.async_io_task
- key: process
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.async_io_task
- key: tenant
  title: 租户
  trust: proposed
  evidence: database_schema:lowcode_pplatform.async_io_task
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: task_no
  data_type: number
  description: 任务号
  nullable: false
  cluster: task
- name: task_type
  data_type: string
  description: 任务类型
  cluster: task
  dictionary: async_io_task__task_type
- name: task_name
  data_type: string
  description: 任务名称
  cluster: task
- name: menu_code
  data_type: string
  description: 业务菜单标识
  cluster: menu
  dictionary: async_io_task__menu_code
- name: menu_name
  data_type: string
  description: 业务菜单名称
  cluster: menu
- name: biz_class
  data_type: string
  description: Controller Bean 全限定名
  cluster: execution
- name: biz_method
  data_type: string
  description: 方法签名 name(paramTypes)
  cluster: execution
- name: biz_args_json
  data_type: string
  description: 参数 JSON
  cluster: execution
- name: ctx_json
  data_type: string
  description: 上下文：userId/custId/companyType/dbTenantCode 等
  cluster: execution
- name: status
  data_type: string
  description: 状态
  cluster: execution
  dictionary: async_io_task__status
- name: result_text
  data_type: string
  description: 业务返回
  cluster: execution
- name: file_url
  data_type: string
  description: 成功:结果文件 / 失败:错误文件 的下载地址
  cluster: file
- name: file_name
  data_type: string
  description: 文件名
  cluster: file
- name: error_msg
  data_type: string
  description: 失败原因
  cluster: execution
- name: user_id
  data_type: number
  description: 用户ID
  cluster: initiator
- name: user_name
  data_type: string
  description: 发起人姓名
  cluster: initiator
- name: is_deleted
  data_type: string
  description: 软删除：0 否 1 是
  cluster: common
  dictionary: async_io_task__is_deleted
- name: start_time
  data_type: temporal
  description: 任务开始时间
  cluster: execution
- name: end_time
  data_type: temporal
  description: 任务结束时间
  cluster: execution
- name: code
  data_type: string
  description: 编码
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: common
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: async_io_task__enable
- name: remark
  data_type: string
  description: remark
  cluster: common
- name: create_by
  data_type: string
  description: 创建人id
  cluster: common
- name: create_user
  data_type: string
  description: 创建人名称
  cluster: common
- name: create_time
  data_type: temporal
  description: 创建时间
  nullable: false
  cluster: common
- name: update_by
  data_type: string
  description: 更新人id
  cluster: common
- name: update_user
  data_type: string
  description: 更新人名称
  cluster: common
- name: update_time
  data_type: temporal
  description: 更新时间
  nullable: false
  cluster: common
- name: act_procinst_id
  data_type: string
  description: 流程实例ID
  cluster: process
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: process
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: process
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: process
- name: organization_id
  data_type: string
  description: 机构编号
```

## 页面链接

### 字典

- [[dicts/async_io_task__task_type]]（`async_io_task.task_type`）
- [[dicts/async_io_task__menu_code]]（`async_io_task.menu_code`）
- [[dicts/async_io_task__status]]（`async_io_task.status`）
- [[dicts/async_io_task__is_deleted]]（`async_io_task.is_deleted`）
- [[dicts/async_io_task__enable]]（`async_io_task.enable`）
