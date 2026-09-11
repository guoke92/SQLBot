---
type: rule
title: "管理员唯一校验的退回豁免"
page_key: "rules/admin_unique_check_reject_exemption"
domain: "customer-onboarding"
status: draft
aliases:
  - "退回场景豁免唯一校验"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustAuthValidatorProcessor.java:validate"
contract_version: "0.1"
---

回调校验链中，若 `rtfState` 含「拒绝」「退回」「补充」，校验器直接返回，不再执行管理员信息唯一性校验。这是为了让退回/补充场景的回传不被本地校验阻断，与 [[calibers/company_admin_unique_check]] 的唯一性口径配套。

## 需求背景

需求文档要求企业修改信息后重新提交；在退回/补充阶段，联系人信息可能处于中间态（尚未替换完成），若仍执行唯一校验会阻断整个回传链路。

## 版本演进

- 豁免以 `rtfState` 文案包含关系判定（含「拒绝」「退回」「补充」），而非枚举匹配；中台文案变化可能使豁免失效，需回归 [[tables/cust_person_info]] 相关校验。

```ground:rule
name: "管理员唯一校验的退回豁免"
content: "CustAuthValidatorProcessor.validate 中，rtfState 含『拒绝』『退回』『补充』时直接 return，不执行管理员信息唯一性校验。"
impact: "退回/补充场景不阻断回传"
field_targets:
  - "cust_person_info.name"
  - "cust_person_info.certification_no"
  - "cust_person_info.email"
evidence: "code_path:CustAuthValidatorProcessor.java:validate"
```

相关：[[calibers/company_admin_unique_check]]、[[tables/cust_person_info]]、[[processes/company_build_status_machine]]。