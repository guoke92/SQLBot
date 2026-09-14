---
type: rule
title: 多级产品回调置中
page_key: multi_level_callback_pending
domain: 平台产品配置
status: draft
aliases: [activeAndNotify, ACFLOW/ORDER 置 P]
oid: 1
scope:
  databases: [platform]
sources:
  - code:TenantProductApplication.java#activeAndNotify
  - code:ProductOpenStatusEnum.java
contract_version: "0.1"
belong: rules
---

租户产品开通时按产品分流：ACFLOW / ORDER 产品把 [[tenant_product]] 的 `open_status` 置为 P，等待多级回调；其他产品直接由 `domainService.active` 生效置 Y，并推送 EFFECTED 事件。

## 需求背景

该规则决定 [[tenant_product_open_status]] 的流转分支，并直接决定 [[tenant_product_on_shelf]] 口径何时成立。P 状态的产品不满足客户产品开通前置条件。

## 版本演进

- 需求文档所述 PENDING/ACTIVE/CANCEL 与实现的 P/Y 不符，本规则以代码为准（见 [[product_open_status]]）。

```ground:rule
name: 多级产品回调置中
content: "ACFLOW/ORDER 产品开通时把 tenant_product.open_status 置 P 等待多级回调，其他产品直接生效并推送 EFFECTED 事件"
impact: 租户产品开通状态流转
field_targets:
  - tenant_product.open_status
evidence: "code_path:TenantProductApplication.java#activeAndNotify"
```

关联：[[tenant_product]]、[[tenant_product_open_status]]、[[tenant_product_on_shelf]]、[[product_open_status]]