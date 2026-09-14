---
type: caliber
title: CA 幂等行
page_key: ca_idempotent_row
domain: 微信生态/小程序/扫脸
status: draft
aliases: [CA幂等键, 幂等行]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
belong: calibers
---

# CA 幂等行

[[ca_certification_info]] 的建单幂等口径：以 (cust_id, data_date, head_company_data, submit_status=PENDING) 命中则返回既有 id，不新建；batch_no 不进幂等键。

## 需求背景

刷脸链路可能因小程序重试多次触发落库，需以幂等键避免重复建单。

## 版本演进

v0.1 记录幂等谓词与 batch_no 的排除说明。

```ground:caliber
name: CA 幂等行
predicate: "ca_certification_info.cust_id = ? AND data_date = ? AND head_company_data = ? AND submit_status = 'PENDING'"
scope: "createOrGetByKey 命中则直接返回既有 id，不新建；batch_no 不进幂等键。"
evidence: code_path:CaCertificationInfoAppServiceImpl.java#createOrGetByKey
```

相关：[[ca_certification_info]]、[[ca_submit_state_machine]]、[[latest_success_submit]]。