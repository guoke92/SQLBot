---
type: table
title: 资金方异常解析及建议主表
page_key: funding_exception_resolution
belong: tables
status: draft
anchors: [funding_exception_resolution]
sources: ['database_schema:lowcode_pplatform.funding_exception_resolution']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [funding_rule_info, funding_exception_resolution__funding_party_code, funding_exception_resolution__product_code,
  funding_exception_resolution__enable]
---

# 资金方异常解析及建议主表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### funding

`funding_party_code`, `funding_party_name`

### error

`error_keyword`, `error_reason`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### 未归簇

`exception_no`, `suggestion`, `file_path`, `product_code`, `name`, `remark`, `app_tenant_code`, `db_tenant_code`, `organization_id`

## 字段

```ground:table
table: funding_exception_resolution
database: lowcode_pplatform
description: 资金方异常解析及建议主表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [funding_party_code, funding_party_name, product_code, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: funding
  title: funding
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_exception_resolution prefix:funding_
- key: error
  title: error
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_exception_resolution prefix:error_
- key: act_procinst
  title: act_procinst
  trust: proposed
  evidence: database_schema:lowcode_pplatform.funding_exception_resolution prefix:act_procinst_
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: exception_no
  data_type: string
  description: 异常编号
- name: funding_party_code
  data_type: string
  description: 对接方标识
  cluster: funding
  dictionary: funding_exception_resolution__funding_party_code
- name: funding_party_name
  data_type: string
  description: 资金方名称
  cluster: funding
- name: error_keyword
  data_type: string
  description: 报错关键字
  cluster: error
- name: error_reason
  data_type: string
  description: 报错原因
  cluster: error
- name: suggestion
  data_type: string
  description: 建议处理方案
- name: file_path
  data_type: string
  description: 附件
- name: product_code
  data_type: string
  description: 产品code
  dictionary: funding_exception_resolution__product_code
- name: code
  data_type: string
  description: 编码
  cluster: common
- name: name
  data_type: string
  description: 名称
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: funding_exception_resolution__enable
- name: remark
  data_type: string
  description: remark
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
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
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
```

## 页面链接

### 关联表

- [[tables/funding_rule_info]]

### 字典

- [[dicts/funding_exception_resolution__funding_party_code]]（`funding_exception_resolution.funding_party_code`）
- [[dicts/funding_exception_resolution__product_code]]（`funding_exception_resolution.product_code`）
- [[dicts/funding_exception_resolution__enable]]（`funding_exception_resolution.enable`）
