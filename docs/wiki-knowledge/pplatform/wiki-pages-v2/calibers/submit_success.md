---
type: caliber
title: 上送完成口径
page_key: submit_success
domain: CA证书认证
status: draft
aliases: [SUCCESS 行, findLatestSuccessRow 口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
belong: calibers
---

"这单算上送完成"的判定：submit_status='SUCCESS'。AMS 复用数据时并不看最新一行，而是按 findLatestSuccessRow 取最新一条 SUCCESS 行重新组装上报，因此 FAIL/PENDING 行不会污染复用结果。

## 需求背景

本口径直接来自 [[ca_submit_status]] 状态机的终态，并与 [[submit_idempotent_short_circuit]] 互为因果：正因为 SUCCESS 是终态且会短路，取 SUCCESS 行复用才是安全的。

## 版本演进

- v0：首次固化判定与复用语义。

```ground:caliber
name: 上送完成口径
predicate: "ca_certification_info.submit_status = 'SUCCESS'"
scope: AMS 复用数据时取最新一条 SUCCESS 行重新组装上报（findLatestSuccessRow）
evidence: "code_path:CaCertificationInfoAppServiceImpl.java#findLatestSuccessRow"
```

关联页面：[[ca_submit_status]]、[[submit_idempotent_short_circuit]]、[[ca_certification_info]]。