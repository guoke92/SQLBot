---
type: table
title: 异步导入导出任务
page_key: async_io_task
belong: tables
status: draft
aliases: []
anchors:
- async_io_task
sources:
- database_schema:lowcode_pplatform.async_io_task
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 异步导入导出任务

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `is_deleted`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### task

`task_no`, `task_type`, `task_name`

### biz_invoke

`biz_class`, `biz_method`, `biz_args_json`, `ctx_json`

### runtime

`status`, `result_text`, `error_msg`, `start_time`, `end_time`

### file

`file_url`, `file_name`

### menu

`menu_code`, `menu_name`

### user

`user_id`, `user_name`

### tenant

`app_tenant_code`, `db_tenant_code`, `organization_id`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### generic

`name`, `remark`

## 字段

```ground:table
table: async_io_task
database: lowcode_pplatform
description: 异步导入导出任务
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- task_name
- menu_code
- menu_name
- file_name
- user_name
- code
- name
clusters:
- key: common
  title: 通用/审计字段
  include: always
- key: task
  title: 任务主体
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.async_io_task
- key: biz_invoke
  title: 异步调用上下文
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.async_io_task
- key: runtime
  title: 执行状态与结果
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.async_io_task
- key: file
  title: 结果文件
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.async_io_task
- key: menu
  title: 业务菜单
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.async_io_task
- key: user
  title: 发起人
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.async_io_task
- key: tenant
  title: 租户与机构
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.async_io_task
- key: workflow
  title: 审批流程关联
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.async_io_task
- key: generic
  title: 名称与备注
  confidence: proposed
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
  nullable: true
  cluster: task
  dictionary: async_io_task_task_type
- name: task_name
  data_type: string
  description: 任务名称
  nullable: true
  cluster: task
- name: menu_code
  data_type: string
  description: 业务菜单标识
  nullable: true
  cluster: menu
- name: menu_name
  data_type: string
  description: 业务菜单名称
  nullable: true
  cluster: menu
- name: biz_class
  data_type: string
  description: Controller Bean 全限定名
  nullable: true
  cluster: biz_invoke
- name: biz_method
  data_type: string
  description: 方法签名 name(paramTypes)
  nullable: true
  cluster: biz_invoke
- name: biz_args_json
  data_type: string
  description: 参数 JSON
  nullable: true
  cluster: biz_invoke
- name: ctx_json
  data_type: string
  description: 上下文：userId/custId/companyType/dbTenantCode 等
  nullable: true
  cluster: biz_invoke
- name: status
  data_type: string
  description: 状态
  nullable: true
  cluster: runtime
  dictionary: async_io_task_status
- name: result_text
  data_type: string
  description: 业务返回
  nullable: true
  cluster: runtime
- name: file_url
  data_type: string
  description: 成功:结果文件 / 失败:错误文件 的下载地址
  nullable: true
  cluster: file
- name: file_name
  data_type: string
  description: 文件名
  nullable: true
  cluster: file
- name: error_msg
  data_type: string
  description: 失败原因
  nullable: true
  cluster: runtime
- name: user_id
  data_type: number
  description: 用户ID
  nullable: true
  cluster: user
- name: user_name
  data_type: string
  description: 发起人姓名
  nullable: true
  cluster: user
- name: is_deleted
  data_type: string
  description: 软删除：0 否 1 是
  nullable: true
  cluster: common
  dictionary: async_io_task_is_deleted
- name: start_time
  data_type: temporal
  description: 任务开始时间
  nullable: true
  cluster: runtime
- name: end_time
  data_type: temporal
  description: 任务结束时间
  nullable: true
  cluster: runtime
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: generic
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: async_io_task_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: generic
- name: create_by
  data_type: string
  description: 创建人id
  nullable: true
  cluster: common
- name: create_user
  data_type: string
  description: 创建人名称
  nullable: true
  cluster: common
- name: create_time
  data_type: temporal
  description: 创建时间
  nullable: false
  cluster: common
- name: update_by
  data_type: string
  description: 更新人id
  nullable: true
  cluster: common
- name: update_user
  data_type: string
  description: 更新人名称
  nullable: true
  cluster: common
- name: update_time
  data_type: temporal
  description: 更新时间
  nullable: false
  cluster: common
- name: act_procinst_id
  data_type: string
  description: 流程实例ID
  nullable: true
  cluster: workflow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  nullable: true
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  nullable: true
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: workflow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: tenant
```
