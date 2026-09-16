---
type: caliber
title: 有效企业
page_key: effective_company
domain: 企业建档与认证状态机
status: draft
aliases: [生效企业]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:cust_company_info"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: calibers
field_targets:
  - cust_company_info.cust_status
  - cust_company_info.enable
  - cust_company_info.data_type
---

建档场景下可用企业，列在 [[cust_company_info]]：主数据行 `data_type='1'`、`cust_status='EFFECT'`（生效）且 `enable='Y'`。建档成功是过程态 [[cust_build_status]]=`BUILD_SUCCESS`，不要与本口径互换——建档成功通常会推动 [[cust_status_flow]] 进入 EFFECT，但冻结/注销后建档状态仍可能是成功。流程数据（`data_type='0'`）和编辑过程（`data_type='2'`）不是本口径。

```ground:caliber
name: 有效企业
predicate: "cust_company_info.data_type = '1' AND cust_company_info.cust_status = 'EFFECT' AND cust_company_info.enable = 'Y'"
scope: cust_company_info
evidence: db
```
