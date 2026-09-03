---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:product-config@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 租户产品开通状态
page_key: open_status
domain: 产品与配置
aliases:
- 已开通产品
- 开通中
- 未开通
- 租户产品状态
- 产品开通状态
- 开通产品
anchors:
- open_status
---
# 租户产品开通状态

tenant_product.open_status 三态（租户侧，与企业侧 cust_auth_application 的 NOT_OPENED/OPENING/OPENED 是不同体系）：Y 已开通 / P 开通中（仅 ACFLOW/ORDER 产品 activate 后出现，等外部多级回调置 Y）/ N 未开通（含取消）。取消前置 checkOnTheWay：存在生效项目（tenant_project.project_status='1' AND product_id=本产品）或企业开通（cust_auth_application.ref=tenant_product.code）则拒绝。

```ground:enum
enum: open_status
fields:
- tenant_product.open_status
values:
  Y:
    label: 已开通
  P:
    label: 开通中
  N:
    label: 未开通
```

## 关联
- [[tenant_product|tenant_product]]
