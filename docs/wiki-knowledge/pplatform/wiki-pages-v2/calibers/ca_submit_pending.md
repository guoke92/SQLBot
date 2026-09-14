---
type: caliber
title: CA 待上送
page_key: ca_submit_pending
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - submit_status=PENDING
  - 待上送行
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
belong: calibers
---

# CA 待上送

## 业务定位

`ca_certification_info.submit_status = 'PENDING'` 表示该行尚未上送签章中台，是 `createOrGetByKey` 幂等命中的条件：已存在待上送行时直接复用，不再新建。

## 需求背景

同一幂等键（含 `cust_id`、`data_date`、`head_company_data` 等）下反复触发上送准备时，必须复用未上送行，避免产生重复待上送数据。

## 版本演进

从代码可见，新建行的初始状态固定为 `PENDING`，该状态是 [[processes/ca_submit_status|CFCA 上送状态]] 的起点；与 [[calibers/ca_submit_success|CA 上送成功]] 共同支撑幂等。

```ground:caliber
name: CA 待上送
predicate: "ca_certification_info.submit_status = 'PENDING'"
scope: createOrGetByKey 幂等命中
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:createOrGetByKey
```

关联页面：[[tables/ca_certification_info|CFCA 认证与上送表]]、[[rules/ca_submit_idempotency|CA 上送幂等规则]]。