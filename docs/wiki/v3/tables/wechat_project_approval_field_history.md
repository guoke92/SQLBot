---
type: table
title: 项目立项字段更新历史
page_key: wechat_project_approval_field_history
belong: tables
status: draft
anchors: [wechat_project_approval_field_history]
sources: ['database_schema:lowcode_pplatform.wechat_project_approval_field_history']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [wechat_project_approval_apply, wechat_project_approval_field_history__field_name,
  wechat_project_approval_field_history__field_label, wechat_project_approval_field_history__change_source,
  wechat_project_approval_field_history__enable]
---

# 项目立项字段更新历史

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: wechat_project_approval_field_history
database: lowcode_pplatform
desc: 项目立项字段更新历史
inactive: false
primary_key: [id]
grain: 企微审批字段历史
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
  dict: [solution_manager, project_phase, project_type, business_center, bussiness_manager,
    main_project_name, project_approval_name, apply_start_time, product_type, enterprise_full_name,
    act_procinst_status, product_type_arr, capital_branch_name, capital_org_full_name,
    ka_white_label, prd, first_settlement_time, system_delivery, sp_pass_time, old_solution_manager,
    comment, project_focus_level, project_exception_remark, custom_field_statistics_one,
    data_source]
- name: field_label
  type: string
  desc: 中文标签
  dict: [方案经理, 项目阶段, 产品类型, 项目类型, 业务中心, 业务经理, 主项目名称, 立项名称, 发起立项时间, 企业全称, 当前审批状态, 资方分支行,
    资方全称, KA是否贴牌, 是否投产, 首笔放款时间, 系统交付方式, 立项审批通过时间, 前方案经理, 备注, 项目投入关注度, 项目异常备注, 自定义字段一(统计用),
    数据来源]
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
trust: confirmed
authenticity: likely
evidence: code_path:FieldHistoryWriter.java:78
source: l1_code
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
