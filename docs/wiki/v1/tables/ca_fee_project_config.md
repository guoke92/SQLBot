---
type: table
title: CA服务费项目配置
page_key: ca_fee_project_config
belong: tables
status: draft
anchors: [ca_fee_project_config]
sources: ['database_schema:lowcode_pplatform.ca_fee_project_config']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [ca_fee_order, ca_fee_project_config__charge_enabled, ca_fee_project_config__supplier_annual_fee,
  ca_fee_project_config__core_annual_fee, ca_fee_project_config__agreement_version,
  ca_fee_project_config__enable, ca_fee_project_config__app_tenant_code]
---

# CA服务费项目配置

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### fee_config

`charge_enabled`, `supplier_annual_fee`, `core_annual_fee`, `pay_channel`, `special_company_list`, `block_scene_list`, `agreement_version`, `last_toggle_time`

### tenant

`tenant_id`, `app_tenant_code`, `db_tenant_code`

### project_org

`project_id`, `organization_id`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: ca_fee_project_config
database: lowcode_pplatform
description: CA服务费项目配置
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: fee_config
  title: 收费项目配置
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_project_config
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_project_config
- key: project_org
  title: 项目与机构
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_project_config
- key: act_procinst
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_project_config
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: project_id
  data_type: number
  description: 项目ID
  cluster: project_org
- name: tenant_id
  data_type: number
  description: 所属租户
  cluster: tenant
- name: charge_enabled
  data_type: string
  description: 是否开启CA收费
  cluster: fee_config
  dictionary: ca_fee_project_config__charge_enabled
- name: supplier_annual_fee
  data_type: number
  description: 供应商角色年费（元）
  cluster: fee_config
  dictionary: ca_fee_project_config__supplier_annual_fee
- name: core_annual_fee
  data_type: number
  description: 核心企业角色年费（元）
  cluster: fee_config
  dictionary: ca_fee_project_config__core_annual_fee
- name: pay_channel
  data_type: string
  description: 缴费渠道JSON数组
  cluster: fee_config
- name: special_company_list
  data_type: string
  description: 特殊企业配置JSON数组
  cluster: fee_config
- name: block_scene_list
  data_type: string
  description: 拦截场景编码 JSON 数组，元素见 CaFeeInterceptSceneEnum
  cluster: fee_config
- name: agreement_version
  data_type: string
  description: 当前绑定收费协议版本号
  cluster: fee_config
  dictionary: ca_fee_project_config__agreement_version
- name: last_toggle_time
  data_type: temporal
  description: 最近一次收费开关切换时间
  cluster: fee_config
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
  dictionary: ca_fee_project_config__enable
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
  cluster: tenant
  dictionary: ca_fee_project_config__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
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
  cluster: project_org
```

## 页面链接

### 关联表

- [[tables/ca_fee_order]]

### 字典

- [[dicts/ca_fee_project_config__charge_enabled]]（`ca_fee_project_config.charge_enabled`）
- [[dicts/ca_fee_project_config__supplier_annual_fee]]（`ca_fee_project_config.supplier_annual_fee`）
- [[dicts/ca_fee_project_config__core_annual_fee]]（`ca_fee_project_config.core_annual_fee`）
- [[dicts/ca_fee_project_config__agreement_version]]（`ca_fee_project_config.agreement_version`）
- [[dicts/ca_fee_project_config__enable]]（`ca_fee_project_config.enable`）
- [[dicts/ca_fee_project_config__app_tenant_code]]（`ca_fee_project_config.app_tenant_code`）
