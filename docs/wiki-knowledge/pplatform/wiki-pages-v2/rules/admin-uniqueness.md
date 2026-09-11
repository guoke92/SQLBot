---
type: rule
title: 管理员唯一性
page_key: rule.admin_uniqueness
domain: 客户联系人管理
status: draft
aliases:
  - 单一管理员约束
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code:CustPersonApplication.checkBeforeSave"
  - "code:CustPersonApplication.updateAuthorAndApply"
contract_version: "0.1"
---

> 本页含未证实文档主张（document_claim，未证实），见文末《版本演进》。

管理员唯一性约束要求：同一企业同一公司类型下只能存在一个启用状态的管理员。校验命中时新增或变更操作被拒绝，避免一个企业出现两个并行管理员。

## 需求背景

需求文档明确要求「同一企业同一角色下只有一个管理员」（code_path:CustPersonApplication.java:checkBeforeSave + reqdoc:同一企业同一角色下只有一个管理员），代码在保存前校验与授权人变更两处实现。企业在同一角色类型（如核心企业、供应商）下应当只有一个对外代表的联系人，因此约束同时覆盖企业维度与公司类型维度。

```ground:rule
rule: 管理员唯一性
content: 同一企业同一公司类型下只能存在一个启用状态的管理员
impact: 新增或变更管理员时校验，防止重复
field_targets:
  - cust_person_info.user_type
  - cust_person_info.ref_cust_company_info
  - cust_person_info.company_type
  - cust_person_info.enable
evidence: "code:CustPersonApplication.checkBeforeSave + code:CustPersonApplication.updateAuthorAndApply + code_path:CustPersonApplication.java:checkBeforeSave + reqdoc:同一企业同一角色下只有一个管理员"
```

## 版本演进

- v0：首次登记。
- （document_claim，未证实）文档主张「管理员角色不能自我删除」在代码中未找到对应实现，暂不纳入约束，见 REVIEW 块。

相关：[[calibers/person-admin]]、[[concepts/admin]]、[[rules/admin-change-freeze]]、[[tables/cust_person_info]]。