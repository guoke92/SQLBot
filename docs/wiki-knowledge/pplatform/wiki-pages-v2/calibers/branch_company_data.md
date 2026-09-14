---
type: caliber
title: 分公司数据
page_key: branch_company_data
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - headCompanyData=N
  - 分公司行
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
belong: calibers
---

# 分公司数据

## 业务定位

`ca_certification_info.head_company_data = 'N'` 标识分公司双行场景中的分公司行。

## 需求背景

分公司行与总公司行共用 `custId` 但上报流水号独立、核验内容可能不同，需在读取「最新成功行」时按该口径正确区分，避免取到另一侧数据。

## 版本演进

从代码可见，该取值与 [[calibers/head_company_data|总公司数据]] 成对出现，由 `normalizeHeadCompanyData` 规范化，见 [[processes/ca_submit_status|CFCA 上送状态]]。

```ground:caliber
name: 分公司数据
predicate: "ca_certification_info.head_company_data = 'N'"
scope: 分公司双行场景分公司行
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:normalizeHeadCompanyData
```

关联页面：[[tables/ca_certification_info|CFCA 认证与上送表]]。