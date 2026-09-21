---
type: table
title: 租户项目审批业务系统推送信息表
page_key: tenant_project_approval_business_info
belong: tables
status: draft
anchors: [tenant_project_approval_business_info]
sources: ['database_schema:lowcode_pplatform.tenant_project_approval_business_info',
  'code_path:ProjectApprovalApplication.java:1003']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_project_approval, tenant_product, tenant_project_approval_business_info__product_code,
  tenant_project_approval_business_info__source_system, tenant_project_approval_business_info__project_config_version,
  tenant_project_approval_business_info__asset_list_mode, tenant_project_approval_business_info__service_fee_min_amount,
  tenant_project_approval_business_info__review_fee, tenant_project_approval_business_info__enable]
---

# 租户项目审批业务系统推送信息表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: tenant_project_approval_business_info
database: lowcode_pplatform
desc: 租户项目审批业务系统推送信息表
inactive: false
primary_key: [id]
grain: 审批单业务系统推送配置
name_anchors: [code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: product_code
  type: string
  desc: 产品编码code
  dict: [ACFLOW, ORDER, RVSFACTOR_PC]
- name: source_system
  type: string
  desc: 来源系统
  dict: [ACFLOW, ORDER, RVSFACTOR_PC]
- name: project_config_version
  type: string
  desc: 项目配置版本
  dict: [config, configPro]
- name: attachment_json
  type: string
  desc: 附件列表 JSON
- name: asset_list_mode
  type: string
  desc: 资产清单模式
  dict: [STANDARD_LIST, SIMPLE_LIST]
- name: business_flow_mode
  type: string
  desc: 业务流程模式
- name: service_fee_collector_financing
  type: string
  desc: 服务费收取方
- name: service_fee_quote_type_financing
  type: string
  desc: 服务费报价类型
- name: service_fee_collect_method_financing
  type: string
  desc: 服务费收取方式
- name: payer
  type: string
  desc: 支付方
- name: quote_method
  type: string
  desc: 报价方式
- name: service_fee_min_amount
  type: string
  desc: 服务费低消金额
  dict: ['0', '200', '200.000000', '100', '201.000000', '2010.000000']
- name: service_fee_min_flag
  type: string
  desc: 服务费低消
- name: review_fee
  type: string
  desc: 审单费
  dict: ['0', '90', '198', '0.000000', '1.000000', '1.330000', '280', '1', '10.000000',
    '200', '110.000000']
- name: zhongdeng_register
  type: string
  desc: 中登登记
- name: ref_tenant_project_approval_business_info_project_approval
  type: string
  desc: 关联项目审批
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
  predicate: tenant_project_approval_business_info.enable = 'Y'
  trust: confirmed
  evidence: code_path:ProjectApprovalApplication.java:1003
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.code
right: tenant_project_approval_business_info.ref_tenant_project_approval_business_info_project_approval
cardinality: one_to_one
trust: confirmed
authenticity: likely
evidence: code_path:ProjectApprovalApplication.java:1003
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: none
  stem: ref_tenant_project_approval_business_info_project_approval
  comment: 关联项目审批
overlap:
  probed: true
  ratio: 1.0
  sample_size: 102
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 业务推送信息按审批 code。
```

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: tenant_product.code
right: tenant_project_approval_business_info.product_code
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.tenant_project_approval_business_info.product_code;database_profile:lowcode_pplatform.tenant_project_approval_business_info.product_code
source: name
join_role: business_code
priority: primary
name_evidence:
  match: family_suffix
  stem: product
  comment: 产品编码code
overlap:
  probed: true
  ratio: 0.0
  sample_size: 3
  miss: 3
  deepened: false
  query_ok: true
  authenticity: unlikely
```

## 页面链接

### 关联表

- [[tables/tenant_project_approval]]
- [[tables/tenant_product]]

### 字典

- [[dicts/tenant_project_approval_business_info__product_code]]（`tenant_project_approval_business_info.product_code`）
- [[dicts/tenant_project_approval_business_info__source_system]]（`tenant_project_approval_business_info.source_system`）
- [[dicts/tenant_project_approval_business_info__project_config_version]]（`tenant_project_approval_business_info.project_config_version`）
- [[dicts/tenant_project_approval_business_info__asset_list_mode]]（`tenant_project_approval_business_info.asset_list_mode`）
- [[dicts/tenant_project_approval_business_info__service_fee_min_amount]]（`tenant_project_approval_business_info.service_fee_min_amount`）
- [[dicts/tenant_project_approval_business_info__review_fee]]（`tenant_project_approval_business_info.review_fee`）
- [[dicts/tenant_project_approval_business_info__enable]]（`tenant_project_approval_business_info.enable`）
