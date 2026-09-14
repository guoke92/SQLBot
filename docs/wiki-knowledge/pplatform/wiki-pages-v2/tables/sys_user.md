---
type: table
title: sys_user 系统用户表
page_key: sys_user
domain: 平台内部服务对接
status: draft
aliases:
  - 系统用户表
  - 用户账号表
oid: 1
scope:
  databases:
    - lowcode_pplatform
sources:
  - code
contract_version: "0.1"
belong: tables
---

sys_user 保存平台内部的系统用户账号，主键 `id` 被 [[cust_person_info]] 的 `user_id` 引用，用于把企业联系人挂到具体的登录账号上；`user_name` 与 `name` 区分账号标识与姓名，`mobile`、`email`、`certificate_type`、`certificate_no` 提供联系方式与证件信息。

在内部服务对接中，本表是「账号—企业」关系的账号侧端点：企业侧关系由 [[cust_person_info]] 与 [[sys_cust_user_rel]] 表达，账号本身的信息只在用户服务内维护。

## 需求背景
企业建档过程中会为联系人分配系统账号，运营侧又会按账号冻结/解冻经办关系（见 [[operator_freeze_flow]]），因此账号标识与联系方式需要稳定可读；证件类字段用于实名与认证类服务的核对。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，字段物理类型与字典绑定尚未在证据中出现，暂留空。

