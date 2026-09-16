---
type: table
title: CA认证信息
page_key: ca_certification_info
belong: tables
status: draft
aliases: []
anchors:
- ca_certification_info
sources:
- database_schema:lowcode_pplatform.ca_certification_info
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# CA认证信息

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### subject

`cust_id`, `cust_type`, `name`, `organization_id`, `head_company_data`

### sync

`data_date`, `op_type`, `batch_no`, `data_source`

### cert_payload

`notify_agreement_json`, `enterprise_four_json`, `police_two_json`, `file_refs_json`

### intent

`intent_sms_json`, `intent_h_face_json`

### submit

`submit_status`, `sign_platform_result`, `submit_time`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### tenant

`app_tenant_code`, `db_tenant_code`

### 未归簇

`remark`

## 字段

```ground:table
table: ca_certification_info
database: lowcode_pplatform
description: CA认证信息
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
clusters:
- key: common
  title: 通用/审计
  include: always
- key: subject
  title: 认证主体信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_certification_info
- key: sync
  title: 数据同步批次
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_certification_info
- key: cert_payload
  title: 认证要素与协议
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_certification_info
- key: intent
  title: 意愿认证
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_certification_info
- key: submit
  title: 提交与中台结果
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_certification_info
- key: workflow
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_certification_info
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.ca_certification_info
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: cust_id
  data_type: number
  description: 企业Id
  nullable: true
  cluster: subject
- name: cust_type
  data_type: string
  description: PERSON / COMPANY
  nullable: true
  cluster: subject
  dictionary: ca_certification_info_cust_type
- name: data_date
  data_type: string
  description: 数据时间
  nullable: true
  cluster: sync
- name: op_type
  data_type: string
  description: INSERT / UPDATE
  nullable: true
  cluster: sync
  dictionary: ca_certification_info_op_type
- name: batch_no
  data_type: string
  description: 批次号
  nullable: true
  cluster: sync
- name: data_source
  data_type: string
  description: 数据来源
  nullable: true
  cluster: sync
  dictionary: ca_certification_info_data_source
- name: notify_agreement_json
  data_type: string
  description: 协议通知
  nullable: true
  cluster: cert_payload
- name: enterprise_four_json
  data_type: string
  description: 企业四要素
  nullable: true
  cluster: cert_payload
- name: police_two_json
  data_type: string
  description: 实名 POLICE_TWO
  nullable: true
  cluster: cert_payload
- name: intent_sms_json
  data_type: string
  description: 意愿 SMS_CODE
  nullable: true
  cluster: intent
- name: intent_h_face_json
  data_type: string
  description: 意愿 H5_FACE
  nullable: true
  cluster: intent
- name: file_refs_json
  data_type: string
  description: 附件
  nullable: true
  cluster: cert_payload
- name: submit_status
  data_type: string
  description: PENDING / SUCCESS / FAIL
  nullable: true
  cluster: submit
  dictionary: ca_certification_info_submit_status
- name: sign_platform_result
  data_type: string
  description: 中台返回结果
  nullable: true
  cluster: submit
- name: submit_time
  data_type: temporal
  description: 提交时间
  nullable: true
  cluster: submit
- name: code
  data_type: string
  description: 编码
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 名称
  nullable: true
  cluster: subject
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: ca_certification_info_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
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
  cluster: subject
- name: head_company_data
  data_type: string
  description: 是否总公司
  nullable: true
  cluster: subject
  dictionary: ca_certification_info_head_company_data
```
