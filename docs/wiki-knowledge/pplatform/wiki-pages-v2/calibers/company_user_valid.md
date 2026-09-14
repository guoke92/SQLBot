---
type: caliber
title: 企业联系人有效
page_key: company_user_valid
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - 有效联系人
  - listCompanyUser 过滤
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/PlatFormUserApplication.java
contract_version: "0.1"
belong: calibers
---

# 企业联系人有效

## 业务定位

定义 [[tables/cust_person_info|联系人表]] 中「有效联系人」的判定：逻辑未删除（`enable = 'Y'`）且账号状态处于 `ADD/EFFECT`。该口径用于 `listCompanyUser` 查询企业联系人。

## 需求背景

扫脸与实名需要拉取真实可用的经办人/联系人，历史逻辑删除行与未进入生效态的行不能参与业务。

## 版本演进

从代码可见，`status` 的取值域在查询侧收敛为 `ADD/EFFECT` 两项；与产品维度的 [[calibers/product_rel_not_frozen|产品关系未冻结]] 联合使用。

```ground:caliber
name: 企业联系人有效
predicate: "cust_person_info.enable = 'Y' AND cust_person_info.status IN ('ADD','EFFECT')"
scope: listCompanyUser 查询企业联系人
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/PlatFormUserApplication.java:listCompanyUser
```

关联页面：[[tables/sys_cust_user_rel|产品-用户关系表]]。