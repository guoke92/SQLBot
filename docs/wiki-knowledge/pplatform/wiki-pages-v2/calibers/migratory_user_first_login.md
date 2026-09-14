---
type: caliber
title: 存量迁移用户首登提示口径
page_key: migratory_user_first_login
domain: 租户迁移
status: draft
aliases: [首登弹提示口径, is_login=N 口径]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:CustMigratoryService.java#loginAfterEjectMsg"
  - "code:CustMigratoryController.java#isEjectMsg"
  - "db:migratory_user_record"
contract_version: "0.1"
belong: calibers
---

判定"该用户是否应弹升级提示"的口径：记录存在且 `is_login='N'` 才弹，弹完立即置 Y。数据分布上未登录 5228 条、已登录 1433 条，说明多数迁移用户尚未完成首登。状态流转见 [[migratory_user_login_prompt]]。

```ground:caliber
name: 存量迁移用户首登提示口径
predicate: "migratory_user_record.is_login = 'N'"
scope: "登录后 isEjectMsg 判定：记录存在且未登录才弹『平台已升级…』，弹后置 Y"
evidence: "code:CustMigratoryService.java#loginAfterEjectMsg + db(N:5228/Y:1433) + reqdoc:migratory-first-login-eject-msg"
```

## 需求背景

存量用户首次登录（当前迁移批次内）弹出『【贴牌名称】平台已升级，新增【产品中心】，期待为您提供更好的服务』，一个用户仅弹一次。贴牌名称取自租户配置（见 [[贴牌]]），文案中的名称缺失时的兜底行为需求未明确。

## 版本演进

由"每次登录都提示"演进为"仅弹一次"，判定依据由内存/前端标记改为服务端 `is_login` 持久列。