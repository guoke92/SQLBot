---
type: table
title: 项目立项字段更新历史
page_key: wechat_project_approval_field_history
belong: tables
status: draft
anchors: [wechat_project_approval_field_history]
sources: ['database_schema:lowcode_pplatform.wechat_project_approval_field_history']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [wechat_project_approval_apply, wechat_project_approval_field_history__field_name,
  wechat_project_approval_field_history__change_source, wechat_project_approval_field_history__operator_name,
  wechat_project_approval_field_history__enable]
---

# 项目立项字段更新历史

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: wechat_project_approval_field_history
database: lowcode_pplatform
desc: 项目立项字段更新历史
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [field_name, operator_name, code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: apply_id
  type: number
  desc: 关联 wechat_project_approval_apply.id
- name: sp_no
  type: string
  desc: 审批编号
- name: field_name
  type: string
  desc: 列名
  dict: [solution_manager, project_phase, business_center, project_type, bussiness_manager,
    main_project_name, project_approval_name, apply_start_time, product_type, enterprise_full_name,
    product_type_arr, act_procinst_status, capital_branch_name, capital_org_full_name,
    ka_white_label, prd, first_settlement_time, system_delivery, old_solution_manager,
    sp_pass_time, comment, project_focus_level, project_exception_remark, custom_field_statistics_one,
    data_source]
- name: field_label
  type: string
  desc: 中文标签
- name: old_value
  type: string
  desc: 变更前值
- name: new_value
  type: string
  desc: 变更后值
- name: change_source
  type: string
  desc: 变更来源
  dict: [SYNC, EDIT, MANUAL_CREATE, IMPORT, BATCH]
- name: operator_id
  type: string
  desc: 操作人ID
- name: operator_name
  type: string
  desc: 操作人姓名
  dict: [system-sync, liuning, linyanxiang, FDPAdmin, ouyangpengfei, xiaolonghao,
    chenkaiwen, liubeicai, caiweicheng, chenzerong, liuhaiou, huangliyu3]
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: enable
  type: string
  desc: enable
  dict: [Y]
- name: remark
  type: string
  desc: remark
- name: create_by
  type: string
  desc: 创建人id
- name: create_user
  type: string
  desc: 创建人名称
- name: create_time
  type: temporal
  desc: 创建时间
  nullable: false
- name: update_by
  type: string
  desc: 更新人id
- name: update_user
  type: string
  desc: 更新人名称
- name: update_time
  type: temporal
  desc: 更新时间
  nullable: false
- name: act_procinst_id
  type: string
  desc: 流程实例ID
- name: app_tenant_code
  type: string
  desc: 逻辑租户标识
- name: db_tenant_code
  type: string
  desc: 数据租户标识
- name: act_procinst_no
  type: string
  desc: 流程申请编号
- name: act_procinst_status
  type: string
  desc: 当前审批状态
- name: act_procinst_date
  type: temporal
  desc: 审批结束时间
- name: organization_id
  type: string
  desc: 机构编号
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
```

## 页面链接

### 关联表

- [[tables/wechat_project_approval_apply]]

### 字典

- [[dicts/wechat_project_approval_field_history__field_name]]（`wechat_project_approval_field_history.field_name`）
- [[dicts/wechat_project_approval_field_history__change_source]]（`wechat_project_approval_field_history.change_source`）
- [[dicts/wechat_project_approval_field_history__operator_name]]（`wechat_project_approval_field_history.operator_name`）
- [[dicts/wechat_project_approval_field_history__enable]]（`wechat_project_approval_field_history.enable`）
