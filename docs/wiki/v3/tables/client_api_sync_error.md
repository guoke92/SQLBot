---
type: table
title: 客户端接口同步失败记录
page_key: client_api_sync_error
belong: tables
status: draft
anchors:
- client_api_sync_error
sources:
- database_schema:lowcode_pplatform.client_api_sync_error
- code_path:StartupSyncRetry.java:119
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- client_api_sync_error__enable
---

# 客户端接口同步失败记录

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: client_api_sync_error
database: lowcode_pplatform
desc: 客户端接口同步失败记录
inactive: false
primary_key:
- id
grain: 客户端同步失败
name_anchors:
- code
- name
- service_class_name
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: service_class_name
  type: string
  desc: 服务类名称
- name: param
  type: string
  desc: 参数
- name: enable
  type: string
  desc: enable
  dict:
  - N
  - Y
  label: [停用, 启用]
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
- name: retry_num
  type: number
  desc: 重试次数
default_filter:
  predicate: client_api_sync_error.enable = 'Y'
  trust: confirmed
  evidence: code_path:StartupSyncRetry.java:119
```

## 页面链接

### 字典

- [[dicts/client_api_sync_error__enable]]（`client_api_sync_error.enable`）
