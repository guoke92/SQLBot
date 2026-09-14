---
type: rule
title: 客户影像查询前置校验
page_key: cust_media_precheck
domain: 文件/附件/媒体
status: draft
aliases: [影像查询前置校验]
oid: 1
scope:
  databases: [unknown]
sources: ["code:PlatFormMediaApplication.java:listCustMediaFile"]
contract_version: "0.1"
belong: rules
---
查询客户影像（[[media]]）时必须传 companyType；随后按 pplatCustId 查企业，再查管理员联系人与角色记录，任一不存在即抛异常。该规则以 [[cust_company_info]]、[[cust_person_info]]、[[cust_role_info]] 三张表为判定依据。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 listCustMediaFile 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 客户影像查询前置校验
content: 查询客户影像时必须传 companyType；根据 pplatCustId 查企业，再查管理员联系人和角色记录，任一不存在抛异常。
impact: 阻止无角色或管理员的企业查询影像
field_targets: [cust_company_info.id, cust_person_info.user_type, cust_role_info.role_type]
evidence: PlatFormMediaApplication.java:listCustMediaFile
```

关联：[[media]]、[[admin_person]]、[[cust_company_info]]、[[cust_person_info]]、[[cust_role_info]]。