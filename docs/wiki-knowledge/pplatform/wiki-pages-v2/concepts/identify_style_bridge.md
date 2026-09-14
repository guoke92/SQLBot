---
type: concept
title: 认证方式术语桥（identify_style 与 IdentifyTypeConstant）
page_key: identify_style_bridge
domain: 平台内部服务对接
status: draft
aliases:
  - identify_style
  - 认证方式
  - IdentifyTypeConstant
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.identify_style]
  - semantic:state_machines[企业建档/认证状态]
contract_version: "0.1"
maps_to:
  - term: identify_style
    target: cust_company_info.identify_style
    evidence: code
  - term: IdentifyTypeConstant.INVITE
    target: cust_company_info.identify_style
    evidence: code
  - term: IdentifyTypeConstant.SELF
    target: cust_company_info.identify_style
    evidence: code
  - term: IdentifyTypeConstant.INVITE_AGW
    target: cust_company_info.identify_style
    evidence: code
field_targets:
  - cust_company_info.identify_style
belong: concepts
---

认证方式在库内为 identify_style（自主 / 邀请-客户录入 / 邀请-平台录入 / 简易），在提交逻辑中体现为 IdentifyTypeConstant 的 INVITE、SELF、INVITE_AGW 分支。

## 需求背景

认证方式决定提交后落到的建档状态（见 [[processes/cust_build_status_machine]]），也决定退回标记与来源补写的处理分支（[[rules/submit_cust_field_reset]]、[[calibers/cust_from_platform_invite]]）。

## 版本演进

v0：首次成页；「简易」对应的常量名在语义分析中未给出，不做推测。