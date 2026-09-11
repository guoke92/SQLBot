---
type: rule
title: 已生效成员单位不可重复操作
page_key: rules/effective-member-no-op
domain: 企业集团关系
status: draft
aliases: [checkCustGroup, 成员单位准入校验]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupLicenseApplication.java:checkCustGroup
contract_version: "0.1"
---

成员单位协议操作的准入规则：已生效记录、根节点、未认证成功企业三类情形均被拒。口径见 [[calibers/effective-group-member]]、[[calibers/group-root-node]]、[[calibers/company-build-success]]。

## 需求背景

重复签署会破坏生效时间与协议一致性，根节点不具备成员身份，未建档完成的企业无承接能力，因此三类场景需要在操作入口一并拦截。

## 版本演进

v0 契约按现状固化；AGW 端登录企业在非 BUILD_SUCCESS 时同样纳入拦截。

## 规则锚点

```ground:rule
name: 已生效成员单位不可重复操作
content: checkCustGroup：groupId 对应记录 status=EFFECTIVE 时抛“集团成员单位已生效，不支持该操作”；root_flag=Y 时抛“集团公司不支持该操作”；非 AGW 端登录企业 cust_build_status 非 BUILD_SUCCESS 时抛“企业未认证成功，不能执行当前操作”。
impact: 成员单位协议签署准入
field_targets:
  - cust_group_rel.status
  - cust_group_rel.root_flag
  - cust_company_info.cust_build_status
evidence: code_path:CustGroupLicenseApplication.java:checkCustGroup
```