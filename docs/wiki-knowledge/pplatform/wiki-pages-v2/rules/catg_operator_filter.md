---
type: rule
title: 特定分类按操作人过滤
page_key: catg_operator_filter
domain: 文件/附件/媒体
status: draft
aliases: [按操作人过滤影像]
oid: 1
scope:
  databases: [unknown]
sources: ["code:PlatFormMediaApplication.java:lookupCustMedia"]
contract_version: "0.1"
belong: rules
---
查询影像时，对 A0004/A0011/A0012 分类的文件只保留 userBusiKey 等于当前管理员 id 的记录，确保授权书与操作人证件只返回当前操作人的影像。涉及分类口径 [[media_catg_a0004]] 与业务键 [[busi_key]]。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 lookupCustMedia 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 特定分类按操作人过滤
content: 查询影像时，对 A0004/A0011/A0012 分类的文件，只保留 userBusiKey 等于当前管理员 id 的记录。
impact: 确保授权书/操作人证件只返回当前操作人的影像
field_targets: [media_file.catg_id, media_file.user_busi_key]
evidence: PlatFormMediaApplication.java:lookupCustMedia
```

关联：[[media_file]]、[[catg_id]]、[[busi_key]]、[[admin_person]]、[[media_catg_a0004]]。