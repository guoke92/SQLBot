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
related: [cust_company_info, cust_project_code_record__status, cust_project_code_record__company_type,
  cust_project_code_record__type, cust_project_code_record__enable, cust_project_code_record__app_tenant_code,
  cust_project_code_record__db_tenant_code]
---

# 企业项目码输入记录

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### project_code

`name`, `status`, `type`, `remark`

### company

`company_id`, `company_type`, `organization_id`

### tenant

`app_tenant_code`, `db_tenant_code`

### act_procinst

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### 未归簇

`use_id`, `channel_code`

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
- key: project_code
  title: 企业项目码信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_code_record
- key: company
  title: 企业与机构
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_code_record
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_project_code_record
- key: act_procinst
  title: 审批流程
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
  cluster: project_code
- name: company_id
  data_type: number
  description: 企业id
  cluster: company
- name: use_id
  data_type: number
  description: 用户id
- name: channel_code
  data_type: string
  description: 渠道码
- name: status
  data_type: string
  description: 是否正确状态
  cluster: project_code
  dictionary: cust_project_code_record__status
- name: company_type
  data_type: string
  description: 企业角色
  cluster: company
  dictionary: cust_project_code_record__company_type
- name: type
  data_type: string
  description: 类型
  cluster: project_code
  dictionary: cust_project_code_record__type
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_project_code_record__enable
- name: remark
  data_type: string
  description: remark
  cluster: project_code
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
  dictionary: cust_project_code_record__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
  dictionary: cust_project_code_record__db_tenant_code
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
  cluster: company
```

## 关联关系

### likely — 值域支持较强

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_project_code_record.company_id
cardinality: one_to_many
trust: proposed
authenticity: likely
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
authenticity_note: name_evidence 为 family_suffix（stem=company，注释「企业id」）；overlap 正向
  0.9278、反向 0.0，具备明显主表指向性，判为 likely，反向为 0 属子表侧多对一正常表现。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_project_code_record__status]]（`cust_project_code_record.status`）
- [[dicts/cust_project_code_record__company_type]]（`cust_project_code_record.company_type`）
- [[dicts/cust_project_code_record__type]]（`cust_project_code_record.type`）
- [[dicts/cust_project_code_record__enable]]（`cust_project_code_record.enable`）
- [[dicts/cust_project_code_record__app_tenant_code]]（`cust_project_code_record.app_tenant_code`）
- [[dicts/cust_project_code_record__db_tenant_code]]（`cust_project_code_record.db_tenant_code`）
