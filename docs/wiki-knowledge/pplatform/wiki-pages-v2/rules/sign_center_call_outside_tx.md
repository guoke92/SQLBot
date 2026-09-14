---
type: rule
title: 中台调用置于事务外
page_key: sign_center_call_outside_tx
domain: CA证书认证
status: draft
aliases: [NOT_SUPPORTED, 事务外调用中台]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaActivationApplication.java
  - code:CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
belong: rules
---

activateByOpCompanyId 标 @Transactional(NOT_SUPPORTED)，confirm 不加事务，submitToSignCenter/openCa 均跨网络调用。

**影响**：避免长 IO 占用数据库事务。相应地，落库与中台调用不是原子的：可能出现"行已建但未上送"（[[ca_submit_status|PENDING]]）或"中台已成功但本地未回写"的窗口，排障时应以 sign_platform_result 与中台查询为准来对账。

## 需求背景

该规则解释了 [[operation_platform_source]] 来源中 PENDING 行偏多的可能原因，也是 [[incremental_idempotent_row]] 复用 PENDING 行的设计动因。

## 版本演进

- v0：首次固化事务边界。

```ground:rule
name: 中台调用置于事务外
content: activateByOpCompanyId 标 @Transactional(NOT_SUPPORTED)，confirm 不加事务，submitToSignCenter/openCa 均跨网络调用
impact: 避免长 IO 占用数据库事务
field_targets:
  - ca_certification_info.submit_status
evidence: "code_path:CaActivationApplication.java#activateByOpCompanyId"
```

关联页面：[[ca_submit_status]]、[[incremental_idempotent_row]]、[[operation_platform_source]]。