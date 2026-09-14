---
type: concept
title: 联系人
page_key: contact_person
domain: 经办人/联系人/管理员管理
status: draft
aliases: [经办人, 客户联系人, cust_person_info, accountNormal]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.user_type", "code:CustPersonController.java#getOperInfo"]
contract_version: "0.1"
maps_to: cust_person_info.user_type
field_targets:
  - cust_person_info.user_type
adjudication: boundary
also_confused_with:
  - "cust_person_info.user_type = 'accountAdmin'"
  - "cust_person_info.user_type = 'accountGuest'"
boundary: "cust_person_info 是表级统称（客户联系人表），“经办人”仅指 user_type=accountNormal 的行，管理员为 accountAdmin、游客为 accountGuest；接口入参常直接叫 CustPersonInfoDO，不代表就是经办人。"
belong: concepts
field_targets: [cust_person_info.user_type]
---

"联系人"是对 [[cust_person_info]] 表级数据的统称，实际业务语义由 user_type 决定：accountAdmin=企业管理员、accountNormal=经办人、accountGuest=游客。日常口语里"联系人"和"经办人"经常混用，但在口径层面必须区分（[[normal_person]]、[[company_admin]]）。

## 需求背景
- 经办人列表、管理员定位、游客排除三个口径分别对应 user_type 的三个取值，混用会直接导致列表与校验结果错误（[[exclude_guest]]、[[valid_person]]）。

## 版本演进
- 当前版本的接口入参仍以 CustPersonInfoDO 命名，命名未体现 user_type，是概念混淆的主要来源。

相关页面：[[cust_person_info]]、[[normal_person]]、[[company_admin]]、[[exclude_guest]]。