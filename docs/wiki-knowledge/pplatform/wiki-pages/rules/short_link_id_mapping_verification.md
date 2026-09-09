---
type: rule
title: 短链接ID映射校验
page_key: short_link_id_mapping_verification
belong: rules
domain: 通知验证码短链与消息
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
field_targets: [short_link.number]
scope:
  databases: [lowcode_pplatform]
---

本规则约束短链 `/sl/{number}` 路径的校验逻辑：number 最后一位为校验码，前端截取前部分用 LongBase64Utils.decode 解码为 id，再校验最后一位与 `generateVerifyCode(link.getNumber())` 一致性，防止伪造。

## 需求背景

短链访问通过 number 定位时需防止伪造，此规则与短链编码结构相关。表 [[short_link]]，概念 [[short_link]]。

## 版本演进

基于 code_path:ShortLinkController.shortLink 证据形成 v0.1 契约。

```ground:rule
name: 短链接ID映射校验
content: /sl/{number}路径中number最后一位为校验码，前端截取前部分用LongBase64Utils.decode解码为id，再校验最后一位与generateVerifyCode(link.getNumber())一致性
impact: 防止短链被伪造
field_targets: [short_link.id, short_link.number]
evidence: code_path:ShortLinkController.shortLink
```