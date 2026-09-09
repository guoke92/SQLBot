---
type: rule
title: "电子授权书关闭跳过签署"
page_key: electronic_auth_skip_when_disabled_rule
belong: rules
domain: "授权协议与电子授权"
status: published
aliases: ["电子授权书开关关闭跳过", "OFF_AUTH 跳过签署"]
oid: 1

sources: ["code:ElectronicAuthLetterApplication.signOfflineElectronicAuthOnLine", "enrich:wiki-admin"]
contract_version: "0.1"
coverage_note: "电子授权书签署流程"
scope:
  databases: [lowcode_pplatform]
---

该规则定义当租户未开启 [[电子授权书]] 生成开关时，线下电子签约版签署流程直接返回成功，保持现网 OFF_AUTH 跳过签署行为。

## 需求背景

[[租户电子授权书开启口径]] 若为否，则签署操作不应执行。本规则确保关闭状态下不触发线下电子签约版签署。

## 版本演进

暂无。

```ground:rule
name: 电子授权书关闭跳过签署
content: "租户未开启 generateElectronicAuthFlag 时，signOfflineElectronicAuthOnLine 直接返回 true，保持现网 OFF_AUTH 跳过签署行为"
impact: "电子授权书功能关闭时不触发线下电子签约版签署"
field_targets:
  - "tenant_setting_config.generateElectronicAuthFlag"
evidence: "code_path:ElectronicAuthLetterApplication.signOfflineElectronicAuthOnLine"
```