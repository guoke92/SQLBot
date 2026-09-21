---
type: table
title: cust_certification_info
page_key: cust_certification_info
belong: tables
status: draft
anchors: [cust_certification_info]
sources: ['database_schema:lowcode_pplatform.cust_certification_info']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_certification_info__enable, cust_certification_info__certification_type,
  cust_certification_info__auto_verify_status, cust_certification_info__auto_verify_count,
  cust_certification_info__manual_verify_status]
---

# cust_certification_info

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: cust_certification_info
database: lowcode_pplatform
desc: cust_certification_info
inactive: false
primary_key: []
grain: 一行一记录（?）
name_anchors: [code, name]
fields:
- name: id
  type: number
- name: code
  type: string
- name: name
  type: string
- name: enable
  type: string
  dict: [Y]
- name: remark
  type: string
- name: create_by
  type: string
- name: create_user
  type: string
- name: create_time
  type: temporal
- name: update_by
  type: string
- name: update_user
  type: string
- name: update_time
  type: temporal
- name: act_procinst_id
  type: string
- name: app_tenant_code
  type: string
- name: db_tenant_code
  type: string
- name: act_procinst_no
  type: string
- name: act_procinst_status
  type: string
- name: act_procinst_date
  type: temporal
- name: organization_id
  type: string
- name: ref_cust_company_info
  type: string
- name: certification_type
  type: string
  dict: [FACE_VERIFY, AUTH_THREE_ELEMENTS, LEGAL_REAL_NAME, LEGAL_THREE_ELEMENTS,
    COMPANY_TWO_ELEMENTS, LEGAL_OCR, AUTH_MEDIA_OCR]
- name: auto_verify_status
  type: string
  dict: [AUTOMATIC_AUTHENTICATION_PASSED, TO_BE_VERIFIED, AUTOMATIC_AUTHENTICATION_FAILED]
- name: auto_verify_msg
  type: string
- name: auto_verify_time
  type: temporal
- name: auto_verify_count
  type: number
  dict: ['0', '1', '2', '4', '3', '5', '6', '7', '8', '-1', '11', '9', '33', '-3',
    '10', '13', '15', '21', '18', '22', '16', '-7']
- name: auto_verify_data
  type: string
- name: manual_verify_status
  type: string
  dict: [MANUAL_AUTHENTICATION_PASSED]
- name: manual_verify_msg
  type: string
- name: manual_verify_time
  type: temporal
- name: manual_verify_count
  type: number
- name: face_business_no
  type: string
- name: verify_score
  type: number
```

## 关联关系

### unlikely — 值域不支持或冲突

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_certification_info.ref_cust_company_info
cardinality: one_to_many
trust: proposed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_certification_info.ref_cust_company_info;database_profile:lowcode_pplatform.cust_certification_info.ref_cust_company_info
source: name
join_role: identity
priority: primary
name_evidence:
  match: exact_table
  stem: cust_company_info
overlap:
  probed: true
  ratio: 0.0
  sample_size: 104
  miss: 104
  deepened: false
  query_ok: true
  authenticity: unlikely
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_certification_info__enable]]（`cust_certification_info.enable`）
- [[dicts/cust_certification_info__certification_type]]（`cust_certification_info.certification_type`）
- [[dicts/cust_certification_info__auto_verify_status]]（`cust_certification_info.auto_verify_status`）
- [[dicts/cust_certification_info__auto_verify_count]]（`cust_certification_info.auto_verify_count`）
- [[dicts/cust_certification_info__manual_verify_status]]（`cust_certification_info.manual_verify_status`）
