---
type: table
title: sys_cust_org_user_permission（用户数据权限表）
page_key: sys_cust_org_user_permission
domain: cust_org_permission
status: draft
aliases: [用户数据权限表, 数据权限表, sys_cust_org_user_permission]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources:
  - code:DataPermissionApplication.java
contract_version: "0.1"
belong: tables
---

sys_cust_org_user_permission 是「数据权限」的落库表：它把某个用户在某企业某角色下可见的组织范围固化成一行记录。读侧由数据权限查询决定返回值，写侧由保存动作校验准入，两侧共用同一张表，因此它同时承载准入口径与默认兜底口径。

本表与 [[cust_person_info]]（判定是否为 [[admin]]）、[[cust_company_info]]（企业与企业角色）、[[permission_type]]、[[org_id_list]] 紧密相关；行为受 [[data_permission_save_admin_only]]、[[specified_requires_org_list]]、[[enterprise_admin_fixed_all]]、[[default_same_as_user_org_backfill]] 约束，值域见流程 [[data_permission_permission_type]]。

## 需求背景
本页仅依据代码证据（DataPermissionApplication）。本次语义分析未包含需求文档（reqdoc）主张，故无双源 evidence。

## 版本演进
本次语义分析未提供版本变更证据。

