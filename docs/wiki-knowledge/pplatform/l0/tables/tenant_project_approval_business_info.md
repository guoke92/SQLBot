---
type: table
title: 租户项目审批业务系统推送信息表
page_key: tenant_project_approval_business_info
belong: tables
status: draft
aliases: []
anchors:
- tenant_project_approval_business_info
sources:
- database_schema:lowcode_pplatform.tenant_project_approval_business_info
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 租户项目审批业务系统推送信息表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### push_payload

`product_code`, `source_system`, `project_config_version`, `attachment_json`

### asset_mode

`asset_list_mode`, `business_flow_mode`

### service_fee

`service_fee_collector_financing`, `service_fee_quote_type_financing`, `service_fee_collect_method_financing`, `service_fee_min_amount`, `service_fee_min_flag`

### fee_terms

`payer`, `quote_method`, `review_fee`, `zhongdeng_register`

### approval_flow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant_scope

`app_tenant_code`, `db_tenant_code`, `organization_id`

### descriptive

`name`, `remark`

### 未归簇

`ref_tenant_project_approval_business_info_project_approval`

## 字段

```ground:table
table: tenant_project_approval_business_info
database: lowcode_pplatform
description: 租户项目审批业务系统推送信息表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- product_code
- code
- name
clusters:
- key: common
  title: 通用/审计
  include: always
- key: push_payload
  title: 推送来源与内容
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_business_info
- key: asset_mode
  title: 业务与资产模式
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_business_info
- key: service_fee
  title: 服务费要素
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_business_info
- key: fee_terms
  title: 费用与报价相关
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_business_info
- key: approval_flow
  title: 审批流程实例
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_business_info
- key: tenant_scope
  title: 租户与机构归属
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_project_approval_business_info
- key: descriptive
  title: 名称与备注
  confidence: proposed
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
  nullable: true
  cluster: push_payload
  dictionary: tenant_project_approval_business_info_product_code
- name: source_system
  data_type: string
  description: 来源系统
  nullable: true
  cluster: push_payload
  dictionary: tenant_project_approval_business_info_source_system
- name: project_config_version
  data_type: string
  description: 项目配置版本
  nullable: true
  cluster: push_payload
- name: attachment_json
  data_type: string
  description: 附件列表 JSON
  nullable: true
  cluster: push_payload
- name: asset_list_mode
  data_type: string
  description: 资产清单模式
  nullable: true
  cluster: asset_mode
  dictionary: tenant_project_approval_business_info_asset_list_mode
- name: business_flow_mode
  data_type: string
  description: 业务流程模式
  nullable: true
  cluster: asset_mode
- name: service_fee_collector_financing
  data_type: string
  description: 服务费收取方
  nullable: true
  cluster: service_fee
- name: service_fee_quote_type_financing
  data_type: string
  description: 服务费报价类型
  nullable: true
  cluster: service_fee
- name: service_fee_collect_method_financing
  data_type: string
  description: 服务费收取方式
  nullable: true
  cluster: service_fee
- name: payer
  data_type: string
  description: 支付方
  nullable: true
  cluster: fee_terms
- name: quote_method
  data_type: string
  description: 报价方式
  nullable: true
  cluster: fee_terms
- name: service_fee_min_amount
  data_type: string
  description: 服务费低消金额
  nullable: true
  cluster: service_fee
- name: service_fee_min_flag
  data_type: string
  description: 服务费低消
  nullable: true
  cluster: service_fee
- name: review_fee
  data_type: string
  description: 审单费
  nullable: true
  cluster: fee_terms
- name: zhongdeng_register
  data_type: string
  description: 中登登记
  nullable: true
  cluster: fee_terms
- name: ref_tenant_project_approval_business_info_project_approval
  data_type: string
  description: 关联项目审批
  nullable: true
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: descriptive
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: tenant_project_approval_business_info_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: descriptive
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
  cluster: approval_flow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  nullable: true
  cluster: tenant_scope
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant_scope
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  nullable: true
  cluster: approval_flow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval_flow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval_flow
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: tenant_scope
```
