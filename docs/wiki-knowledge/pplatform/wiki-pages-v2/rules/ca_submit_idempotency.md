---
type: rule
title: CA 上送幂等规则
page_key: ca_submit_idempotency
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - createOrGetByKey 幂等
  - 幂等跳过重复上送
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
belong: rules
---

# CA 上送幂等规则

## 业务定位

约束 [[tables/ca_certification_info|CFCA 认证与上送表]] 的建行与上送行为：建行时命中 [[calibers/ca_submit_pending|CA 待上送]] 行直接复用；上送前命中 [[calibers/ca_submit_success|CA 上送成功]] 行则跳过重复上送。

## 需求背景

签章中台上送不可重复受理；业务侧可能多次触发认证与上送准备，必须以库内状态作为幂等依据，而不是依赖调用方去重。

## 版本演进

从代码可见，`createOrGetByKey` 负责建行幂等，`findLatestSuccessRow` 负责上送前幂等判定；状态流转见 [[processes/ca_submit_status|CFCA 上送状态]]。

```ground:rule
name: CA 上送幂等
predicate: "createOrGetByKey 命中 ca_certification_info.submit_status = 'PENDING' 行则复用；findLatestSuccessRow 命中 ca_certification_info.submit_status = 'SUCCESS' 行则跳过重复上送"
scope: CFCA 上送签章中台的建行与上送前置判定
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:createOrGetByKey, lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:findLatestSuccessRow
```

关联页面：[[concepts/submit_success|上送成功（术语）]]、[[calibers/ca_submit_pending|CA 待上送]]。