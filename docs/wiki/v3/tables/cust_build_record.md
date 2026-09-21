---
type: table
title: 建档推送运营记录表
page_key: cust_build_record
belong: tables
status: draft
anchors: [cust_build_record]
sources: ['database_schema:lowcode_pplatform.cust_build_record']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_person_info, cust_build_record__enable, cust_build_record__electronic_auth_sign_status]
---

# 建档推送运营记录表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_build_record
database: lowcode_pplatform
desc: 建档推送运营记录表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 名称
- name: cust_id
  type: number
  desc: 企业ID
- name: plat_cust_id
  type: number
  desc: 运营中台ID
- name: person_id
  type: number
  desc: 联系人ID
- name: plat_person_id
  type: number
  desc: 运营中台ID
- name: push_data
  type: string
  desc: 推送json
- name: return_data
  type: string
  desc: 返回data
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
- name: retry_status
  type: string
  desc: 补偿重试状态：PENDING-待重试，RETRYING-重试中，SUCCESS-重试成功，FAILED-重试失败
- name: channel
  type: string
  desc: 渠道
- name: electronic_auth_sign_status
  type: string
  dict: [SIGNED, PENDING, UPLOAD_FAILED, FAILED, VOIDED]
  label: [已签署, 待签署, 影像上传失败, 签署失败, 作废]
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_build_record.cust_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:OperCustFacade.java:4288
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_hub
  stem: cust
  comment: 企业ID
overlap:
  probed: true
  ratio: 0.9699
  ratio_reverse: 0.58
  sample_size: 598
  miss: 18
  deepened: true
  query_ok: true
  authenticity: likely
authenticity_note: 建档推送记录的 cust_id 是企业主键。
```

```ground:relation
type: EQUI_JOIN
left: cust_person_info.id
right: cust_build_record.person_id
cardinality: one_to_many
trust: proposed
authenticity: likely
evidence: database_schema:lowcode_pplatform.cust_build_record.person_id;database_profile:lowcode_pplatform.cust_build_record.person_id
source: name
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: person
  comment: 联系人ID
overlap:
  probed: true
  ratio: 0.9699
  ratio_reverse: 0.56
  sample_size: 599
  miss: 18
  deepened: true
  query_ok: true
  authenticity: likely
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]
- [[tables/cust_person_info]]

### 字典

- [[dicts/cust_build_record__enable]]（`cust_build_record.enable`）
- [[dicts/cust_build_record__electronic_auth_sign_status]]（`cust_build_record.electronic_auth_sign_status`）
