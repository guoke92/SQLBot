---
type: table
title: 客户端接口同步失败记录
page_key: client_api_sync_error
belong: tables
status: draft
anchors: [client_api_sync_error]
sources: ['database_schema:lowcode_pplatform.client_api_sync_error']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [client_api_sync_error__enable]
---

# 客户端接口同步失败记录

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### sync_service

`name`, `service_class_name`, `param`, `retry_num`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant_org

`app_tenant_code`, `db_tenant_code`, `organization_id`

## 字段

```ground:table
table: client_api_sync_error
database: lowcode_pplatform
description: 客户端接口同步失败记录
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, service_class_name]
clusters:
- key: common
  title: 通用
  include: always
- key: sync_service
  title: 同步服务定义
  trust: proposed
  evidence: database_schema:lowcode_pplatform.client_api_sync_error
- key: act_procinst
  title: 流程审批
  trust: proposed
  evidence: database_schema:lowcode_pplatform.client_api_sync_error
- key: tenant_org
  title: 租户与机构
  trust: proposed
  evidence: database_schema:lowcode_pplatform.client_api_sync_error
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: code
  data_type: string
  description: 编码
  cluster: common
- name: name
  data_type: string
  description: 名称
  cluster: sync_service
- name: service_class_name
  data_type: string
  description: 服务类名称
  cluster: sync_service
- name: param
  data_type: string
  description: 参数
  cluster: sync_service
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: client_api_sync_error__enable
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
  cluster: act_procinst
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant_org
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant_org
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: act_procinst
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: act_procinst
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: act_procinst
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: tenant_org
- name: retry_num
  data_type: number
  description: 重试次数
  cluster: sync_service
```

## 页面链接

### 字典

- [[dicts/client_api_sync_error__enable]]（`client_api_sync_error.enable`）
