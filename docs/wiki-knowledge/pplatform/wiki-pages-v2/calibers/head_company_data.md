---
type: caliber
title: 总公司数据
page_key: head_company_data
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - headCompanyData=Y
  - 总公司行
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
belong: calibers
---

# 总公司数据

## 业务定位

`ca_certification_info.head_company_data = 'Y'` 标识分公司双行场景中的总公司行，是幂等键的组成部分。

## 需求背景

总公司与分公司在同一 `custId` 下需要各自独立上报（`batch_no` 各自独立），必须以 `head_company_data` 区分，否则会互相覆盖或误判幂等。

## 版本演进

从代码可见，`normalizeHeadCompanyData` 统一规范化该字段取值；与之相对的是 [[calibers/branch_company_data|分公司数据]]，语义辨析见 [[concepts/head_company_data|总公司数据（术语）]]。

```ground:caliber
name: 总公司数据
predicate: "ca_certification_info.head_company_data = 'Y'"
scope: 分公司双行场景总公司行
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:normalizeHeadCompanyData
```

关联页面：[[tables/ca_certification_info|CFCA 认证与上送表]]、[[rules/head_company_two_row_idempotency|总分公司双行幂等规则]]。