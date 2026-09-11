---
type: concept
title: 经办人
page_key: concept.handler
domain: 客户联系人管理
status: draft
aliases:
  - accountNormal
  - operator
  - 业务用户
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code:CustPersonApplication.insertOrUpdatePerson"
maps_to: "cust_person_info.user_type = 'accountNormal'"
adjudication: boundary
also_confused_with:
  - 运营人员
  - 联系人
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---

经办人指企业内使用业务功能的用户，是 [[tables/cust_person_info]] 中 `user_type = 'accountNormal'` 的记录。取数口径见 [[calibers/person-operator]]，其认证与建档行为见 [[processes/person-realname-status]]、[[rules/new-person-default-build-success]]。

## 需求背景

经办人是业务办理的主体，需要实名认证后才能作业；企业通过邀请的方式把经办人纳入平台，邀请相关前置条件见 [[rules/operator-assignment-prerequisite]]。

## 边界

经办人与**运营人员**不是同一实体：经办人是企业侧用户（`user_type = 'accountNormal'`），运营人员是平台侧人员（`operator` 字段），二者通过 `operator_id` 关联。经办人也不是「联系人」的同义词，联系人是对全表的统称，见 [[concepts/contact-person]]。

## 版本演进

- v0：首次登记；别名 `operator` 沿用术语桥给出的并列叫法，需注意与平台侧 `operator` 字段字面冲突。

相关：[[calibers/person-operator]]、[[concepts/contact-person]]、[[concepts/admin]]、[[rules/phone-uniqueness]]。

相关：[[cust_person_info]]
