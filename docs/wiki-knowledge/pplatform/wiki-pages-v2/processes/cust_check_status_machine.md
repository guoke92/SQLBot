---
type: process
title: 客户审核状态机
page_key: processes/cust_check_status_machine
domain: 外部渠道与银行对接
status: draft
aliases:
  - check_status
  - OperApiConstants.CheckStatus
  - 审核状态机
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:OperApiConstants.CheckStatus
  - code:CustAccessApplication#terminateBuildingFlow
  - code:CustAccessApplication#terminateChangingFlow
contract_version: "0.1"
---

# 客户审核状态机

## 业务定位

该状态机由 `cust_company_info.check_status` 承载，取值为 `OperApiConstants.CheckStatus` 下的 `CUST_CHECK_*` 常量族，描述企业建档资料在审核链路上的位置。它与建档状态（[[processes/cust_build_status_machine]]）彼此独立：同一企业可以"建档成功但审核退回"。

对外接口并不直接回传库内枚举，而是先做 `CheckStatus → RegStatus` 映射（`CUSTS001~CUSTS005` / `CUST404`）后再返回，因此 `CUSTS*` 属于开放接口协议值，不能当库存值使用（见 [[concepts/company_status_fields]]）。

## 需求背景

渠道重新建档或重新变更时，旧流程可能停在 `CUST_CHECK_CHECKING`。标准接口终止旧流程后统一落到 `CUST_CHECK_REJECT`：终止建档流程走 `terminateBuildingFlow`，终止运营变更流程走 `terminateChangingFlow`（该方法内注释说明 `changeRejectProcess` 已在库中落 `CUST_CHECK_REJECT`）。`remark` 字段在开放接口查询建档状态时作为 `checkDesc`（退回原因）回传。

## 版本演进

- v0.1（本页首版）：状态枚举与两条迁移均来自代码语义分析，尚无需求文档或变更单佐证。

```ground:state_machine
name: 客户审核状态机
field: cust_company_info.check_status
states:
  - value: CUST_CHECK_INIT
    label: 审核初始化
    source: code_enum
  - value: CUST_CHECK_CHECKING
    label: 审核中
    source: code_enum
  - value: CUST_CHECK_PASS
    label: 审核通过
    source: code_enum
  - value: CUST_CHECK_REJECT
    label: 审核拒绝/退回
    source: code_enum
  - value: CUST_BACK
    label: 退回
    source: code_enum
  - value: CUST_CHECK_BACKTOCUSTOM
    label: 退回客户补充
    source: code_enum
transitions:
  - from: CUST_CHECK_CHECKING
    event: 标准接口终止旧建档流程
    to: CUST_CHECK_REJECT
    evidence: "code_path:lowcode-pplatform-customer-management/.../cust/application/CustAccessApplication.java#terminateBuildingFlow"
  - from: CUST_CHECK_CHECKING
    event: 标准接口终止运营变更流程（changeRejectProcess 落库）
    to: CUST_CHECK_REJECT
    evidence: "code_path:lowcode-pplatform-customer-management/.../cust/application/CustAccessApplication.java#terminateChangingFlow（方法内注释：changeRejectProcess 已在库中落 CUST_CHECK_REJECT）"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 流程：[[processes/cust_build_status_machine]]、[[processes/cust_status_machine]]
- 术语：[[concepts/company_status_fields]]、[[concepts/reg_archive]]
- 口径：[[calibers/standard_api_registered]]