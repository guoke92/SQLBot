---
type: rule
title: 总分公司双行幂等规则
page_key: head_company_two_row_idempotency
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - headCompanyData 幂等键
  - 分公司双行
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
belong: rules
---

# 总分公司双行幂等规则

## 业务定位

约束 [[tables/ca_certification_info|CFCA 认证与上送表]] 在分公司场景下的行唯一性：总公司行与分公司行共用 `cust_id`，但以 `head_company_data`（`Y`/`N`）区分，形成两行独立数据；`batch_no` 亦各自独立生成。

## 需求背景

若不以 `head_company_data` 参与幂等键，总公司与分公司数据会互相命中，导致一侧数据被覆盖或上送错主体。

## 版本演进

从代码可见，`normalizeHeadCompanyData` 统一规范化取值，配套口径见 [[calibers/head_company_data|总公司数据]] 与 [[calibers/branch_company_data|分公司数据]]，术语边界见 [[concepts/head_company_data|总公司数据（术语）]]。

```ground:rule
name: 总分公司双行幂等
predicate: "ca_certification_info.cust_id 相同且 ca_certification_info.head_company_data = 'Y' / 'N' 区分总公司行与分公司行；ca_certification_info.data_date 与 ca_certification_info.batch_no 参与唯一性判定"
scope: 分公司双行场景建行与取数幂等
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java:normalizeHeadCompanyData
```

关联页面：[[rules/ca_submit_idempotency|CA 上送幂等规则]]。