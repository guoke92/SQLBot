---
type: process
title: 客户状态机
page_key: cust_status
domain: 外部渠道与银行对接
status: draft
aliases:
  - 客户状态
  - CustStatusEnum
  - CustStatusConstant
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.setCustCompany
  - code:CustAccessApplication.terminateChangingFlow
contract_version: "0.1"
belong: processes
---

客户状态表示企业在库生命周期（新增/变更中/作废），落库字段为 [[cust_company_info]].cust_status。

## 需求背景
建档落库即置为 ADD；标准 OpenAPI 发起企业变更后进入 CHANGE，只有 CHANGE 态才允许终止变更流程，这是变更流程终止的前置校验。作废态在查重时被排除，允许重新建档（[[writeoff_excluded]]）。

## 版本演进
暂无版本演进记录。

```ground:process
name: 客户状态
field: cust_company_info.cust_status
states:
  - value: ADD
    label: 新增/在库
    source: code_const
  - value: CHANGE
    label: 变更中
    source: code_enum
  - value: WRITEOFF
    label: 作废
    source: code_const
transitions:
  - from: "*"
    event: 建档落库
    to: ADD
    evidence: "code_path:CustAccessApplication.setCustCompany → company.setCustStatus(CustStatusConstant.ADD)"
  - from: ADD
    event: 标准 OpenAPI 发起企业变更
    to: CHANGE(经运营变更流程)
    evidence: "code_path:CustAccessApplication.terminateChangingFlow 前置判断 CustStatusEnum.CHANGE.getDictKey().equals(company.getCustStatus())"
```