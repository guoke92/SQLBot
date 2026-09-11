---
type: caliber
title: "企业管理员唯一校验"
page_key: "calibers/company_admin_unique_check"
domain: "customer-onboarding"
status: draft
aliases:
  - "管理员唯一性口径"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustPersonApplication.java:checkBeforeSave,updateAuthorAndApply"
contract_version: "0.1"
---

同一企业、同一客户角色下，只允许一个启用状态的管理员联系人。校验在保存与更新授权/申请两处复用，命中即为冲突。字段载体见 [[tables/cust_person_info]]，退回场景的豁免见 [[rules/admin_unique_check_reject_exemption]]。

## 需求背景

需求文档要求企业管理员唯一，作为变更提交与授权判定的前置条件。

## 版本演进

- 校验入口由单点保存扩展到授权/申请链路，两处必须保持同一 predicate，否则会出现「保存拦得住、申请拦不住」的漏洞。

```ground:caliber
name: "企业管理员唯一校验"
predicate: "cust_person_info.user_type = 'admin' AND cust_person_info.enable = 'Y' AND ref_cust_company_info = X AND company_type = Y AND id != 当前id"
scope: "checkBeforeSave/updateAuthorAndApply：count 必须为 0"
evidence: "code_path:CustPersonApplication.java:checkBeforeSave,updateAuthorAndApply"
```

相关：[[tables/cust_person_info]]、[[rules/admin_unique_check_reject_exemption]]。