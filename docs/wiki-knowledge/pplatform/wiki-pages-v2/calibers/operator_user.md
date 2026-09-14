---
type: caliber
title: 经办人用户
page_key: operator_user
domain: 平台内部服务对接
status: draft
aliases:
  - 经办人口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
belong: calibers
---

「经办人用户」以 [[cust_person_info]] 的 `user_type = 'accountNormal'` 识别企业经办人，与管理口径 [[admin_user]] 对称，取值域见 [[user_type_role]]。经办人在关系表上的冻结状态见 [[sys_cust_user_rel]] 与状态机 [[operator_freeze_flow]]。

## 需求背景
经办人是被运营侧冻结/解冻的直接对象，因此人员角色与关系冻结两个维度需要分别判定：前者决定「他是不是经办人」，后者决定「这条关系当前是否可用」。

## 版本演进
- v0.1（本页）：本口径在语义分析中被截断，当前仅确认名称与谓词，适用范围与代码出处待补（见页面末尾 REVIEW 记录）。

```ground:caliber
name: 经办人用户
predicate: "cust_person_info.user_type = 'accountNormal'"
```