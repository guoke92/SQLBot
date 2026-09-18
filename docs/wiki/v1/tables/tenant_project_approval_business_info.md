---
type: table
title: 租户项目审批业务系统推送信息表
page_key: tenant_project_approval_business_info
belong: tables
status: draft
anchors: [tenant_project_approval_business_info]
sources: ['database_schema:lowcode_pplatform.tenant_project_approval_business_info']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_product, tenant_project_approval, tenant_project_approval_business_info__product_code,
  tenant_project_approval_business_info__source_system, tenant_project_approval_business_info__project_config_version,
  tenant_project_approval_business_info__asset_list_mode, tenant_project_approval_business_info__business_flow_mode,
  tenant_project_approval_business_info__service_fee_collector_financing, tenant_project_approval_business_info__service_fee_quote_type_financing,
  tenant_project_approval_business_info__service_fee_collect_method_financing, tenant_project_approval_business_info__payer,
  tenant_project_approval_business_info__service_fee_min_amount, tenant_project_approval_business_info__service_fee_min_flag,
  tenant_project_approval_business_info__review_fee, tenant_project_approval_business_info__zhongdeng_register,
  tenant_project_approval_business_info__enable, tenant_project_approval_business_info__app_tenant_code,
  tenant_project_approval_business_info__db_tenant_code]
---

# 租户项目审批业务系统推送信息表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### product_source

`product_code`, `source_system`, `project_config_version`, `attachment_json`, `asset_list_mode`, `business_flow_mode`, `zhongdeng_register`

### fee

`service_fee_collector_financing`, `service_fee_quote_type_financing`, `service_fee_collect_method_financing`, `payer`, `quote_method`, `service_fee_min_amount`, `service_fee_min_flag`, `review_fee`

### approval

`ref_tenant_project_approval_business_info_project_approval`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant_org

`app_tenant_code`, `db_tenant_code`, `organization_id`

## 字段

```ground:table
table: tenant_project_approval_business_info
database: lowcode_pplatform
description: 租户项目审批业务系统推送信息表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: product_source
  title: 产品与来源及项目配置
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_business_info
- key: fee
  title: 服务费与报价
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_business_info
- key: approval
  title: 项目审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_business_info
- key: tenant_org
  title: 租户与机构
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_business_info
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: product_code
  data_type: string
  description: 产品编码code
  cluster: product_source
  dictionary: tenant_project_approval_business_info__product_code
- name: source_system
  data_type: string
  description: 来源系统
  cluster: product_source
  dictionary: tenant_project_approval_business_info__source_system
- name: project_config_version
  data_type: string
  description: 项目配置版本
  cluster: product_source
  dictionary: tenant_project_approval_business_info__project_config_version
- name: attachment_json
  data_type: string
  description: 附件列表 JSON
  cluster: product_source
- name: asset_list_mode
  data_type: string
  description: 资产清单模式
  cluster: product_source
  dictionary: tenant_project_approval_business_info__asset_list_mode
- name: business_flow_mode
  data_type: string
  description: 业务流程模式
  cluster: product_source
  dictionary: tenant_project_approval_business_info__business_flow_mode
- name: service_fee_collector_financing
  data_type: string
  description: 服务费收取方
  cluster: fee
  dictionary: tenant_project_approval_business_info__service_fee_collector_financing
- name: service_fee_quote_type_financing
  data_type: string
  description: 服务费报价类型
  cluster: fee
  dictionary: tenant_project_approval_business_info__service_fee_quote_type_financing
- name: service_fee_collect_method_financing
  data_type: string
  description: 服务费收取方式
  cluster: fee
  dictionary: tenant_project_approval_business_info__service_fee_collect_method_financing
- name: payer
  data_type: string
  description: 支付方
  cluster: fee
  dictionary: tenant_project_approval_business_info__payer
- name: quote_method
  data_type: string
  description: 报价方式
  cluster: fee
- name: service_fee_min_amount
  data_type: string
  description: 服务费低消金额
  cluster: fee
  dictionary: tenant_project_approval_business_info__service_fee_min_amount
- name: service_fee_min_flag
  data_type: string
  description: 服务费低消
  cluster: fee
  dictionary: tenant_project_approval_business_info__service_fee_min_flag
- name: review_fee
  data_type: string
  description: 审单费
  cluster: fee
  dictionary: tenant_project_approval_business_info__review_fee
- name: zhongdeng_register
  data_type: string
  description: 中登登记
  cluster: product_source
  dictionary: tenant_project_approval_business_info__zhongdeng_register
- name: ref_tenant_project_approval_business_info_project_approval
  data_type: string
  description: 关联项目审批
  cluster: approval
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
  dictionary: tenant_project_approval_business_info__enable
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
  cluster: approval
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: tenant_org
  dictionary: tenant_project_approval_business_info__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant_org
  dictionary: tenant_project_approval_business_info__db_tenant_code
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: approval
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: tenant_org
```

