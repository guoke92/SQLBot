---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-product-activation@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 邀请进度
page_key: progress
domain: 客户与建档
aliases:
- 邀请完成
- 邀请中企业
- 邀请状态
- 邀请进度跟踪
- 已邀请企业
anchors:
- progress
---
# 邀请进度

cust_invite_info.progress 是 cust_company_info.cust_build_status 的直接拷贝 （回调时 updateInviteCustProcess，按企业名+租户匹配写入）。progress=BUILD_SUCCESS 即"邀请完成"。

```ground:enum
enum: progress
fields:
- cust_invite_info.progress
values:
  INIT:
    label: 初始化
  BUILDING:
    label: 建档中
  BUILD_SUCCESS:
    label: 认证成功（邀请完成）
  BUILD_FAIL:
    label: 认证失败
  CUST_CHANGE:
    label: 变更
```

## 关联
- [[cust_invite_info|cust_invite_info]]
