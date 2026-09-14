---
type: caliber
title: 运营企业ID一致性口径
page_key: oper_platform_id_consistency
domain: 外部渠道与银行对接
status: draft
aliases:
  - plat_cust_id 一致性
  - 运营企业ID对账口径
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.resolveBuildPlatformCustIdForOper
contract_version: "0.1"
belong: calibers
---

运营中台企业 ID 在两个来源不一致时以 cust_role_info 为准并告警。

## 需求背景
该值决定是否拉起或终止中台流程，取错会造成流程挂空。冲突处理规则见 [[oper_platform_id_priority]]，两个来源表见 [[cust_build_record]] 与 [[cust_role_info]]。

## 版本演进
暂无版本演进记录。

```ground:caliber
name: 运营企业ID一致性口径
predicate: "cust_build_record.plat_cust_id = cust_role_info.platform_cust_id"
scope: 不一致时以 cust_role_info 为准并告警
evidence: "code:CustAccessApplication.resolveBuildPlatformCustIdForOper"
```