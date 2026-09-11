---
type: caliber
title: 有效联系人
page_key: caliber.valid_person
domain: 客户联系人管理
status: draft
aliases:
  - 启用联系人
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code:CustPersonApplication.listCompanyPerson"
contract_version: "0.1"
---

有效联系人是最基础的列表口径：只要 [[tables/cust_person_info]] 的 `enable = 'Y'` 即计入。注意它与 [[processes/person-account-status]] 的 `status` 无关，冻结（`FREEZE`）的联系人仍属有效联系人，只是不可再作为当前管理员使用。

## 需求背景

企业联系人列表、选择器等处均以「未逻辑删除」为默认过滤条件，删除联系人时系统只置 `enable = 'N'`，保留历史关系与操作记录。

```ground:caliber
caliber: 有效联系人
predicate: "cust_person_info.enable = 'Y'"
scope: 查询所有启用状态的联系人
evidence: "code:CustPersonApplication.listCompanyPerson"
```

## 版本演进

- v0：首次登记，口径与代码过滤条件一致。

相关：[[tables/cust_person_info]]、[[concepts/contact-person]]、[[processes/person-account-status]]。