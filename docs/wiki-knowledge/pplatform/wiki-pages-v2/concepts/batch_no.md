---
type: concept
title: 批次号（batch_no）
page_key: batch_no
domain: CA证书认证
status: draft
aliases: [batch_no, 批次流水号]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
maps_to: ca_certification_info.batch_no
field_targets:
  - ca_certification_info.batch_no
  - ca_certification_info.data_date
adjudication: boundary
also_confused_with:
  - ca_certification_info.data_date
belong: concepts
field_targets: [ca_certification_info.batch_no]
---

batch_no 是新建认证行时生成的一次性流水号，格式 INC_<yyyyMMddHHmmssSSS>_<6位hex>，总/分公司两行各自独立。

**边界（boundary）**：batch_no 是每次新建行的唯一流水号（INC_ 前缀），已从幂等键移除；幂等只依赖 cust_id+data_date+head_company_data+PENDING（见 [[incremental_idempotent_key]]）。因此它不能用于判断"是不是同一笔业务"，也不等同于 data_date：同一天可以有多行（两主体类型、状态不同），同一 batch_no 也不会跨日复用。

## 需求背景

定位一行数据的正确姿势是 (cust_id, data_date, head_company_data) 三元组 + [[submit_status]]，batch_no 只作为新建时刻的痕迹参考。

## 版本演进

- v0：首次记录 batch_no 退出幂等键这一变更，及其与 data_date 的语义差异。

关联页面：[[ca_certification_info]]、[[incremental_idempotent_key]]、[[incremental_idempotent_row]]、[[head_company_data]]。