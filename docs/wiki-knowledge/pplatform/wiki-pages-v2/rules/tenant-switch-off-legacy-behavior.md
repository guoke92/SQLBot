---
type: rule
title: 租户开关关闭时保持现网行为
page_key: tenant-switch-off-legacy-behavior
domain: 授权协议与电子授权
status: draft
aliases:
  - 电子授权开关回退规则
  - isGenerateElectronicAuth
oid: 1
scope:
  databases: [unknown]
sources:
  - code:ElectronicAuthLetterApplication.java
  - db:tenant_setting_config
contract_version: "0.1"
belong: rules
---

当租户开关 `generate_electronic_auth_flag` 非 `Y`——包括配置不存在、值为空、以及查询异常——`signOfflineElectronicAuthOnLine` 直接返回 `true`，既不做 CFCA 校验也不发起签署，从而保持现网线下纸质授权行为。该规则是 [[concepts/offline-electronic-auth]] 的失败安全设计，同时构成 [[calibers/offline-electronic-auth-trigger]] 的一部分。

## 需求背景
电子签署能力需要可灰度、可一键回退；把「配置缺失/查询异常」与「显式关闭」归为同一结果，避免依赖故障导致误发起签署。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的规则。该条证据在语义分析中被截断（`code_path:ElectronicAuthLetterApplication.java#isGenerateElectronicA`），精确方法名待补全，见文末 REVIEW。

```ground:rule
name: 租户开关关闭时保持现网行为
content: "tenant_setting_config.generate_electronic_auth_flag 非 Y（含配置不存在、为空、查询异常）时，signOfflineElectronicAuthOnLine 直接返回 true，不做 CFCA 校验也不发起签署。"
impact: "开关是灰度/回退的唯一入口"
field_targets:
  - tenant_setting_config.generate_electronic_auth_flag
evidence: "code_path:ElectronicAuthLetterApplication.java#isGenerateElectronicA"
```