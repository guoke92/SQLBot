---
type: rule
title: 集团成员单位关联唯一性
page_key: group-rel-uniqueness
domain: 企业集团关系
status: draft
aliases: [成员单位重复校验, 已存在]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupRelApplication.java:addExistSubCustGroupRel
  - code_path:CustGroupRelApplication.java:addNewSubCustGroupRel
contract_version: "0.1"
belong: rules
---

新增成员单位关系时的唯一性规则：以企业 + 租户 + 父/根企业 + 角色为组合键计数，命中即阻断。涉及表见 [[tables/cust_group_rel]]，角色字段语义见 [[concepts/cust-type]]。

## 需求背景

同一企业在同一集团树下承担同一角色只能有一条关系记录，否则生效状态、待办与统计都会重复。组合键中包含 cust_type，意味着同一企业可在不同角色下被重复关联。

## 版本演进

v0 契约按现状固化，新增（addNewSubCustGroupRel）与既有企业关联（addExistSubCustGroupRel）共用同一唯一性判定。

## 规则锚点

```ground:rule
name: 集团成员单位关联唯一性
content: 按 cust_id + db_tenant_code + parent_cust_id + root_cust_id + cust_type 计数，>=1 即抛“该企业{名称} - {角色}已存在”。
impact: 重复关联拦截
field_targets:
  - cust_group_rel.cust_id
  - cust_group_rel.cust_type
  - cust_group_rel.parent_cust_id
  - cust_group_rel.root_cust_id
evidence: code_path:CustGroupRelApplication.java:addExistSubCustGroupRel / addNewSubCustGroupRel
```