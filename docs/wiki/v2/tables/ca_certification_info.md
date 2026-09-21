---
type: table
title: CA认证信息
page_key: ca_certification_info
belong: tables
status: draft
anchors: [ca_certification_info]
sources: ['database_schema:lowcode_pplatform.ca_certification_info']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [ca_certification_info__cust_type, ca_certification_info__op_type, ca_certification_info__data_source,
  ca_certification_info__submit_status, ca_certification_info__enable, ca_certification_info__head_company_data]
---

# CA认证信息

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: ca_certification_info
database: lowcode_pplatform
desc: CA认证信息
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: cust_id
  type: number
  desc: 企业Id
- name: cust_type
  type: string
  desc: PERSON / COMPANY
  dict: [COMPANY]
- name: data_date
  type: string
  desc: 数据时间
- name: op_type
  type: string
  desc: INSERT / UPDATE
  dict: [INSERT]
- name: batch_no
  type: string
  desc: 批次号
- name: data_source
  type: string
  desc: 数据来源
  dict: [FBP_PORTAL, OPERATION_PLATFORM, CHANNEL_OPENAPI]
- name: notify_agreement_json
  type: string
  desc: 协议通知
- name: enterprise_four_json
  type: string
  desc: 企业四要素
- name: police_two_json
  type: string
  desc: 实名 POLICE_TWO
- name: intent_sms_json
  type: string
  desc: 意愿 SMS_CODE
- name: intent_h_face_json
  type: string
  desc: 意愿 H5_FACE
- name: file_refs_json
  type: string
  desc: 附件
- name: submit_status
  type: string
  desc: PENDING / SUCCESS / FAIL
  dict: [SUCCESS, PENDING, FAIL]
- name: sign_platform_result
  type: string
  desc: 中台返回结果
- name: submit_time
  type: temporal
  desc: 提交时间
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
- name: head_company_data
  type: string
  desc: 是否总公司
  dict: [N, Y]
```

## 页面链接

### 字典

- [[dicts/ca_certification_info__cust_type]]（`ca_certification_info.cust_type`）
- [[dicts/ca_certification_info__op_type]]（`ca_certification_info.op_type`）
- [[dicts/ca_certification_info__data_source]]（`ca_certification_info.data_source`）
- [[dicts/ca_certification_info__submit_status]]（`ca_certification_info.submit_status`）
- [[dicts/ca_certification_info__enable]]（`ca_certification_info.enable`）
- [[dicts/ca_certification_info__head_company_data]]（`ca_certification_info.head_company_data`）
