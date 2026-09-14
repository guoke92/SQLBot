---
type: rule
title: "统一社会信用代码一致性校验"
page_key: social_unified_code_check
domain: "customer-onboarding"
status: draft
aliases:
  - "信用代码一致性校验"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustValidatorProcessor.java:validate"
contract_version: "0.1"
belong: rules
---

回调携带的统一社会信用代码必须与本地企业的 `certification_no` 一致，否则直接抛异常阻断；变更流程与来源 id 缺失的场景被显式放行。这条规则是防止串户的关键闸门，载体表见 [[tables/cust_company_info]]。

## 需求背景

中台以 sourceId 关联企业，若中台侧代码与企业绑定发生错位，会把 A 企业的审核结论写到 B 企业上，因此需要代码级一致性校验。

## 版本演进

- 放行条件（`process=change` 或 `sourceId` 为空）是后加的兼容分支，变更流程不走该校验；因此变更链路的防串户依赖其他机制，见 [[processes/change_record_check_machine]]。

```ground:rule
name: "统一社会信用代码一致性校验"
content: "运营中台回调校验：process=change 或 sourceId 为空直接放行；否则按 sourceId 查企业，回调 socialUnifiedCode 与企业 certificationNo 不一致时抛『统一信用代码不一致』。"
impact: "阻断错误企业回调"
field_targets:
  - "cust_company_info.certification_no"
evidence: "code_path:CustValidatorProcessor.java:validate"
```

相关：[[tables/cust_company_info]]、[[processes/workflow_check_status_machine]]。