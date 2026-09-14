---
type: caliber
title: 管理员联系人
page_key: admin_person
domain: 文件/附件/媒体
status: draft
aliases: [user_type=admin]
oid: 1
scope:
  databases: [unknown]
sources: ["code:PlatFormMediaApplication.java:personInfoService.getOne"]
contract_version: "0.1"
belong: calibers
---
判定企业下管理员联系人的口径，是影像查询与按操作人过滤的前置条件，见 [[cust_media_precheck]]、[[catg_operator_filter]]。

## 需求背景
本期语义分析未提供需求文档主张；口径来自代码取值证据。

## 版本演进
v0 初版：口径来自 personInfoService.getOne 查询条件证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 管理员联系人
predicate: cust_person_info.user_type = 'accountAdmin'
scope: 客户联系人
evidence: code
```

关联：[[cust_person_info]]、[[UserTypeEnum]]、[[cust_media_precheck]]。