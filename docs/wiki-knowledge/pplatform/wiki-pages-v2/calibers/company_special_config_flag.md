---
type: caliber
title: 企业存在特殊配置快照
page_key: company_special_config_flag
domain: CA证书收费
status: draft
aliases:
  - special_config_flag = Y
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
  - code_path:CaFeeRuleEngineService.java
contract_version: "0.1"
belong: calibers
---

该口径指 [[ca_fee_company]] 中 `special_config_flag = 'Y'`，用于白名单／定向减免判定。它是企业侧**快照**标记，需与项目配置 `ca_fee_project_config.special_company_list` 交叉校验后才生效，辨析见 [[whitelist]]，落规则见 [[whitelist_exempt]]。

## 需求背景

规则引擎需要在评估时快速判断企业是否处于特殊名单，故在企業主数据上冗余快照标记；配置源仍在项目侧，二者不一致时应以交叉校验结果为准。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 企业存在特殊配置快照
predicate: ca_fee_company.special_config_flag = 'Y'
scope: 白名单/定向减免判定
evidence: db + CaFeeRuleEngineService.java
```