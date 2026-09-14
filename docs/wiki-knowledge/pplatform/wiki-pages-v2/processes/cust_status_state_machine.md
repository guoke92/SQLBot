---
type: process
title: 企业状态机（cust_company_info.cust_status）
page_key: cust_status_state_machine
domain: 准入接入与接入密钥
status: draft
aliases:
  - 企业主体状态机
  - 客户状态流转
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustCompanyInfoApplication.java:updateCustBuildStatus
  - code:CustCompanyInfoApplication.java:freeze
  - code:CustCompanyInfoApplication.java:unfreeze
  - code:CustCompanyInfoApplication.java:diable
contract_version: "0.1"
belong: processes
---

# 企业状态机

## 业务定位

该状态机描述 [[tables/cust_company_info|cust_company_info]] 中 `cust_status` 字段的取值与流转，刻画企业主体在平台上的生命周期：新增 → 生效 → 冻结/解冻 → 注销。它与建档状态（[[processes/cust_build_status_state_machine|企业建档准入状态机]]）不是同一维度：建档成功会推动 `cust_status` 从 `ADD` 进入 `EFFECT`，但建档态本身不因冻结而回退。

## 需求背景

企业主体需要独立支持冻结与注销，冻结/解冻不改变建档结果；注销（`WRITEOFF`）作为终态，在天马重复校验中被用作排除条件（见 [[calibers/tianma_duplicate_exclude_writeoff|天马重复校验排除已注销]]）。

## 版本演进

给定证据仅覆盖 ADD→EFFECT、EFFECT↔FREEZE、EFFECT→WRITEOFF 四条迁移，`CHANGE`（变更中）的进入与退出条件未在证据中出现。

```ground:process
name: 企业状态机
field: cust_company_info.cust_status
states:
  - value: ADD
    label: 新增/初始
    source: code_const
  - value: EFFECT
    label: 生效
    source: code_enum
  - value: FREEZE
    label: 冻结
    source: code_enum
  - value: WRITEOFF
    label: 注销
    source: code_enum
  - value: CHANGE
    label: 变更中
    source: code_enum
transitions:
  - from: ADD
    event: 建档成功
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java:updateCustBuildStatus"
  - from: EFFECT
    event: 冻结
    to: FREEZE
    evidence: "code_path:CustCompanyInfoApplication.java:freeze"
  - from: FREEZE
    event: 解冻
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java:unfreeze"
  - from: EFFECT
    event: 注销/禁用
    to: WRITEOFF
    evidence: "code_path:CustCompanyInfoApplication.java:diable"
```

相关联的建档结果语义见 [[concepts/build_success|建档成功]]。

---REVIEW: process | 企业状态机
- `CHANGE`（变更中）的迁移条件未在证据中出现，需补充代码路径。
- FREEZE/WRITEOFF 是否可逆（WRITEOFF 后能否恢复）未确认。
---END REVIEW---