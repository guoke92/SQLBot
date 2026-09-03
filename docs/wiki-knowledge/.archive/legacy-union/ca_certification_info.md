---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: table
title: CA 认证主记录（一行=一次报数尝试；分公司双行 N+Y；JSON 列存储各步骤结果； 全局共享不参与租户行过滤）。
page_key: ca_certification_info
domain: CA认证与服务费
aliases:
- ca_certification_info
anchors:
- ca_certification_info
---
# ca_certification_info

CA 认证主记录（一行=一次报数尝试；分公司双行 N+Y；JSON 列存储各步骤结果； 全局共享不参与租户行过滤）。

```ground:table
table: ca_certification_info
description: CA 认证主记录（一行=一次报数尝试；分公司双行 N+Y；JSON 列存储各步骤结果； 全局共享不参与租户行过滤）。
inactive: false
fields:
- name: cust_id
- name: data_source
- name: enterprise_four_json
- name: file_refs_json
- name: head_company_data
- name: intent_h5_face_json
- name: intent_sms_json
- name: notify_agreement_json
- name: police_two_json
- name: sign_platform_result
- name: submit_status
  dictionary: submit-status
- name: submit_time
```

```ground:relation
type: EQUI_JOIN
left: cust_certification_info.organization_id
right: ca_certification_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:ev-ca-cross-link
```
