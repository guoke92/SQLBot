---
type: process
title: 迁移存量用户登录提示状态机
page_key: migratory_user_login_prompt
domain: 租户迁移
status: draft
aliases: [首登弹提示状态机, is_login 状态机]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:CustMigratoryService.java#loginAfterEjectMsg"
  - "code:CustMigratoryController.java#isEjectMsg"
  - "code:PlatFormMigratoryApplication.java#migratoryCust"
  - "db:migratory_user_record"
contract_version: "0.1"
belong: processes
---

状态机只有两个状态，但入口与出口都很硬：迁移落库时一定是 N，登录后的 `isEjectMsg` 判定命中才翻转为 Y，翻转后同一用户不再弹。它同时是企业侧与用户侧的"迁移已完成提示"开关，见口径 [[migratory_user_first_login]]、规则 [[migratory_user_record_insert]]。

```ground:process
name: 迁移存量用户登录提示状态
field: migratory_user_record.is_login
states:
  - value: N
    label: "迁移存量用户、尚未登录（可弹升级提示）"
    source: db_dist
  - value: Y
    label: "已登录过（不再弹提示）"
    source: db_dist
transitions:
  - from: N
    event: "登录后调用 /cust-web/migratory/isEjectMsg（isExist 且 hasNotLogin）"
    to: Y
    evidence: "code_path:CustMigratoryService.java#loginAfterEjectMsg"
  - from: 新增
    event: '迁移落库时为每个迁移人员创建记录并写 is_login="N"'
    to: N
    evidence: "code_path:PlatFormMigratoryApplication.java#migratoryCust"
```

## 需求背景

存量用户首次登录（当前迁移批次内）弹出『【贴牌名称】平台已升级，新增【产品中心】，期待为您提供更好的服务』，一个用户仅弹一次。因此状态必须由服务端持久化，不能依赖前端本地标记；记录不存在视为非迁移用户，不弹提示。

## 版本演进

`is_login` 初值硬编码 `"N"`；查询条件由单 user_id 演进为 `user_id + db_tenant_code`（见 [[tenant_code]]）。记录不存在时不补建（不回溯弹窗）。