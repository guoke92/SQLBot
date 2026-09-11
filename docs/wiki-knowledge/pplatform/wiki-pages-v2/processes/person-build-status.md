---
type: process
title: 联系人建档状态
page_key: process.person_build_status
domain: 客户联系人管理
status: draft
aliases:
  - 建档状态流转
  - cust_build_status 状态机
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code_path:CustCompanyInfoApplication.java:getCustBuildStatus"
  - "code_path:CustCompanyInfoApplication.java:messageNotify"
contract_version: "0.1"
---

建档状态描述联系人（随企业建档）从初始化到审核通过或失败的流转，落在 [[tables/cust_person_info]] 的 `cust_build_status` 字段。不同录入来源决定首次进入的是「待客户确认」还是「建档中」。

## 需求背景

邀请认证-客户录入/自主注册的场景由客户先确认资料，再进入运营中台审核；邀请认证-平台录入的场景由平台直接送审。审核环节支持退回修改、拒绝与通过，失败后允许修改后重新提交，因此状态机在 `CUST_BUILDING` 与 `CUST_CONFIRM_AWAIT` 之间存在回退边。非 AMS 来源新增经办人时默认直接置为建档成功，见 [[rules/new-person-default-build-success]]。

```ground:process
process: 联系人建档状态
field: cust_person_info.cust_build_status
states:
  - value: INIT
    label: 初始化
    source: db_dist
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: db_dist
  - value: CUST_BUILDING
    label: 建档中
    source: db_dist
  - value: BUILD_SUCCESS
    label: 建档成功
    source: db_dist
  - value: BUILD_FAIL
    label: 建档失败
    source: db_dist
  - value: CUST_CHANGE
    label: 变更中
    source: code_enum
  - value: AWAIT_CUST_CONFIRM
    label: 待客户确认（代码枚举）
    source: code_enum
transitions:
  - from: INIT
    event: 提交建档（邀请认证-客户录入/自主注册）
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:getCustBuildStatus"
  - from: INIT
    event: 提交建档（邀请认证-平台录入）
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:getCustBuildStatus"
  - from: CUST_CONFIRM_AWAIT
    event: 客户提交，运营中台审核
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 运营中台审核退回
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 审核通过
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 审核拒绝
    to: BUILD_FAIL
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: BUILD_FAIL
    event: 修改后重新提交
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
```

## 版本演进

- v0：首次登记。`CUST_CHANGE`、`AWAIT_CUST_CONFIRM` 仅有代码枚举证据，DB 值分布中未出现，属低频/待观察状态。

相关：[[tables/cust_person_info]]、[[rules/new-person-default-build-success]]、[[processes/person-realname-status]]。