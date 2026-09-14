---
type: rule
title: 管理员变更走企业变更流程
page_key: admin_change_company_flow
domain: 经办人/联系人/管理员管理
status: draft
aliases: [copyCustRecordAndStartApply, cust_status=EFFECT]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonApplication.java#updateAuthorAndApply"]
contract_version: "0.1"
belong: rules
---

管理员变更不是独立动作，而是通过企业变更流程（copyCustRecordAndStartApply）承载；仅当企业 cust_status=EFFECT 时才启动，非 EFFECT 状态下静默不启动、不抛异常（[[cust_company_info]]、[[admin]]）。

## 需求背景
- 由于是"静默不启动"，冻结/注销企业下的变更请求表现为"提交成功但无后续流程"，排障时需优先检查企业状态（[[company_status_cascade_person]]）。

## 版本演进
- 当前版本未对非 EFFECT 场景给出用户提示，属已知行为差异。

```ground:rule
name: 管理员变更走企业变更流程
content: "仅当企业 cust_company_info.cust_status=EFFECT 时才 copyCustRecordAndStartApply 启动变更流程；非 EFFECT 时静默不启动（不抛异常）"
impact: 冻结/注销企业无法发起管理员变更
field_targets:
  - cust_company_info.cust_status
evidence: "code_path:CustPersonApplication.java#updateAuthorAndApply"
```

相关页面：[[cust_company_info]]、[[admin]]、[[company_status_cascade_person]]、[[admin_change_freeze_create]]。