---
type: process
title: 企业认证状态机
page_key: cust_build_status_flow
domain: 平台内部服务对接
status: draft
aliases:
  - 企业建档状态流转
  - cust_company_info.cust_build_status 状态机
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
belong: processes
---

企业认证状态机描述 [[cust_company_info]] 上 `cust_build_status` 字段的取值与流转，是平台内部服务对接中「客户录入 / 平台录入 → 客户确认 → 运营审核 → 建档成功或失败」这条链路的契约表达。字段本身仍是表 [[cust_company_info]] 的一部分，本页只描述其状态语义。

流转的关键分叉在于提交建档的入口：邀请认证模式下若由客户录入或客户自行注册认证，企业先进入待客户确认；若由平台录入，则直接进入客户建档中。之后由客户提交审核推动到建档中，运营中台审核通过或拒绝分别到达建档成功与建档失败，审核退回则回到待客户确认；建档失败后可重新提交并回到待客户确认。相关状态展示于企业的启用与审核字段旁，见 [[cust_status_flow]]。

## 需求背景
客户侧与运营侧服务读写同一状态字段，任何一侧都需要知道「当前轮到谁处理」。因此状态取值必须是稳定的枚举字符串，而不是可自由拼写的文案；审核退回与重新提交也必须回到确定的节点，避免出现两侧都无法处理的中间态。

## 版本演进
- v0.1（本页）：状态与流转来自代码语义分析，`AWAIT_CUST_CONFIRM`（待客户确认（简易））在证据中只有状态定义，未给出迁移边，暂按孤立状态记录。

```ground:process
name: 企业认证状态机
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始化
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: CUST_BUILDING
    label: 客户建档中
    source: code_enum
  - value: BUILD_SUCCESS
    label: 建档成功
    source: code_enum
  - value: BUILD_FAIL
    label: 建档失败
    source: code_enum
  - value: AWAIT_CUST_CONFIRM
    label: 待客户确认（简易）
    source: code_enum
transitions:
  - from: INIT
    event: 提交建档（邀请认证-客户录入/注册认证）
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:getCustBuildStatus"
  - from: INIT
    event: 提交建档（邀请认证-平台录入）
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:getCustBuildStatus"
  - from: CUST_CONFIRM_AWAIT
    event: 客户提交审核
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 运营中台审核退回
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 审核通过
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 审核拒绝
    to: BUILD_FAIL
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: BUILD_FAIL
    event: 重新提交（客户录入）
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
```