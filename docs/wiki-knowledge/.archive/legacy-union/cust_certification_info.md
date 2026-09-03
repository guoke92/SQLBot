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
title: 客户核查记录（一类型一行；含法人三要素/四要素/人脸/OCR 等 12 种； CFCA 人脸行 organization_id=ca_certification_info.id
  跨表暗链）。
page_key: cust_certification_info
domain: CA认证与服务费
aliases:
- cust_certification_info
anchors:
- cust_certification_info
---
# cust_certification_info

客户核查记录（一类型一行；含法人三要素/四要素/人脸/OCR 等 12 种； CFCA 人脸行 organization_id=ca_certification_info.id 跨表暗链）。

```ground:table
table: cust_certification_info
description: 客户核查记录（一类型一行；含法人三要素/四要素/人脸/OCR 等 12 种； CFCA 人脸行 organization_id=ca_certification_info.id
  跨表暗链）。
inactive: false
fields: []
```

```ground:relation
type: EQUI_JOIN
left: cust_certification_info.organization_id
right: ca_certification_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:ev-ca-cross-link
```
