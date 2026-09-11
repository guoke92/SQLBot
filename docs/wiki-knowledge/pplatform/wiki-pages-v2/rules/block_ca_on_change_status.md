---
type: rule
title: 变更态拦截CA开通
page_key: rule/block_ca_on_change_status
domain: CA证书认证
status: draft
aliases: [assertCompanyNotInChange]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaCertificationPreCheckApplication.java:assertCompanyNotInChange"]
contract_version: "0.1"
---

规则要求：企业在变更态时禁止进入一证四步——cust_company_info.cust_status=CHANGE 或 cust_company_info.cust_build_status=CUST_CHANGE 都会触发拦截，抛出异常提示先完成变更流程。

拦截发生在认证前置检查阶段，早于 [[tables/ca_certification_info]] 的建行与上送，因此不会产生 PENDING 行（对比 [[calibers/ca_row_idempotent_key]]）。其业务动因是：企业身份信息在变更中，此时核验与证书登记名都不可靠，开通后极易触发名称不一致的回写（[[rules/ca_invalidate_writeback]]）与升级授权书补签（[[rules/upgrade_auth_online_seal]]）。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。两个触发字段与取值来自代码路径证据。

## 版本演进

暂无文档化的版本演进证据。同一前置检查类中还包含管理员校验（[[rules/admin_check]]）。

```ground:rule
name: 变更态拦截CA开通
content: 企业cust_status=CHANGE或cust_build_status=CUST_CHANGE时，禁止进入一证四步。
impact: 抛出异常提示先完成变更流程
field_targets:
  - cust_company_info.cust_status
  - cust_company_info.cust_build_status
evidence: "code_path:CaCertificationPreCheckApplication.java:assertCompanyNotInChange"
```

相关页面：[[rules/admin_check]]、[[rules/ca_invalidate_writeback]]、[[concepts/one_cert_four_steps]]。