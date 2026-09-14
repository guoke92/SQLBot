---
type: process
title: 企业状态机
page_key: cust_status_flow
domain: 平台内部服务对接
status: draft
aliases:
  - 企业生效状态流转
  - cust_company_info.cust_status 状态机
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
belong: processes
---

企业状态机描述 [[cust_company_info]] 上 `cust_status` 字段的取值与流转，覆盖企业从新增到生效、冻结、注销的生命周期。它与建档状态（见 [[cust_build_status_flow]]）是两条独立的轨道：建档成功推动企业进入生效，而冻结/解冻与注销只在本状态机上发生。

冻结用于临时停用企业（如风险控制），解冻恢复到生效；注销是不可逆的终态，对应平台侧的注销操作。企业的启用标记 `enable` 与状态口径的关系见 [[valid_company]]，避免出现「已注销但被当作有效企业查出」的情形。

## 需求背景
运营侧服务需要在企业维度执行冻结、解冻与注销，客户侧与其它内部服务则需要按生效状态判断企业是否可用。状态语义必须集中在单一字段上，冻结/解冻成对出现，注销作为终态不再回到生效。

## 版本演进
- v0.1（本页）：状态与流转来自代码语义分析；`ADD → CHANGE` 等变更类流转在证据中未出现，暂不记录。企业有效性的查询口径见 [[valid_company]]。

```ground:process
name: 企业状态机
field: cust_company_info.cust_status
states:
  - value: ADD
    label: 新增
    source: code_enum
  - value: EFFECT
    label: 生效
    source: code_enum
  - value: CHANGE
    label: 变更中
    source: code_enum
  - value: FREEZE
    label: 冻结
    source: code_enum
  - value: WRITEOFF
    label: 注销
    source: code_enum
transitions:
  - from: ADD
    event: 建档成功
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java:confirmCustInfoForSimpleAuth"
  - from: EFFECT
    event: 冻结企业
    to: FREEZE
    evidence: "code_path:CustCompanyInfoApplication.java:freeze"
  - from: FREEZE
    event: 解冻企业
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java:unfreeze"
  - from: EFFECT
    event: 注销企业
    to: WRITEOFF
    evidence: "code_path:CustCompanyInfoApplication.java:diable"
```