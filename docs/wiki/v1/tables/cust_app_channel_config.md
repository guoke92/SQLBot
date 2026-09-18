---
type: table
title: 客户应用渠道关系
page_key: cust_app_channel_config
belong: tables
status: draft
anchors: [cust_app_channel_config]
sources: ['database_schema:lowcode_pplatform.cust_app_channel_config']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_app_channel_config__app_id, cust_app_channel_config__code,
  cust_app_channel_config__name, cust_app_channel_config__enable, cust_app_channel_config__app_tenant_code,
  cust_app_channel_config__db_tenant_code]
---

# 客户应用渠道关系

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### tenant_org

`app_tenant_code`, `db_tenant_code`, `organization_id`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### 未归簇

`app_id`

## 字段

```ground:table
table: cust_app_channel_config
database: lowcode_pplatform
description: 客户应用渠道关系
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: tenant_org
  title: 租户与机构
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_app_channel_config
- key: act_procinst
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_app_channel_config
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: app_id
  data_type: string
  description: 应用id
  dictionary: cust_app_channel_config__app_id
- name: code
  data_type: string
  description: 编码
  cluster: common
  dictionary: cust_app_channel_config__code
- name: name
  data_type: string
  description: 名称
  cluster: common
  dictionary: cust_app_channel_config__name
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_app_channel_config__enable
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
  dictionary: cust_app_channel_config__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant_org
  dictionary: cust_app_channel_config__db_tenant_code
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
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_app_channel_config__app_id]]（`cust_app_channel_config.app_id`）
- [[dicts/cust_app_channel_config__code]]（`cust_app_channel_config.code`）
- [[dicts/cust_app_channel_config__name]]（`cust_app_channel_config.name`）
- [[dicts/cust_app_channel_config__enable]]（`cust_app_channel_config.enable`）
- [[dicts/cust_app_channel_config__app_tenant_code]]（`cust_app_channel_config.app_tenant_code`）
- [[dicts/cust_app_channel_config__db_tenant_code]]（`cust_app_channel_config.db_tenant_code`）
