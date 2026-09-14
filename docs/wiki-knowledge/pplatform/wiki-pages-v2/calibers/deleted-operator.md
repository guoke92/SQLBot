---
type: caliber
title: 已离职运营人员口径
page_key: deleted-operator
domain: 项目报表/统计/上报
status: draft
aliases:
  - 离职人员判定口径
  - getDeletedOperatorIds
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectReportController.java
  - code:CustProjectController.java
contract_version: "0.1"
belong: calibers
---

# 已离职运营人员口径

运营对接人、查验对接人、风控对接人的离职校验统一取 `operation_user.deleted = 'Y' AND enable = 'Y'` 判定，作为提示文本与联系人有效性判断的唯一依据。它是 [[calibers/deleted-operator-hint-for-chanyong]] 的底层判定。

## 需求背景

对接人以 ID 或编码存放于关联表（见 [[tables/cust_project_rel]]），姓名需回查人员数据；离职状态同时出现在 deleted 与 enable 两列，业务上以二者同时成立为「已离职且记录有效」。项目台账与客户项目两处控制器都实现同一判定，保证口径一致。

## 版本演进

同一判定在 ProjectReportController 与 CustProjectController 中各自实现（getDeletedOperatorIds），属重复实现，未见抽取为公共服务的演进证据。

```ground:caliber
name: "已离职运营人员口径"
predicate: "operation_user.deleted = 'Y' AND operation_user.enable = 'Y'"
scope: "所有运营对接人/查验对接人/风控对接人的离职校验与提示文本生成"
evidence: "code_path:ProjectReportController.java:getDeletedOperatorIds + CustProjectController.java:getDeletedOperatorIds"
```