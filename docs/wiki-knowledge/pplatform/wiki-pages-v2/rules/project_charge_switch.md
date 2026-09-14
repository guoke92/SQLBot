---
type: rule
title: 项目收费开关规则
page_key: project_charge_switch
domain: CA证书收费
status: draft
aliases:
  - 收费开关
  - PROJECT_DISABLED
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeRuleEngineService.java
contract_version: "0.1"
belong: rules
---

项目无 [[ca_fee_project_config]] 行或 `charge_enabled <> 'Y'` 时，规则引擎直接返回 `EXEMPT`，`needPay=false`，`exemptReason=PROJECT_DISABLED`。这是收费流程的**第一道闸门**，口径见 [[project_charge_enabled]]，多项目场景的放行见 [[multi_project_pass]]。

## 需求背景

收费按项目灰度：未开放收费的项目必须完全不产生待缴与拦截，故把「无配置」与「开关关闭」统一收敛为同一豁免结果。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 项目收费开关规则
content: 项目无 ca_fee_project_config 或 charge_enabled<>'Y' 时，规则引擎直接返回 EXEMPT，needPay=false，exemptReason=PROJECT_DISABLED
impact: 决定是否进入CA服务费收费流程
field_targets:
  - ca_fee_project_config.charge_enabled
evidence: CaFeeRuleEngineService.evaluate
```