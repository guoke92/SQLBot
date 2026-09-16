---
type: table
title: 资金方异常解析及建议主表
page_key: funding_exception_resolution
belong: tables
status: draft
aliases: []
anchors:
- funding_exception_resolution
sources:
- database_schema:lowcode_pplatform.funding_exception_resolution
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 资金方异常解析及建议主表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### exception

`exception_no`, `error_keyword`, `error_reason`, `suggestion`, `file_path`

### funding_party

`funding_party_code`, `funding_party_name`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`product_code`, `organization_id`

## 字段

```ground:table
table: funding_exception_resolution
database: lowcode_pplatform
description: 资金方异常解析及建议主表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- funding_party_code
- funding_party_name
- product_code
- code
- name
clusters:
- key: common
  title: 通用/审计
  include: always
- key: exception
  title: 异常信息与处理
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.funding_exception_resolution
- key: funding_party
  title: 资金方
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.funding_exception_resolution
- key: workflow
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.funding_exception_resolution
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.funding_exception_resolution
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: exception_no
  data_type: string
  description: 异常编号
  nullable: true
  cluster: exception
- name: funding_party_code
  data_type: string
  description: 对接方标识
  nullable: true
  cluster: funding_party
- name: funding_party_name
  data_type: string
  description: 资金方名称
  nullable: true
  cluster: funding_party
- name: error_keyword
  data_type: string
  description: 报错关键字
  nullable: true
  cluster: exception
- name: error_reason
  data_type: string
  description: 报错原因
  nullable: true
  cluster: exception
- name: suggestion
  data_type: string
  description: 建议处理方案
  nullable: true
  cluster: exception
- name: file_path
  data_type: string
  description: 附件
  nullable: true
  cluster: exception
- name: product_code
  data_type: string
  description: 产品code
  nullable: true
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: common
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: funding_exception_resolution_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: common
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
```
