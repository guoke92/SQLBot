---
type: table
title: CA服务费项目配置
page_key: ca_fee_project_config
belong: tables
status: draft
anchors: [ca_fee_project_config]
sources: ['database_schema:lowcode_pplatform.ca_fee_project_config', 'code_path:CaFeeProjectConfigBizMapper.java:13']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [ca_fee_company, ca_fee_order, tenant_project, tenant_setting_config, ca_fee_project_config__charge_enabled,
  ca_fee_project_config__enable]
---

# CA服务费项目配置

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: ca_fee_project_config
database: lowcode_pplatform
desc: CA服务费项目配置
inactive: false
primary_key: [id]
grain: 一租户项目一行收费配置
name_anchors: [code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: project_id
  type: number
  desc: 项目ID
- name: tenant_id
  type: number
  desc: 所属租户
- name: charge_enabled
  type: string
  desc: 是否开启CA收费
  dict: [N, Y]
  written_with: [last_toggle_time]
- name: supplier_annual_fee
  type: number
  desc: 供应商角色年费（元）
- name: core_annual_fee
  type: number
  desc: 核心企业角色年费（元）
- name: pay_channel
  type: string
  desc: 缴费渠道JSON数组
- name: special_company_list
  type: string
  desc: 特殊企业配置JSON数组
- name: block_scene_list
  type: string
  desc: 拦截场景编码 JSON 数组，元素见 CaFeeInterceptSceneEnum
- name: agreement_version
  type: string
  desc: 当前绑定收费协议版本号
- name: last_toggle_time
  type: temporal
  desc: 最近一次收费开关切换时间
  written_with: [charge_enabled]
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
default_filter:
  predicate: ca_fee_project_config.enable = 'Y'
  trust: confirmed
  evidence: code_path:CaFeeProjectConfigBizMapper.java:13
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: tenant_project.id
right: ca_fee_project_config.project_id
cardinality: one_to_one
trust: confirmed
authenticity: likely
evidence: code_path:cafee/CaFeeProjectConfigService.java:296
source: l1_code
join_role: identity
priority: primary
authenticity_note: 项目配置按 tenant_project 主键，一项目一行。
```

```ground:relation
type: EQUI_JOIN
left: tenant_setting_config.id
right: ca_fee_project_config.tenant_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:cafee/CaFeeProjectConfigService.java:236
source: l1_code
join_role: identity
priority: primary
authenticity_note: 新建配置写 tenant_id=项目上的租户主键。
```

## 页面链接

### 关联表

- [[tables/ca_fee_company]]
- [[tables/ca_fee_order]]
- [[tables/tenant_project]]
- [[tables/tenant_setting_config]]

### 字典

- [[dicts/ca_fee_project_config__charge_enabled]]（`ca_fee_project_config.charge_enabled`）
- [[dicts/ca_fee_project_config__enable]]（`ca_fee_project_config.enable`）
