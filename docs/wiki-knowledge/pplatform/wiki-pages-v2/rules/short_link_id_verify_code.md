---
type: rule
title: 短链 ID 映射校验
page_key: short_link_id_verify_code
domain: notification
status: draft
aliases: [generateVerifyCode, LongBase64Utils.decode]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:71-90
contract_version: "0.1"
belong: rules
---

shortLink 接口取 number 最后一位为校验码，用 LongBase64Utils.decode 解出 id，并用 generateVerifyCode(link.number) 校验，防止短链被顺序枚举。字段含义见 [[short_link]] 的 number 与 id。

## 需求背景
短链对外可被穷举访问，需求侧要求短链码内嵌校验位，使猜测的 id 无法直接映射为可访问链接。

## 版本演进
- 当前校验在访问侧完成；生成侧如何写入校验位未在本次分析取得证据，见 REVIEW。

```ground:rule
name: 短链 ID 映射校验
content: shortLink 接口取 number 最后一位为校验码，LongBase64Utils.decode 得到 id，并用 generateVerifyCode(link.number) 校验
impact: 防止短链被枚举
field_targets:
  - short_link.number
  - short_link.id
evidence: ShortLinkController.java:71-90
```