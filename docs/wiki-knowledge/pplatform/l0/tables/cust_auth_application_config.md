---
type: table
title: 客户产品开通配置
page_key: cust_auth_application_config
belong: tables
status: draft
aliases: []
anchors:
- cust_auth_application_config
sources:
- database_schema:lowcode_pplatform.cust_auth_application_config
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 客户产品开通配置

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### basic_info

`name`, `remark`

### customer_org

`cust_id`, `organization_id`

### product_config

`product_sign_mode`, `product_protocol_agreement`, `needs_company_type_configuration`, `needs_product_agreement_configuration`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`ref_cust_auth_application_config_cust_auth_application`

## 字段

```ground:table
table: cust_auth_application_config
database: lowcode_pplatform
description: 客户产品开通配置
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
clusters:
- key: common
  title: 通用审计与编码
  include: always
- key: basic_info
  title: 基础信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_auth_application_config
- key: customer_org
  title: 客户与机构
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_auth_application_config
- key: product_config
  title: 产品开通配置
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_auth_application_config
- key: workflow
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_auth_application_config
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_auth_application_config
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: basic_info
- name: cust_id
  data_type: number
  description: 企业id
  nullable: true
  cluster: customer_org
- name: product_sign_mode
  data_type: string
  description: 产品协议签署方式
  nullable: true
  cluster: product_config
- name: product_protocol_agreement
  data_type: string
  description: 产品协议
  nullable: true
  cluster: product_config
- name: needs_company_type_configuration
  data_type: string
  description: 是否区分企业
  nullable: true
  cluster: product_config
- name: needs_product_agreement_configuration
  data_type: string
  description: 是否需要产品协议
  nullable: true
  cluster: product_config
- name: ref_cust_auth_application_config_cust_auth_application
  data_type: string
  description: 客户产品开通
  nullable: true
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: basic_info
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
  cluster: workflow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  nullable: true
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  nullable: true
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: workflow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: customer_org
```
