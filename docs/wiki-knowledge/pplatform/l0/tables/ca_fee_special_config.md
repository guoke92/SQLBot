---
type: table
title: CA服务费特殊企业配置
page_key: ca_fee_special_config
belong: tables
status: draft
aliases: []
anchors:
- ca_fee_special_config
sources:
- database_schema:lowcode_pplatform.ca_fee_special_config
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# CA服务费特殊企业配置

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### enterprise

`certification_no`, `company_name`

### fee

`annual_fee`, `name`, `remark`

### validity

`valid_start`, `valid_end`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### ref

`project_id`, `organization_id`

### 未归簇

`operate_logs`

## 字段

```ground:table
table: ca_fee_special_config
database: lowcode_pplatform
description: CA服务费特殊企业配置
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
  title: 通用（主键/编码/开关/审计/时间戳）
  include: always
- key: enterprise
  title: 企业主体信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_special_config
- key: fee
  title: 费用配置
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_special_config
- key: validity
  title: 有效期
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_special_config
- key: workflow
  title: 审批流程实例
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_special_config
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_fee_special_config
- key: ref
  title: 外部引用
  confidence: proposed
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
  nullable: true
  cluster: enterprise
- name: company_name
  data_type: string
  description: 企业名称
  nullable: true
  cluster: enterprise
- name: annual_fee
  data_type: number
  description: 年费标准
  nullable: true
  cluster: fee
- name: valid_start
  data_type: temporal
  description: 有效期起
  nullable: true
  cluster: validity
- name: valid_end
  data_type: temporal
  description: 有效期止
  nullable: true
  cluster: validity
- name: operate_logs
  data_type: string
  description: 操作日志
  nullable: true
- name: project_id
  data_type: number
  description: 项目id
  nullable: true
  cluster: ref
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: fee
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: ca_fee_special_config_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: fee
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
  cluster: ref
```
