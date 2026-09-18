---
type: table
title: CA认证信息
page_key: ca_certification_info
belong: tables
status: draft
anchors: [ca_certification_info]
sources: ['database_schema:lowcode_pplatform.ca_certification_info']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [ca_certification_info__cust_type, ca_certification_info__op_type, ca_certification_info__data_source,
  ca_certification_info__submit_status, ca_certification_info__enable, ca_certification_info__app_tenant_code,
  ca_certification_info__db_tenant_code, ca_certification_info__head_company_data]
---

# CA认证信息

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### audit

（空）

### cust

`cust_id`, `cust_type`

### cert_material

`notify_agreement_json`, `enterprise_four_json`, `police_two_json`, `file_refs_json`

### intent

`intent_sms_json`, `intent_h_face_json`

### submit

`submit_status`, `sign_platform_result`, `submit_time`

### process

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### etl

`data_date`, `op_type`, `batch_no`, `data_source`

### tenant

`app_tenant_code`, `db_tenant_code`

### org

`organization_id`, `head_company_data`

## 字段

```ground:table
table: ca_certification_info
database: lowcode_pplatform
description: CA认证信息
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
- key: audit
  title: 审计字段
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_certification_info
- key: cust
  title: 主体信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_certification_info
- key: cert_material
  title: 认证要素
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_certification_info
- key: intent
  title: 意愿核验
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_certification_info
- key: submit
  title: 提交结果
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_certification_info
- key: process
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_certification_info
- key: etl
  title: 数据同步信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_certification_info
- key: tenant
  title: 租户标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.ca_certification_info
- key: org
  title: 机构属性
  trust: proposed
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
  cluster: cust
- name: cust_type
  data_type: string
  description: PERSON / COMPANY
  cluster: cust
  dictionary: ca_certification_info__cust_type
- name: data_date
  data_type: string
  description: 数据时间
  cluster: etl
- name: op_type
  data_type: string
  description: INSERT / UPDATE
  cluster: etl
  dictionary: ca_certification_info__op_type
- name: batch_no
  data_type: string
  description: 批次号
  cluster: etl
- name: data_source
  data_type: string
  description: 数据来源
  cluster: etl
  dictionary: ca_certification_info__data_source
- name: notify_agreement_json
  data_type: string
  description: 协议通知
  cluster: cert_material
- name: enterprise_four_json
  data_type: string
  description: 企业四要素
  cluster: cert_material
- name: police_two_json
  data_type: string
  description: 实名 POLICE_TWO
  cluster: cert_material
- name: intent_sms_json
  data_type: string
  description: 意愿 SMS_CODE
  cluster: intent
- name: intent_h_face_json
  data_type: string
  description: 意愿 H5_FACE
  cluster: intent
- name: file_refs_json
  data_type: string
  description: 附件
  cluster: cert_material
- name: submit_status
  data_type: string
  description: PENDING / SUCCESS / FAIL
  cluster: submit
  dictionary: ca_certification_info__submit_status
- name: sign_platform_result
  data_type: string
  description: 中台返回结果
  cluster: submit
- name: submit_time
  data_type: temporal
  description: 提交时间
  cluster: submit
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
  dictionary: ca_certification_info__enable
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
  cluster: tenant
  dictionary: ca_certification_info__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant
  dictionary: ca_certification_info__db_tenant_code
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
  cluster: org
- name: head_company_data
  data_type: string
  description: 是否总公司
  cluster: org
  dictionary: ca_certification_info__head_company_data
```

## 页面链接

### 字典

- [[dicts/ca_certification_info__cust_type]]（`ca_certification_info.cust_type`）
- [[dicts/ca_certification_info__op_type]]（`ca_certification_info.op_type`）
- [[dicts/ca_certification_info__data_source]]（`ca_certification_info.data_source`）
- [[dicts/ca_certification_info__submit_status]]（`ca_certification_info.submit_status`）
- [[dicts/ca_certification_info__enable]]（`ca_certification_info.enable`）
- [[dicts/ca_certification_info__app_tenant_code]]（`ca_certification_info.app_tenant_code`）
- [[dicts/ca_certification_info__db_tenant_code]]（`ca_certification_info.db_tenant_code`）
- [[dicts/ca_certification_info__head_company_data]]（`ca_certification_info.head_company_data`）
