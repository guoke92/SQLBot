---
type: caliber
title: 管理员用户
page_key: admin_user
domain: 平台内部服务对接
status: draft
aliases:
  - 企业管理员口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
belong: calibers
---

「管理员用户」以 [[cust_person_info]] 的 `user_type = 'accountAdmin'` 识别企业管理员。用户类型取值见 [[user_type_role]]；与之并列的经办人判定见 [[operator_user]]。该口径通常与联系人有效性口径 [[valid_person]] 组合使用，避免把已停用的管理员纳入判定。

## 需求背景
企业管理员在平台上承担确认、提交审核等动作，服务侧需要稳定识别该角色；角色信息落在人员表上而非独立角色表，角色表 [[cust_role_info]] 表达的是另一维度的企业角色，两者不可互相替代。

## 版本演进
- v0.1（本页）：口径谓词来自代码语义分析。

```ground:caliber
name: 管理员用户
predicate: "cust_person_info.user_type = 'accountAdmin'"
scope: 识别企业管理员
evidence: "code_path:CustFacade.java:getCustPerson"
```