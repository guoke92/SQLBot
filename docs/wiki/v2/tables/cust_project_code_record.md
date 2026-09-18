---
type: table
title: 企业项目码输入记录
page_key: cust_project_code_record
belong: tables
status: draft
anchors: [cust_project_code_record]
sources: ['database_schema:lowcode_pplatform.cust_project_code_record']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_project_code_record__status, cust_project_code_record__type,
  cust_project_code_record__enable]
---

# 企业项目码输入记录

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `type`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### flag

`status`

### company

`company_id`, `company_type`, `organization_id`

### source

`use_id`, `channel_code`

### audit

（空）

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

## 字段

```ground:table
table: cust_project_code_record
database: lowcode_pplatform
description: 企业项目码输入记录
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, channel_code]
clusters:
- key: common
  title: 通用
  include: always
- key: flag
  title: 状态标志
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_code_record
- key: company
  title: 企业机构
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_code_record
- key: source
  title: 录入来源
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_code_record
- key: audit
  title: 审计字段
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_code_record
- key: workflow
  title: 流程审批
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_code_record
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_code_record
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
  cluster: common
- name: company_id
  data_type: number
  description: 企业id
  cluster: company
- name: use_id
  data_type: number
  description: 用户id
  cluster: source
- name: channel_code
  data_type: string
  description: 渠道码
  cluster: source
- name: status
  data_type: string
  description: 是否正确状态
  cluster: flag
  dictionary: cust_project_code_record__status
- name: company_type
  data_type: string
  description: 企业角色
  cluster: company
- name: type
  data_type: string
  description: 类型
  cluster: common
  dictionary: cust_project_code_record__type
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_project_code_record__enable
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
  cluster: workflow
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
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: workflow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: company
```

## 关联关系

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_project_code_record.company_id
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.cust_project_code_record.company_id;database_profile:lowcode_pplatform.cust_project_code_record.company_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: company
  comment: 企业id
overlap:
  probed: true
  ratio: 0.9278
  ratio_reverse: 0.0
  sample_size: 263
  miss: 19
  deepened: true
  query_ok: true
  authenticity: unknown
authenticity_note: name_evidence=family_suffix(stem=company)，本地注释「企业id」与对端主键语义一致；overlap
  ratio=0.9278（sample_size=263，miss=19），值域高度契合，判 likely。ratio_reverse=0.0 仅说明方向不对称（父表主键未全被引用），不否定该外键边。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_project_code_record__status]]（`cust_project_code_record.status`）
- [[dicts/cust_project_code_record__type]]（`cust_project_code_record.type`）
- [[dicts/cust_project_code_record__enable]]（`cust_project_code_record.enable`）
