---
type: table
title: 建档推送运营记录表
page_key: cust_build_record
belong: tables
status: draft
anchors: [cust_build_record]
sources: ['database_schema:lowcode_pplatform.cust_build_record']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_person_info, cust_build_record__enable, cust_build_record__electronic_auth_sign_status]
---

# 建档推送运营记录表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### subject_ref

`cust_id`, `person_id`, `organization_id`

### platform_ref

`plat_cust_id`, `plat_person_id`

### push_payload

`push_data`, `return_data`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### retry_channel

`retry_status`, `channel`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`electronic_auth_sign_status`

## 字段

```ground:table
table: cust_build_record
database: lowcode_pplatform
description: 建档推送运营记录表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: subject_ref
  title: 主体引用
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_build_record
- key: platform_ref
  title: 运营中台引用
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_build_record
- key: push_payload
  title: 推送与回执数据
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_build_record
- key: workflow
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_build_record
- key: retry_channel
  title: 重试与渠道
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_build_record
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_build_record
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
- name: cust_id
  data_type: number
  description: 企业ID
  cluster: subject_ref
- name: plat_cust_id
  data_type: number
  description: 运营中台ID
  cluster: platform_ref
- name: person_id
  data_type: number
  description: 联系人ID
  cluster: subject_ref
- name: plat_person_id
  data_type: number
  description: 运营中台ID
  cluster: platform_ref
- name: push_data
  data_type: string
  description: 推送json
  cluster: push_payload
- name: return_data
  data_type: string
  description: 返回data
  cluster: push_payload
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_build_record__enable
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
  cluster: subject_ref
- name: retry_status
  data_type: string
  description: 补偿重试状态：PENDING-待重试，RETRYING-重试中，SUCCESS-重试成功，FAILED-重试失败
  cluster: retry_channel
- name: channel
  data_type: string
  description: 渠道
  cluster: retry_channel
- name: electronic_auth_sign_status
  data_type: string
  dictionary: cust_build_record__electronic_auth_sign_status
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_build_record.cust_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.cust_build_record.cust_id;database_profile:lowcode_pplatform.cust_build_record.cust_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_hub
  stem: cust
  comment: 企业ID
overlap:
  probed: true
  ratio: 0.9699
  ratio_reverse: 0.58
  sample_size: 598
  miss: 18
  deepened: true
  query_ok: true
  authenticity: likely
authenticity_note: overlap 0.9699（反向 0.58，miss 18），列名族 hub 命中 stem=cust，本地注释「企业ID」，值域契合且语义关联，判
  likely。
```

```ground:relation
type: EQUI_JOIN
left: cust_person_info.id
right: cust_build_record.person_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.cust_build_record.person_id;database_profile:lowcode_pplatform.cust_build_record.person_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: person
  comment: 联系人ID
overlap:
  probed: true
  ratio: 0.9699
  ratio_reverse: 0.56
  sample_size: 599
  miss: 18
  deepened: true
  query_ok: true
  authenticity: likely
authenticity_note: overlap 0.9699（反向 0.56，miss 18），列名族后缀命中 stem=person，本地注释「联系人ID」，值域契合且语义关联，判
  likely。
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]
- [[tables/cust_person_info]]

### 字典

- [[dicts/cust_build_record__enable]]（`cust_build_record.enable`）
- [[dicts/cust_build_record__electronic_auth_sign_status]]（`cust_build_record.electronic_auth_sign_status`）
