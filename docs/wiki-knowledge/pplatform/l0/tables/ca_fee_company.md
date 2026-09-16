---
type: table
title: CA服务费企业主数据
page_key: ca_fee_company
belong: tables
status: draft
aliases: []
anchors:
- ca_fee_company
sources:
- database_schema:lowcode_pplatform.ca_fee_company
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# CA服务费企业主数据

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### company_identity

`certification_no`, `company_name`, `name`

### source_lock

`tenant_id`, `source_project_id`, `source_company_type`

### service_period

`service_start`, `service_end`

### fee_management

`locked_annual_fee`, `fee_locked`, `pay_status`, `renew_remind_sent`

### special_config

`special_config_flag`, `special_annual_fee`

### approval_flow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant_org

`app_tenant_code`, `db_tenant_code`, `organization_id`

### extension

`ext_json`, `remark`

### 未归簇

`ca_status`

## 字段

```ground:table
table: ca_fee_company
database: lowcode_pplatform
description: CA服务费企业主数据
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- company_name
- code
- name
clusters:
- key: common
  title: 通用
  include: always
- key: company_identity
  title: 企业主档身份
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_company
- key: source_lock
  title: 来源锁定
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_company
- key: service_period
  title: 服务周期
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_company
- key: fee_management
  title: 年费与缴费
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_company
- key: special_config
  title: 特殊配置
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_company
- key: approval_flow
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_company
- key: tenant_org
  title: 租户与机构
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_company
- key: extension
  title: 扩展与备注
  confidence: proposed
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
  nullable: true
  cluster: company_identity
- name: company_name
  data_type: string
  description: 企业名称
  nullable: true
  cluster: company_identity
- name: tenant_id
  data_type: number
  description: 首次锁定来源租户
  nullable: true
  cluster: source_lock
- name: locked_annual_fee
  data_type: number
  description: 首次缴费成功后锁定的年费标准（元）
  nullable: true
  cluster: fee_management
- name: fee_locked
  data_type: string
  description: 是否已锁定年费标准
  nullable: true
  cluster: fee_management
  dictionary: ca_fee_company_fee_locked
- name: pay_status
  data_type: string
  description: 缴费状态：PAID 已缴费 / UNPAID 未缴费
  nullable: true
  cluster: fee_management
  dictionary: ca_fee_company_pay_status
- name: service_start
  data_type: temporal
  description: 当前 CA 服务费服务周期起始日（含）
  nullable: true
  cluster: service_period
- name: service_end
  data_type: temporal
  description: 当前 CA 服务费服务周期截止日（含）
  nullable: true
  cluster: service_period
- name: source_project_id
  data_type: number
  description: 首次锁定来源项目 ID
  nullable: true
  cluster: source_lock
- name: source_company_type
  data_type: string
  description: 首次锁定来源企业角色，如 SUPPLIER/CORE
  nullable: true
  cluster: source_lock
  dictionary: ca_fee_company_source_company_type
- name: renew_remind_sent
  data_type: string
  description: 本期续费待办是否已生成：Y 已生成 / N 未生成
  nullable: true
  cluster: fee_management
  dictionary: ca_fee_company_renew_remind_sent
- name: special_config_flag
  data_type: string
  description: 是否存在生效中的特殊配置快照
  nullable: true
  cluster: special_config
  dictionary: ca_fee_company_special_config_flag
- name: special_annual_fee
  data_type: number
  description: 特殊配置后应缴年费（元）
  nullable: true
  cluster: special_config
- name: ca_status
  data_type: string
  description: CA签章状态
  nullable: true
  dictionary: ca_fee_company_ca_status
- name: ext_json
  data_type: string
  description: 扩展字段 JSON预留
  nullable: true
  cluster: extension
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: company_identity
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: extension
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
  cluster: approval_flow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  nullable: true
  cluster: tenant_org
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant_org
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  nullable: true
  cluster: approval_flow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval_flow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval_flow
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: tenant_org
```
