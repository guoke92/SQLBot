---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-build-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 建档认证状态
page_key: cust_build_status
domain: 客户与建档
aliases:
- 认证状态
- 认证成功
- 建档成功
- 认证失败
- 待客户认证
- 审核中
- 退回
- 变更中
anchors:
- cust_build_status
---
# 建档认证状态

企业在本地系统的认证全生命周期状态（14 态）：INIT 初始化 →（邀请流经运营中台回调 / 简易流客户确认）→ BUILD_SUCCESS 认证成功 或 BUILD_FAIL 认证失败；含审核流 （CUST_BUILDING/CUST_BUILD_SUCCESS）、变更流（CUST_CHANGE）、待客户确认 （AWAIT_CUST_CONFIRM 简易流 / CUST_CONFIRM_AWAIT 邀请流，两值显示名近似但分属两流）。

```ground:enum
enum: cust_build_status
fields:
- cust_company_info.cust_build_status
values:
  INIT:
    label: 初始化
  TO_BE_BUILD:
    label: 未建档
  BUILDING:
    label: 建档中
  BUILD_SUCCESS:
    label: 认证成功
  BUILD_FAIL:
    label: 认证失败
  BUILD_BACK:
    label: 退回
  BUILD_ACTIVATE:
    label: 待激活
  CUST_CONFIRM_AWAIT:
    label: 待客户认证（邀请流）
  CUST_AUDIT_AWAIT:
    label: 待审核
  CUST_BUILDING:
    label: 审核中
  CUST_BUILD_SUCCESS:
    label: 审核通过
  CUST_BUILD_FAIL:
    label: 审核拒绝
  CUST_CHANGE:
    label: 变更
  AWAIT_CUST_CONFIRM:
    label: 待客户确认（简易流）
```

## 关联
- [[cust_company_info|cust_company_info]]
