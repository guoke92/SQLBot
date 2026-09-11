---
type: rule
title: 多角色建档影像复制
page_key: rules/multi-role-media-copy
domain: 文件/附件/媒体
status: draft
aliases: [uploadMultiRole, 多角色影像复制, companyTypes 复制影像]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code_path:CustMediaFacade.java:uploadMultiRole
contract_version: "0.1"
---

# 多角色建档影像复制

## 业务定位

互通产品场景下，运营中台回传的是单角色，而产融目标系统可能存在多角色。为此系统对 `A0004`/`A0011`/`A0012`（[[calibers/auth-media-a0004]]、[[calibers/operator-auth-cert-media-a0011-a0012]]）按 `extText.companyTypes` 的剩余角色重传影像。

结果与影响：同一份授权书/操作人影像会按角色复制多份。做影像去重统计时，不能假设“一份授权书只有一条记录”，应以角色维度聚合。

```ground:rule
name: 多角色建档影像复制
content: 互通产品下运营中台回传单角色，产融目标系统可能多角色，对 A0004/A0011/A0012 按 extText.companyTypes 剩余角色重传影像。
impact: 同一授权书/操作人影像会按角色复制多份。
field_targets:
  - MediaFile.catgId
  - MediaFile.companyType
evidence: "code_path:CustMediaFacade.java:uploadMultiRole"
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

## 版本演进

- v0（本页）：规则来自 [代码] 证据；`companyType` 字段未出现在本次字段语义清单中，其取值集合待补充。