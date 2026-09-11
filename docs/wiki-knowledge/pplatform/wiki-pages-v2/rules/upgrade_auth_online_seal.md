---
type: rule
title: 升级授权书在线盖章条件
page_key: rule/upgrade_auth_online_seal
domain: CA证书认证
status: draft
aliases: [processUpgradeAuthOnOpsNameChange]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaUpgradeAuthApplication.java:processUpgradeAuthOnOpsNameChange"]
contract_version: "0.1"
---

规则要求：当签章中台证书登记名与运营中台企业名不一致且证书状态为 NORMAL 时，在线签署升级授权书，并上传运营中台与产融影像，回写 file_refs_json。影响是企业名称变更后重新开通 CA 需签署升级授权书。

判定条件是「名称不一致 + 证书仍 NORMAL」这一组合：名称不一致但证书已失效时走的是失效回写路径（[[rules/ca_invalidate_writeback]]），而不是补签授权书。签名与影像材料的落点是 [[tables/ca_certification_info]] 的 file_refs_json，该字段同时是上送签章中台的前置材料（[[rules/submit_sign_center_completeness]]）。名称来源区分运营中台与产融两个影像渠道，与 data_source 的入口语义不同（[[concepts/data_source]]）。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。触发条件、上传来源与回写字段来自代码路径证据。升级过程的异常会上报到 [[tables/ca_cfca_upgrade_report]]。

## 版本演进

暂无文档化的版本演进证据。

```ground:rule
name: 升级授权书在线盖章条件
content: 签章中台证书登记名与运营中台企业名不一致且证书状态为NORMAL时，在线签署升级授权书，并上传运营中台与产融影像，回写file_refs_json。
impact: 企业名称变更后重新开通CA需签署升级授权书
field_targets:
  - ca_certification_info.file_refs_json
  - ca_certification_info.notify_agreement_json
evidence: "code_path:CaUpgradeAuthApplication.java:processUpgradeAuthOnOpsNameChange"
```

相关页面：[[rules/ca_invalidate_writeback]]、[[tables/ca_cfca_upgrade_report]]、[[concepts/ca]]。