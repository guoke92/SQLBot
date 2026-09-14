---
type: process
title: 企业建档准入状态机（cust_company_info.cust_build_status）
page_key: cust_build_status_state_machine
domain: 准入接入与接入密钥
status: draft
aliases:
  - 建档状态机
  - 准入状态流转
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustCompanyInfoApplication.java:getCustBuildStatus
  - code:CustAuditMsgService.java:getCustBuildStatus
  - code:CustCompanyInfoApplication.java:messageNotify
  - code:CustCompanyInfoApplication.java:confirmCustInfoForSimpleAuth
contract_version: "0.1"
belong: processes
---

# 企业建档准入状态机

## 业务定位

该状态机描述 [[tables/cust_company_info|cust_company_info]] 上 `cust_build_status` 字段的取值与流转，覆盖「提交建档 → 待客户确认 / 审核中 → 建档成功 / 失败 → 修改后重新提交」的完整闭环。

两条分支入口由 [[concepts/independent_reg|自主建档]]（`identify_style=INVITE`/`SELF`）与 [[concepts/dependent_reg|非自主建档]]（`identify_style=INVITE_AGW`）决定：前者先进待客户确认，后者直接进审核中。运营中台回调（`CustAuditMsgService`）负责推进审核通过与拒绝。

## 需求背景

建档结果需要与运营中台审核态解耦（见 [[concepts/await_cust_confirm|待客户确认]]、[[concepts/build_success|建档成功]]），运营中台退回时本地必须回到待客户确认，拒绝时必须落失败态并允许客户修改后重新提交。

## 版本演进

- `CUST_BUILDING` 与 `BUILDING` 并存：查询分支使用 `BUILDING`，回调分支使用 `CUST_BUILDING`，两者关系待核对。
- `CUST_CONFIRM_AWAIT` 与 `AWAIT_CUST_CONFIRM` 并存：邀请/自主流程用前者，简易认证分支用后者，需核对字典键。
- `BUILD_FAIL` 之后的重新提交路径只在 `messageNotify` 中处理，需要确认是否所有入口共用。

```ground:process
name: 企业建档准入状态机
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始化
    source: code_const
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: CUST_BUILDING
    label: 运营中台审核中
    source: code_enum
  - value: BUILDING
    label: 建档中/审核中（查询分支使用，需核对与CUST_BUILDING关系）
    source: code_enum
  - value: BUILD_SUCCESS
    label: 建档成功
    source: code_enum
  - value: BUILD_FAIL
    label: 建档失败
    source: code_enum
  - value: AWAIT_CUST_CONFIRM
    label: 待客户确认（简易认证分支，需核对与CUST_CONFIRM_AWAIT关系）
    source: code_enum
transitions:
  - from: INIT
    event: 提交建档且identify_style为INVITE/SELF
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:getCustBuildStatus"
  - from: INIT
    event: 提交建档且identify_style为INVITE_AGW
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:getCustBuildStatus"
  - from: CUST_BUILDING
    event: 运营中台退回客户确认CUST_CHECK_BACKTOCUSTOM
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustAuditMsgService.java:getCustBuildStatus"
  - from: CUST_CONFIRM_AWAIT
    event: 客户确认提交/运营审核中CUST_CHECK_CHECKING
    to: CUST_BUILDING
    evidence: "code_path:CustAuditMsgService.java:getCustBuildStatus"
  - from: CUST_BUILDING
    event: 运营中台审核通过CUST_CHECK_PASS
    to: BUILD_SUCCESS
    evidence: "code_path:CustAuditMsgService.java:getCustBuildStatus"
  - from: CUST_CONFIRM_AWAIT
    event: 运营中台审核通过CUST_CHECK_PASS
    to: BUILD_SUCCESS
    evidence: "code_path:CustAuditMsgService.java:getCustBuildStatus"
  - from: CUST_BUILDING
    event: 运营中台审核拒绝CUST_CHECK_REJECT
    to: BUILD_FAIL
    evidence: "code_path:CustAuditMsgService.java:getCustBuildStatus"
  - from: CUST_CONFIRM_AWAIT
    event: 运营中台审核拒绝CUST_CHECK_REJECT
    to: BUILD_FAIL
    evidence: "code_path:CustAuditMsgService.java:getCustBuildStatus"
  - from: BUILD_FAIL
    event: 修改后重新提交且identify_style为INVITE/SELF
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: AWAIT_CUST_CONFIRM
    event: 简易认证确认提交
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java:confirmCustInfoForSimpleAuth"
```

关联：[[processes/cust_check_status_state_machine|运营审核状态机]] 的推进事件是本状态机的驱动源；建档成功会联动 [[processes/cust_status_state_machine|企业状态机]] 进入 EFFECT。

---REVIEW: process | 企业建档准入状态机
- `BUILDING` 与 `CUST_BUILDING` 是否为同一状态的两种写法，语义分析未给出结论，需核对字典与查询分支。
- `AWAIT_CUST_CONFIRM` 与 `CUST_CONFIRM_AWAIT` 的关系未确认（是否为同一 dictKey 的不同分支值）。
- 简易认证分支（`confirmCustInfoForSimpleAuth`）只给出到 BUILD_SUCCESS 的迁移，是否存在失败分支未知。
---END REVIEW---