---
type: table
title: 项目立项字段更新历史
page_key: wechat_project_approval_field_history
belong: tables
status: draft
anchors: [wechat_project_approval_field_history]
sources: ['database_schema:lowcode_pplatform.wechat_project_approval_field_history']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [wechat_project_approval_apply, wechat_project_approval_field_history__field_name,
  wechat_project_approval_field_history__field_label, wechat_project_approval_field_history__change_source,
  wechat_project_approval_field_history__enable]
---

# 项目立项字段更新历史

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`, `app_tenant_code`, `db_tenant_code`

### change_content

`field_name`, `field_label`, `old_value`, `new_value`, `change_source`

### operator

`operator_id`, `operator_name`

### process

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### business_link

`apply_id`, `sp_no`, `organization_id`

## 字段

```ground:table
table: wechat_project_approval_field_history
database: lowcode_pplatform
description: 项目立项字段更新历史
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [field_name, operator_name, code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: change_content
  title: 字段变更内容
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_field_history
- key: operator
  title: 操作人
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_field_history
- key: process
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_field_history
- key: business_link
  title: 立项业务关联
  trust: proposed
  evidence: database_schema:lowcode_pplatform.wechat_project_approval_field_history
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: apply_id
  data_type: number
  description: 关联 wechat_project_approval_apply.id
  cluster: business_link
- name: sp_no
  data_type: string
  description: 审批编号
  cluster: business_link
- name: field_name
  data_type: string
  description: 列名
  cluster: change_content
  dictionary: wechat_project_approval_field_history__field_name
- name: field_label
  data_type: string
  description: 中文标签
  cluster: change_content
  dictionary: wechat_project_approval_field_history__field_label
- name: old_value
  data_type: string
  description: 变更前值
  cluster: change_content
- name: new_value
  data_type: string
  description: 变更后值
  cluster: change_content
- name: change_source
  data_type: string
  description: 变更来源
  cluster: change_content
  dictionary: wechat_project_approval_field_history__change_source
- name: operator_id
  data_type: string
  description: 操作人ID
  cluster: operator
- name: operator_name
  data_type: string
  description: 操作人姓名
  cluster: operator
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
  dictionary: wechat_project_approval_field_history__enable
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
  cluster: process
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
  cluster: process
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: process
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: process
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: business_link
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: wechat_project_approval_apply.id
right: wechat_project_approval_field_history.apply_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.wechat_project_approval_field_history.apply_id;database_profile:lowcode_pplatform.wechat_project_approval_field_history.apply_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: apply
  comment: 关联 wechat_project_approval_apply.id
overlap:
  probed: true
  ratio: 1.0
  sample_size: 23
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: apply_id 注释显式写明「关联 wechat_project_approval_apply.id」，name_evidence
  为 family_suffix(stem=apply)；overlap 已探测 ratio=1.0、sample_size=23、miss=0，值域完全契合，判定子表→父表外键为
  likely
```

## 页面链接

### 关联表

- [[tables/wechat_project_approval_apply]]

### 字典

- [[dicts/wechat_project_approval_field_history__field_name]]（`wechat_project_approval_field_history.field_name`）
- [[dicts/wechat_project_approval_field_history__field_label]]（`wechat_project_approval_field_history.field_label`）
- [[dicts/wechat_project_approval_field_history__change_source]]（`wechat_project_approval_field_history.change_source`）
- [[dicts/wechat_project_approval_field_history__enable]]（`wechat_project_approval_field_history.enable`）
