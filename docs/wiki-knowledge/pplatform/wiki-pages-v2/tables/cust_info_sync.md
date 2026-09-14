---
type: table
title: cust_info_sync 客户信息同步记录表
page_key: cust_info_sync
domain: 平台事件监听与同步
status: draft
aliases:
  - 客户信息同步
  - 同步请求记录
oid: 1
scope:
  databases: [lowcode_pplatform]
sources:
  - db:cust_info_sync
  - code:CustCompanyInfoApplication.java:syncClientForSimple
contract_version: "0.1"
belong: tables
---

记录平台向运营中台发起的客户信息同步请求，`processType` 区分「建档/审核流程」与「变更流程」，是 [[cust_build_status]] 状态迁移的外部触发点。

## 需求背景

需求文档主张「企业准入审核通过则更新企业状态为已通过，驳回则更新为已驳回」，其上游即本表所记录的同步请求：`CUST_CHECK_INIT` 由 `operCustFacade.doSyncClient` 发起，变更侧由 `CustSyncService.requestSync(ProcessTy.CHANGE, ...)` 发起。

## 版本演进

- `processType` 落库使用 `ProcessTy.getCode()` 而非 `name()`，同族枚举在本主题内存在三种落库风格（name() / getCode() / getDictKey()），是排查数据时的常见陷阱。

