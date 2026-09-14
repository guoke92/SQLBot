---
type: rule
title: 角色为覆盖式新增
page_key: role-overwrite-add
domain: 客户角色与端口
status: draft
aliases:
  - addRoleInfo 覆盖式重建
oid: 1
scope:
  databases:
    - db_dist
sources:
  - code_path:CustRoleApplication.java#addRoleInfo
contract_version: "0.1"
belong: rules
---

# 角色为覆盖式新增

addRoleInfo 是**覆盖式**的：先按 ref_cust_company_info 删除该企业已有角色，再按传入 roleType 的 JSON 数组逐项 saveBatch 重建。新记录 code 由 uuid 生成，db_tenant_code 取企业租户。

影响：同一企业重复调用会整体重建角色集合，不做增量合并；任何依赖「原有角色记录 id/编码稳定」的逻辑都会失效。重建还会重置 status（回到 DB 默认 ADD 的新增态语义），因此调用前需确认是否会打断正在生效的角色。

## 需求背景

需求文档以「提交企业角色信息」描述该动作，未强调其覆盖语义；实现侧是「先删后建」，与增量 upsert 的直觉不同，需在对接文档中显式说明。

## 版本演进

- 由可能的逐条增量维护收敛为先删后批量重建，简化了角色集合的一致性维护。

```ground:rule
name: 角色为覆盖式新增
content: addRoleInfo 先按 ref_cust_company_info 删除该企业已有角色，再按传入 roleType 的 JSON 数组逐项 saveBatch 重建；新记录 code 由 uuid 生成，db_tenant_code 取企业租户。
impact: 同一企业重复调用会整体重建角色集合，不做增量合并
field_targets:
  - cust_role_info.role_type
  - cust_role_info.code
  - cust_role_info.db_tenant_code
evidence: code_path:CustRoleApplication.java#addRoleInfo
```

## 关联

- [[tables/cust_role_info]]
- [[concepts/company-role]]
- [[rules/rejected-cust-clear-role]]