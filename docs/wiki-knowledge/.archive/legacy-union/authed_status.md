---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 授权书签署状态
page_key: authed_status
domain: CA认证与服务费
aliases:
- 已签授权书
- 未签授权书
- 平台授权
- 授权书已签
- 授权书未签
- 平台授权
anchors:
- authed_status
---
# 授权书签署状态

authorization_agreement.authed_status：N（流程启动建）→ Y（审批通过）；管理员变更旧行停用新行重建。

```ground:enum
enum: authed_status
fields:
- authorization_agreement.authed_status
values:
  Y:
    label: 已签署
  N:
    label: 未签署
```

## 关联
- [[authorization_agreement|authorization_agreement]]
