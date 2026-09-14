---
type: caliber
title: 增量落库幂等键
page_key: incremental_idempotent_key
domain: CA证书认证
status: draft
aliases: [幂等键, createOrGetByKey 口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
belong: calibers
---

认定"这一行是不是已存在的行"的口径：命中条件为 (cust_id, data_date, head_company_data, submit_status=PENDING)，batch_no 不参与。命中即复用旧行，未命中才新建并生成 batch_no。由此产生两个直接后果：同一企业同日同主体类型重复触发不会产生重复行；跨日重发（data_date 变化）会产生新行。

## 需求背景

本口径与 [[batch_no]] 的边界是历史上最容易误判的地方——batch_no 是新建行时的唯一流水号（INC_ 前缀），但已从幂等键中移除；总/分公司两行各自独立，靠 head_company_data 区分。落地规则见 [[incremental_idempotent_row]]。

## 版本演进

- v0：首次固化幂等键构成，并记录 batch_no 退出幂等键这一变更。

```ground:caliber
name: 增量落库幂等键
predicate: "ca_certification_info.submit_status = 'PENDING'"
scope: "幂等命中条件为 (cust_id, data_date, head_company_data, submit_status=PENDING)；batch_no 不参与；因此跨日重发会产生新行"
evidence: "code_path:CaCertificationInfoAppServiceImpl.java#createOrGetByKey"
```

关联页面：[[ca_certification_info]]、[[batch_no]]、[[incremental_idempotent_row]]、[[head_company_row]]、[[head_company_data]]。