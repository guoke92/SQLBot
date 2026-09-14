---
type: process
title: 授权确认书认证状态流转
page_key: authed_status_state_flow
domain: 授权协议与电子授权
status: draft
aliases:
  - 授权书状态流转
  - authed_status 状态机
oid: 1
scope:
  databases: [unknown]
sources:
  - db:authorization_agreement
  - code:CustAuthAgreementDomainService.java
contract_version: "0.1"
belong: processes
---

该状态机描述 [[authorization_agreement]] 中 `authed_status` 的取值与迁移路径。它决定“这家企业/这个管理员是否已签署授权书”，是 [[auth_agreement_authed_y]] / [[auth_agreement_authed_n]] 两个口径的底层依据。

关键点在于：**N → Y 只在当前操作人是企业管理员（admin）时成立**；非管理员用户被指定授权时，记录保持 N。**Y → N 出现在管理员变更**：换人时原管理员在该企业下的全部授权记录被置为 `enable=N` 且 `authed_status=N`，再由新管理员重新走授权，见 [[manager_change_invalidate_agreement]] 与 [[auth_agreement]]。

## 需求背景
企业管理员授权认证通过（新增企业认证、补授权、完善资料）后授权才生效；管理员换人后原授权必须立即失效，避免“旧人授权、新人操作”。因此状态机需要一条双向通路，且 Y→N 只能由管理员变更触发。

## 版本演进
DB 中 N（19547）显著多于 Y（11617），与“管理员变更即作废、需重新授权”的写入行为一致；`creation_type` 中的 `CUST_BUILD_INIT`（建档初始化自动授权）说明早期授权是在建档时自动产生的。

```ground:process
name: 授权确认书认证状态
field: authorization_agreement.authed_status
states:
  - value: "N"
    label: 未授权/已禁用
    source: db_dist
  - value: "Y"
    label: 已授权
    source: db_dist
transitions:
  - from: "N"
    event: 企业管理员授权认证通过（新增企业认证/补授权/完善资料）
    to: "Y"
    evidence: "code_path:CustAuthAgreementDomainService.java:passAuthorizationAgreementDirectly"
  - from: "N"
    event: 存在未签署记录且当前用户为企业管理员（admin）
    to: "Y"
    evidence: "code_path:CustAuthAgreementDomainService.java:passAuthorizationAgreementDirectly"
  - from: "N"
    event: 非管理员用户被指定授权
    to: "N"
    evidence: "code_path:CustAuthAgreementDomainService.java:passAuthorizationAgreementDirectly"
  - from: "Y"
    event: 企业管理员变更（换人）
    to: "N"
    evidence: "code_path:CustAuthAgreementDomainService.java:disabledAllAuthorizationAgreement"
```