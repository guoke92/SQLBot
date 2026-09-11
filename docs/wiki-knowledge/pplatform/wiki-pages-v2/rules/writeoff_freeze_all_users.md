---
type: rule
title: 注销企业前先冻结企业下全部用户
page_key: rule.writeoff_freeze_all_users
domain: 数据权限与组织
status: draft
aliases: [注销前冻结全部用户, freezeCustAllUsers]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

企业注销时，先执行 freezeCustAllUsers 把该企业下全部用户冻结，再置企业状态为 WRITEOFF；即注销动作的实际生效依赖「用户先冻结」这一前置步骤。流转见 [[processes/cust_status_fsm]]，用户冻结体现为 [[tables/cust_person_info]].enable/N 与 status/FREEZE。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本规则由状态机中 custStatusOperator(freezeCustAllUsers) 的证据得出。

## 版本演进

v0：依据 code 证据成文。

```ground:rule
name: 注销前冻结全部用户
statement: 企业注销前必须先冻结该企业下全部用户
condition: 企业状态由 EFFECT 走向 WRITEOFF
action: 调用 freezeCustAllUsers 冻结全部用户后再注销
evidence: code_path:CustCompanyInfoApplication.java#custStatusOperator(freezeCustAllUsers)
```