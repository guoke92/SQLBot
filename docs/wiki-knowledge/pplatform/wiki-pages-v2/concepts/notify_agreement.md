---
type: concept
title: 协议告知
page_key: notify_agreement
domain: CA证书认证
status: draft
aliases: [notifyAgreementList, notify_agreement_json]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
maps_to: ca_certification_info.notify_agreement_json
field_targets:
  - ca_certification_info.notify_agreement_json
  - ca_certification_info.file_refs_json
adjudication: boundary
also_confused_with:
  - ca_certification_info.file_refs_json
belong: concepts
field_targets: [ca_certification_info.notify_agreement_json]
---

协议告知指用户在上送前逐条确认的协议清单留痕，落库为 notify_agreement_json：CfcaNotifyAgreementItemDto 列表序列化成 JSONArray（固定数组结构）。它是 [[submit_completeness|一证四步上送完整性口径]] 中唯一"必须非空"的前置项。

**边界（boundary）**：协议告知是留痕 JSON 数组；同一条协议的文件路径另有 embeddedFiles 映射进 file_refs_json，两者通过 serviceKey/agreementUrl 关联但不共列。因此"协议告知为空"与"协议文件缺失"是两个独立故障，不能相互推断。

## 需求背景

协议清单中至少包含数字证书服务协议（CFCA_Auth）与 [[ca_upgrade_auth|CA 升级授权书]]（CaUpgradeAuth）等不同 serviceKey 的条目，filterUpgradeAuthContracts 在选择升级授权书时还需排除 CFCA_Auth 文件，详见 [[ca_upgrade_auth]]。

## 版本演进

- v0：首次固化 JSONArray 结构（固定数组，非对象）与 file_refs_json 的分工。

关联页面：[[ca_certification_info]]、[[ca_upgrade_auth]]、[[submit_completeness]]、[[submit_completeness_check]]。