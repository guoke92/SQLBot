---
type: rule
title: 变更申请前置校验
page_key: change_precheck
domain: 企业变更与运营变更
status: draft
aliases: [changeEnable, 是否可变更校验]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
belong: rules
---

**(document_claim，未证实)**

规则内容：当企业 `check_status = CUST_CHECK_CHECKING`（准入审核中）时，`changeEnable` 返回 false，不允许发起变更，直接阻断变更申请入口。判定口径见 [[checking_company_cannot_change]]。

## 需求背景

准入审核与信息变更会写同一批企业资质字段，准入审核中再发起变更会造成两端状态互相覆盖，因此在入口处拦截，避免脏数据进入变更流程。

## 版本演进

v0.1：代码侧仅覆盖「准入审核中」一种情形。需求文档 3.4.3 主张「企业状态为『已冻结』或『已注销』时不允许变更」，语义分析判定为 uncovered：`CustChangeApplication.java#changeEnable` 仅校验 `check_status=CUST_CHECK_CHECKING`，未见 `cust_status=FREEZE/WRITEOFF` 拦截。该主张未经证实，暂不进入锚点块，也不作为现有规则的一部分。

```ground:rule
name: 变更申请前置校验
content: "企业 check_status=CUST_CHECK_CHECKING（准入审核中）时 changeEnable 返回 false，不允许发起变更"
impact: 阻断变更申请入口
field_targets:
  - cust_company_info.check_status
evidence: "code_path:CustChangeApplication.java#changeEnable"
```

相关页面：[[checking_company_cannot_change]]、[[cust_company_info]]、[[change_on_way]]、[[cust_company_info_cust_status]]。

---REVIEW: rule | 变更申请前置校验---
需求文档 3.4.3（企业状态为「已冻结」或「已注销」时不允许变更）与代码现状不一致：`changeEnable` 只拦 `CUST_CHECK_CHECKING`，没有冻结/注销拦截。需确认是文档过期、校验落在前端或其他入口，还是确实缺失实现；在确认前，本页不为其生成锚点。
---END REVIEW---