---
type: table
title: 建档推送运营记录表
page_key: cust_build_record
belong: tables
status: draft
aliases: []
anchors:
- cust_build_record
sources:
- database_schema:lowcode_pplatform.cust_build_record
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 建档推送运营记录表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### cust_identity

`name`, `cust_id`, `plat_cust_id`, `person_id`, `plat_person_id`

### push_payload

`push_data`, `return_data`, `remark`

### push_flow

`retry_status`, `channel`, `electronic_auth_sign_status`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant_org

`app_tenant_code`, `db_tenant_code`, `organization_id`

## 字段

```ground:table
table: cust_build_record
database: lowcode_pplatform
description: 建档推送运营记录表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
clusters:
- key: common
  title: 通用/审计字段
  include: always
- key: cust_identity
  title: 企业/联系人身份
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_build_record
- key: push_payload
  title: 推送与返回报文
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_build_record
- key: push_flow
  title: 推送渠道与状态
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_build_record
- key: workflow
  title: 审批流程实例
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_build_record
- key: tenant_org
  title: 租户与机构
  confidence: proposed
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
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: cust_identity
- name: cust_id
  data_type: number
  description: 企业ID
  nullable: true
  cluster: cust_identity
- name: plat_cust_id
  data_type: number
  description: 运营中台ID
  nullable: true
  cluster: cust_identity
- name: person_id
  data_type: number
  description: 联系人ID
  nullable: true
  cluster: cust_identity
- name: plat_person_id
  data_type: number
  description: 运营中台ID
  nullable: true
  cluster: cust_identity
- name: push_data
  data_type: string
  description: 推送json
  nullable: true
  cluster: push_payload
- name: return_data
  data_type: string
  description: 返回data
  nullable: true
  cluster: push_payload
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_build_record_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: push_payload
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
  cluster: tenant_org
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant_org
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
  cluster: tenant_org
- name: retry_status
  data_type: string
  description: 补偿重试状态：PENDING-待重试，RETRYING-重试中，SUCCESS-重试成功，FAILED-重试失败
  nullable: true
  cluster: push_flow
- name: channel
  data_type: string
  description: 渠道
  nullable: true
  cluster: push_flow
- name: electronic_auth_sign_status
  data_type: string
  description: ''
  nullable: true
  cluster: push_flow
  dictionary: cust_build_record_electronic_auth_sign_status
```
