---
type: rule
title: 企微导入按 sp_no 匹配既有记录
page_key: rule/wechat-import-match-by-sp-no
domain: 微企链立项与项目审批
status: draft
aliases:
  - 企微导入只更新不新增
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - db:wechat_project_approval_apply
contract_version: "0.1"
---

企微同步写入立项申请时，匹配键只有一个：`sp_no`。匹配到既有记录就更新，匹配不到不会新增。因此企微侧产生的数据能否进入本系统，取决于对应的 `sp_no` 记录是否已经存在。

这条规则解释了为什么 `sp_no` 是唯一索引，也解释了「企微明明审批通过了但平台查不到」的一类问题的排查方向。相关桥接关系见 [[concepts/sp-no-bridge]]，字段语义见 [[tables/wechat_project_approval_apply]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 未发现该规则的历史变更记录。

```ground:rule
rule: 企微导入按 sp_no 匹配既有记录
subject: wechat_project_approval_apply.sp_no
evidence: db
source_meaning: 企微审批编号，表唯一索引（UNI）；企微导入仅按 sp_no 匹配既有记录（只更新不新增），项目上线审批侧按它回写 tenant_project.wechat_audit_no
```