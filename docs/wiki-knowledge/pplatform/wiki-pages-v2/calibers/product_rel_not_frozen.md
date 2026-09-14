---
type: caliber
title: 产品关系未冻结
page_key: product_rel_not_frozen
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - is_freeze=N
  - 未冻结产品关系
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/PlatFormUserApplication.java
contract_version: "0.1"
belong: calibers
---

# 产品关系未冻结

## 业务定位

[[tables/sys_cust_user_rel|产品-用户关系表]] 中 `is_freeze = 'N'` 表示关系未冻结，是企业联系人按产品过滤有效用户的必要条件。

## 需求背景

企业联系人的可用性同时受账号状态与产品关系状态约束，冻结关系下的用户不应出现在可选经办人列表中。

## 版本演进

从代码可见，该条件固定出现在 `listCompanyUser` 的过滤逻辑中，与 [[calibers/company_user_valid|企业联系人有效]] 并列。

```ground:caliber
name: 产品关系未冻结
predicate: "sys_cust_user_rel.is_freeze = 'N'"
scope: 企业联系人按产品过滤有效用户
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/PlatFormUserApplication.java:listCompanyUser
```

关联页面：[[tables/cust_person_info|联系人表]]。