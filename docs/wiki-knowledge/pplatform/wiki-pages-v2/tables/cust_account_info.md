---
type: table
title: cust_account_info 企业银行账户表
page_key: tables/cust_account_info
domain: 企业银行账户
status: draft
aliases: [客户账号信息, 企业银行账户信息]
oid: 1
scope:
  databases: [unknown]
sources:
  - db
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java
contract_version: "0.1"
---

`cust_account_info` 是企业银行账户主表，承载账号、户名、开户行、认证状态与打款计数等要素，是「企业—银行账户」一对多关系的落地表。账户的真实性通过人行小额打款（CNAPS）验证：先申请打款，再回填金额验证，状态流转见 [[processes/account-cnaps-payment-auth-state]]。其中唯一的默认还款账户口径见 [[calibers/default-repayment-account]]。

## 需求背景

企业完成建档后需绑定银行账户用于资金动作（还款代扣等），因此需要一张账户表同时解决三件事：账户归属（[[concepts/account-owner-company]]）、账户真实性认证（[[calibers/account-payment-auth-passed]]）、默认账户唯一性（[[rules/default-account-unique]]）。打款申请上送的账号/户名/银行名称与联行号存在字段复用，边界见 [[concepts/bank-no]]；账户类型的真实取值集与代码枚举基线不一致，见 [[concepts/account-type]]。新增账户受 [[rules/account-no-unique-per-company]] 约束。

## 版本演进

v0 契约按现状固化：认证状态由 [[processes/account-cnaps-payment-auth-state]] 定义为 APPLY_00 / APPLY_10 / APPLY_20 / APPLY_30 / APPLY_40 五态，DB 默认 APPLY_00；`account_type` 代码枚举基线未覆盖实测存在的 OPERATION_FEE_ACCOUNT，待后续版本补齐；`bank_branch_name` 目前不参与打款申请链路。全表通用逻辑删除口径为 enable = 'Y'（见 [[calibers/valid-record-enable-y]]）。

## 字段语义锚点

```ground:fields
table: cust_account_info
fields:
  - field: account_no
    meaning: 企业银行账户账号（打款验证/默认还款账号载体）
    evidence: db
  - field: account_name
    meaning: 账户名称（户名），打款申请上送 accountName
    evidence: db
  - field: account_type
    meaning: 账户类型，DB 默认 BANK；实测另有 OPERATION_FEE_ACCOUNT（运营费账户），为代码枚举基线外的真实取值
    evidence: db
  - field: bank_no
    meaning: 联行号；代码中同时作为 bankID 与 cnapsCode 上送人行小额打款接口（bankNo 一值两用）
    evidence: code
  - field: bank_code / bank_code_name
    meaning: 银行(总行)代码/名称；申请打款时 bank_code_name 被当作请求 bankName 上送
    evidence: code
  - field: bank_branch_name
    meaning: 开户行网点名称，打款申请链路未使用
    evidence: db
  - field: default_account_flag
    meaning: 是否默认账户，'1'=默认，'0'=非默认；同企业下默认账号需唯一
    evidence: db
  - field: auth_state
    meaning: 小额打款认证状态，DB 默认 APPLY_00，代码取值 APPLY_00/10/20/30/40
    evidence: code
  - field: trans_id
    meaning: 打款申请交易ID（发起时写入银行返回的 OriginalTxSN，查询/验证均以它为准）
    evidence: code
  - field: trace_no
    meaning: 银行系统跟踪号（申请打款返回）
    evidence: code
  - field: payment_remaining_count
    meaning: 剩余打款次数，初始取 cust_setting_config.payment_maximum_number，每次申请 -1
    evidence: code
  - field: error_try_count
    meaning: 打款金额验证失败次数，失败时累加
    evidence: code
  - field: error_try_time
    meaning: 最后一次验证失败时间
    evidence: code
  - field: ref_cust_company_info
    meaning: 账户归属企业标识，存的是 cust_company_info.code（企业编码），不是企业主键 id
    evidence: code
  - field: status
    meaning: 账户状态，实测仅 INIT
    evidence: db
```