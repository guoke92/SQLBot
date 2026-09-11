---
type: concept
title: 联系人
page_key: concept.contact_person
domain: 客户联系人管理
status: draft
aliases:
  - cust_person_info
  - 用户
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "db"
maps_to: "表 cust_person_info 的记录"
adjudication: synonym
also_confused_with:
  - 管理员
  - 经办人
  - 游客
contract_version: "0.1"
---

联系人是 [[tables/cust_person_info]] 表记录的统称，按 `user_type` 细分为管理员（[[concepts/admin]]）、经办人（[[concepts/handler]]）、游客（[[concepts/guest]]）三类。

## 需求背景

系统内部与需求文档中「联系人」「用户」交替使用，实际都指本表记录；为避免与登录账号（`user_name`、`user_id`）等概念混淆，wiki 统一以「联系人」作为表级统称。

## 边界

联系人是同义归一（synonym）：`cust_person_info` 记录即联系人。发生歧义时按 `user_type` 明确到具体角色，不要用「用户」泛指。

## 版本演进

- v0：首次登记，adjudication 为 synonym。

相关：[[concepts/admin]]、[[concepts/handler]]、[[concepts/guest]]、[[tables/cust_person_info]]、[[calibers/valid-person]]。