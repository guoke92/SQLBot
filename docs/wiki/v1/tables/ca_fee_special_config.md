---
type: table
title: CA服务费特殊企业配置
page_key: ca_fee_special_config
belong: tables
status: draft
anchors: [ca_fee_special_config]
sources: ['database_schema:lowcode_pplatform.ca_fee_special_config']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [ca_fee_special_config__annual_fee, ca_fee_special_config__enable]
---

# CA服务费特殊企业配置

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `operate_logs`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`, `app_tenant_code`, `db_tenant_code`

### company_identity

`certification_no`, `company_name`, `organization_id`

### fee_validity

`annual_fee`, `valid_start`, `valid_end`

### approval_flow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### 未归簇

`project_id`

## 字段

```ground:table
table: ca_fee_special_config
database: lowcode_pplatform
description: CA服务费特殊企业配置
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [company_name, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: company_identity
  title: 企业身份
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_special_config
- key: fee_validity
  title: 费用与有效期
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_special_config
- key: approval_flow
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_special_config
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: certification_no
  data_type: string
  description: 统一社会信用代码
  cluster: company_identity
- name: company_name
  data_type: string
  description: 企业名称
  cluster: company_identity
- name: annual_fee
  data_type: number
  description: 年费标准
  cluster: fee_validity
  dictionary: ca_fee_special_config__annual_fee
- name: valid_start
  data_type: temporal
  description: 有效期起
  cluster: fee_validity
- name: valid_end
  data_type: temporal
  description: 有效期止
  cluster: fee_validity
- name: operate_logs
  data_type: string
  description: 操作日志
  cluster: common
- name: project_id
  data_type: number
  description: 项目id
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
  dictionary: ca_fee_special_config__enable
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
  cluster: approval_flow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: common
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: common
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: approval_flow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: approval_flow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval_flow
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: company_identity
```

## 页面链接

### 字典

- [[dicts/ca_fee_special_config__annual_fee]]（`ca_fee_special_config.annual_fee`）
- [[dicts/ca_fee_special_config__enable]]（`ca_fee_special_config.enable`）
