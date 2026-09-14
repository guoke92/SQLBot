---
type: concept
title: CA
page_key: ca
domain: CA证书认证
status: draft
aliases: [CFCA, 数字证书, 电子签章]
oid: 1
scope:
  databases: [unknown]
sources: [code]
contract_version: "0.1"
maps_to: CFCA数字证书认证服务
adjudication: boundary
also_confused_with: [电子签名, 上上签]
field_targets: []
belong: concepts
---

「CA」在本主题中特指 CFCA 数字证书认证，是围绕企业数字证书开通、升级与失效回写的一整套服务，落地在 [[tables/ca_certification_info]]（开通链路）与 [[tables/ca_cfca_upgrade_report]]（升级异常上报）两张表上。

## 边界与辨析

- CA 特指 CFCA 数字证书认证；「电子签章」指签章中台提供的签章服务，是 CA 认证通过后调用的下游能力（例如上送签章中台、生成升级授权书，见 [[rules/upgrade_auth_online_seal]]）。
- 「上上签」是另一家第三方签章机构，代码中通过 SignAgency 区分，不属于本主题的 CA 范畴。
- 「电子签名」是更宽泛的行为描述，不指向具体机构与证书；本页的 CA 始终绑定 CFCA 证书。

因此在本契约中，CA 相关页面描述的是证书本体与认证流程，签章服务只在「上送」「盖章」等动作上被引用，不作为 CA 的同义词。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。术语映射与边界结论来自代码中的枚举与分支（data_source、verifyMethod、authType、SignAgency 等标识）。

## 版本演进

暂无文档化的版本演进证据。若后续出现其他 CA 机构接入，本页的 boundary 结论需要重新裁定。

相关页面：[[concepts/one_cert_four_steps]]、[[concepts/data_source]]、[[processes/ca_certification_submit_status]]。