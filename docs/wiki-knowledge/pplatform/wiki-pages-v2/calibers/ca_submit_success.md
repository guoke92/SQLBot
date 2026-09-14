---
type: caliber
title: CA 上送成功
page_key: ca_submit_success
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - submit_status=SUCCESS
  - 上送成功行
  - findLatestSuccessRow
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
belong: calibers
---

# CA 上送成功

## 业务定位

`ca_certification_info.submit_status = 'SUCCESS'` 表示该行已成功上送签章中台。用于取企业最新成功上报数据，以及幂等跳过重复上送。

## 需求背景

同一企业在同一幂等键下已成功上送后不应重复上报，避免签章中台重复受理；同时「最新成功行」也是查询企业当前有效认证数据的口径。

## 版本演进

从代码可见，`findLatestSuccessRow` 承接该口径；成功态可被再次 `submitToSignCenter` 覆盖为 `SUCCESS`，见 [[processes/ca_submit_status|CFCA 上送状态]] 与 [[rules/ca_submit_idempotency|CA 上送幂等规则]]。

```ground:caliber
name: CA 上送成功
predicate: "ca_certification_info.submit_status = 'SUCCESS'"
scope: 取企业最新成功上报数据、幂等跳过重复上送
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:findLatestSuccessRow
```

关联页面：[[tables/ca_certification_info|CFCA 认证与上送表]]、[[concepts/submit_success|上送成功（术语）]]。