## 关联关系

### likely — 值域支持较强

```ground:relation
type: EQUI_JOIN
left: tenant_project_approval.code
right: tenant_project_approval_business_info.ref_tenant_project_approval_business_info_project_approval
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_profile:lowcode_pplatform.tenant_project_approval_business_info.ref_tenant_project_approval_business_info_project_approval
source: overlap
join_role: business_code
priority: primary
name_evidence:
  match: none
overlap:
  probed: true
  ratio: 1.0
  sample_size: 102
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 列名为外键式引用名（ref_..._project_approval，注释「关联项目审批」），实测重叠率 1.0（102 样本全命中），判定为指向项目审批主档
  code 的引用边。
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
authenticity_note: 名称同族（product 后缀）且本列注释为「产品编码code」，但实测重叠率 0.0（3 样本全部未命中），产品编码体系可能不同或跨库不可比，暂判
  unlikely。
```

## 页面链接

### 关联表

- [[tables/tenant_product]]
- [[tables/tenant_project_approval]]

### 字典

- [[dicts/tenant_project_approval_business_info__product_code]]（`tenant_project_approval_business_info.product_code`）
- [[dicts/tenant_project_approval_business_info__source_system]]（`tenant_project_approval_business_info.source_system`）
- [[dicts/tenant_project_approval_business_info__project_config_version]]（`tenant_project_approval_business_info.project_config_version`）
- [[dicts/tenant_project_approval_business_info__asset_list_mode]]（`tenant_project_approval_business_info.asset_list_mode`）
- [[dicts/tenant_project_approval_business_info__business_flow_mode]]（`tenant_project_approval_business_info.business_flow_mode`）
- [[dicts/tenant_project_approval_business_info__service_fee_collector_financing]]（`tenant_project_approval_business_info.service_fee_collector_financing`）
- [[dicts/tenant_project_approval_business_info__service_fee_quote_type_financing]]（`tenant_project_approval_business_info.service_fee_quote_type_financing`）
- [[dicts/tenant_project_approval_business_info__service_fee_collect_method_financing]]（`tenant_project_approval_business_info.service_fee_collect_method_financing`）
- [[dicts/tenant_project_approval_business_info__payer]]（`tenant_project_approval_business_info.payer`）
- [[dicts/tenant_project_approval_business_info__service_fee_min_amount]]（`tenant_project_approval_business_info.service_fee_min_amount`）
- [[dicts/tenant_project_approval_business_info__service_fee_min_flag]]（`tenant_project_approval_business_info.service_fee_min_flag`）
- [[dicts/tenant_project_approval_business_info__review_fee]]（`tenant_project_approval_business_info.review_fee`）
- [[dicts/tenant_project_approval_business_info__zhongdeng_register]]（`tenant_project_approval_business_info.zhongdeng_register`）
- [[dicts/tenant_project_approval_business_info__enable]]（`tenant_project_approval_business_info.enable`）
- [[dicts/tenant_project_approval_business_info__app_tenant_code]]（`tenant_project_approval_business_info.app_tenant_code`）
- [[dicts/tenant_project_approval_business_info__db_tenant_code]]（`tenant_project_approval_business_info.db_tenant_code`）
