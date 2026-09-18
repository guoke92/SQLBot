---
type: table
title: CA服务费企业主数据
page_key: ca_fee_company
belong: tables
status: draft
anchors: [ca_fee_company]
sources: ['database_schema:lowcode_pplatform.ca_fee_company']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [ca_fee_project_config, ca_fee_order, ca_fee_company__fee_locked, ca_fee_company__pay_status,
  ca_fee_company__source_company_type, ca_fee_company__renew_remind_sent, ca_fee_company__special_config_flag,
  ca_fee_company__ca_status, ca_fee_company__enable]
---

# CA服务费企业主数据

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### identity

`certification_no`, `company_name`, `organization_id`

### fee

`locked_annual_fee`, `fee_locked`, `pay_status`, `special_config_flag`, `special_annual_fee`, `ca_status`

### service

`service_start`, `service_end`, `renew_remind_sent`

### source

`tenant_id`, `source_project_id`, `source_company_type`

### tenant

`app_tenant_code`, `db_tenant_code`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### 未归簇

`ext_json`

## 字段

```ground:table
table: ca_fee_company
database: lowcode_pplatform
description: CA服务费企业主数据
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [company_name, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: identity
  title: 企业主档身份
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_company
- key: fee
  title: 年费与缴费
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_company
- key: service
  title: 服务周期与续费
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_company
- key: source
  title: 首次锁定来源
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_company
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_company
- key: approval
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_company
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: certification_no
  data_type: string
  description: 统一社会信用代码
  cluster: identity
- name: company_name
  data_type: string
  description: 企业名称
  cluster: identity
- name: tenant_id
  data_type: number
  description: 首次锁定来源租户
  cluster: source
- name: locked_annual_fee
  data_type: number
  description: 首次缴费成功后锁定的年费标准（元）
  cluster: fee
- name: fee_locked
  data_type: string
  description: 是否已锁定年费标准
  cluster: fee
  dictionary: ca_fee_company__fee_locked
- name: pay_status
  data_type: string
  description: 缴费状态：PAID 已缴费 / UNPAID 未缴费
  cluster: fee
  dictionary: ca_fee_company__pay_status
- name: service_start
  data_type: temporal
  description: 当前 CA 服务费服务周期起始日（含）
  cluster: service
- name: service_end
  data_type: temporal
  description: 当前 CA 服务费服务周期截止日（含）
  cluster: service
- name: source_project_id
  data_type: number
  description: 首次锁定来源项目 ID
  cluster: source
- name: source_company_type
  data_type: string
  description: 首次锁定来源企业角色，如 SUPPLIER/CORE
  cluster: source
  dictionary: ca_fee_company__source_company_type
- name: renew_remind_sent
  data_type: string
  description: 本期续费待办是否已生成：Y 已生成 / N 未生成
  cluster: service
  dictionary: ca_fee_company__renew_remind_sent
- name: special_config_flag
  data_type: string
  description: 是否存在生效中的特殊配置快照
  cluster: fee
  dictionary: ca_fee_company__special_config_flag
- name: special_annual_fee
  data_type: number
  description: 特殊配置后应缴年费（元）
  cluster: fee
- name: ca_status
  data_type: string
  description: CA签章状态
  cluster: fee
  dictionary: ca_fee_company__ca_status
- name: ext_json
  data_type: string
  description: 扩展字段 JSON预留
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
  dictionary: ca_fee_company__enable
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
  cluster: approval
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
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: approval
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: identity
```

## 关联关系

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: ca_fee_project_config.id
right: ca_fee_company.source_project_id
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.ca_fee_company.source_project_id
source: llm
join_role: identity
priority: primary
name_evidence:
  match: llm_propose
  stem: source_project_id
  comment: 列名/注释语义最贴近（来源项目 ID ↔ CA服务费项目配置主键），但探测 overlap=0.0、authenticity=unlikely，样本仅
    13 条
overlap:
  probed: true
  ratio: 0.0
  sample_size: 13
  authenticity: unlikely
authenticity_note: 列名/注释语义最贴近（来源项目 ID ↔ CA服务费项目配置主键），但探测 overlap=0.0、authenticity=unlikely，样本仅
  13 条，值域契合度存疑，接受为待复核边。
```

## 页面链接

### 关联表

- [[tables/ca_fee_project_config]]
- [[tables/ca_fee_order]]

### 字典

- [[dicts/ca_fee_company__fee_locked]]（`ca_fee_company.fee_locked`）
- [[dicts/ca_fee_company__pay_status]]（`ca_fee_company.pay_status`）
- [[dicts/ca_fee_company__source_company_type]]（`ca_fee_company.source_company_type`）
- [[dicts/ca_fee_company__renew_remind_sent]]（`ca_fee_company.renew_remind_sent`）
- [[dicts/ca_fee_company__special_config_flag]]（`ca_fee_company.special_config_flag`）
- [[dicts/ca_fee_company__ca_status]]（`ca_fee_company.ca_status`）
- [[dicts/ca_fee_company__enable]]（`ca_fee_company.enable`）
