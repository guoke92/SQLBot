---
type: rule
title: 运营企业ID冲突以 cust_role_info 为准
page_key: oper_platform_id_priority
domain: 外部渠道与银行对接
status: draft
aliases:
  - plat_cust_id 冲突处理
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.resolveBuildPlatformCustIdForOper
contract_version: "0.1"
belong: rules
---

建档记录与角色表记录的运营中台企业 ID 不一致时，告警并取角色表值。

## 需求背景
该值决定是否拉起/终止中台流程，取错会导致流程挂空或误终止。涉及表见 [[cust_build_record]]、[[cust_role_info]]，判定口径见 [[oper_platform_id_consistency]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 运营企业ID冲突以 cust_role_info 为准
content: cust_build_record.plat_cust_id 与 cust_role_info.platform_cust_id 不一致时告警并取 role 值
impact: 是否拉起/终止中台流程的判定
field_targets:
  - cust_build_record.plat_cust_id
  - cust_role_info.platform_cust_id
evidence: "code:CustAccessApplication.resolveBuildPlatformCustIdForOper"
```