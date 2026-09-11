---
type: concept
title: 管理员
page_key: concept.admin
domain: 客户联系人管理
status: draft
aliases:
  - accountAdmin
  - admin
  - 企业管理员
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code:CustPersonApplication.getAdminByCustCodeCompanyType"
maps_to: "cust_person_info.user_type = 'accountAdmin'"
adjudication: boundary
also_confused_with:
  - 运营人员
  - 平台管理员
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---

管理员指企业管理员，是 [[tables/cust_person_info]] 中 `user_type = 'accountAdmin'` 的记录，代表企业侧拥有最高权限的人。取数口径见 [[calibers/person-admin]]，其唯一性与变更约束见 [[rules/admin-uniqueness]]、[[rules/admin-change-freeze]]。

## 需求背景

企业侧的权限体系以管理员为顶点：平台先为企业指派运营人员，再由管理员邀请经办人加入并使用业务功能。因此「管理员」在企业语境下即企业管理员，口语中常被简称为「管理员」。

## 边界

管理员与**运营人员**不是同一实体：管理员是企业内部人员，落在 `user_type` 上；运营人员是平台分配给企业的对接人，落在 `operator` / `operator_id` / `operator_realname` 字段上，两者通过 `operator_id` 关联而非身份同一。与「平台管理员」同样需要区分，后者不属于本表语义。

## 版本演进

- v0：首次登记，`maps_to`、adjudication 与易混项来自术语桥语义分析。

相关：[[calibers/person-admin]]、[[rules/admin-uniqueness]]、[[rules/operator-assignment-prerequisite]]、[[concepts/handler]]。

相关：[[cust_person_info]]
