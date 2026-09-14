---
type: caliber
title: 项目开启CA收费
page_key: project_charge_enabled
domain: CA证书收费
status: draft
aliases:
  - charge_enabled = Y
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeRuleEngineService.java
contract_version: "0.1"
belong: calibers
---

该口径判定一个项目是否进入 CA 服务费收费流程，是规则引擎评估的**前置条件**：项目不存在 [[ca_fee_project_config]] 行或 `charge_enabled <> 'Y'` 时直接豁免（见 [[project_charge_switch]]）。多项目企业按项目逐个通过本口径筛选后再评估（见 [[multi_project_pass]]）。

## 需求背景

收费按项目灰度开放，本口径是「不收费」与「可能收费」的分界线，必须先于定价与豁免判定执行。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 项目开启CA收费
predicate: ca_fee_project_config.charge_enabled = 'Y'
scope: 规则引擎评估收费项目的前置条件
evidence: CaFeeRuleEngineService.java
```