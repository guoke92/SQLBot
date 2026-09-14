---
type: rule
title: 规则：逻辑有效标记过滤（enable='Y'）
page_key: enable_validity_filter
domain: 租户项目
status: draft
aliases: [逻辑有效标记过滤, enable 过滤规则]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - db:tenant_product
  - code:exportProjectInfo
  - code:queryRelatedCompanies
contract_version: "0.1"
belong: rules
---

规定凡涉及 [[tenant_product]]、[[tenant_project]]、[[cust_project_rel]] 的查询与导出，必须显式带 `enable='Y'`；删除一律走逻辑删除。该规则由三条独立证据归纳而成（见下方锚点与各表口径 [[valid_tenant_product]]、[[valid_project]]、[[valid_cust_project_rel]]）。

## 需求背景
语义分析未附带需求文档锚点，本节依据代码证据归纳：多张表统一使用 `enable` 作为逻辑有效标记，避免物理删除破坏关联关系（项目-产品-企业）。

## 版本演进
语义分析未记录该规则的版本演进；[[tenant_product]] 的 `enable` 在 DB 实测全为 Y。

```ground:rule
name: 逻辑有效标记过滤规则
statement: 查询与导出涉及 tenant_product / tenant_project / cust_project_rel 时必须附加 enable = 'Y'；删除采用逻辑删除，不物理删除。
predicate: "enable = 'Y'"
scope: tenant_product, tenant_project, cust_project_rel
evidence: "code:exportProjectInfo/updateProjectData 按 enable='Y'；code:queryRelatedCompanies 按 enable='Y'；db:tenant_product.enable 全为 Y"
```

---REVIEW: rule | 逻辑有效标记过滤---
语义分析在 term_bridges 处被截断，规则（rules）段落未随分析结果提供；本页是依据 caliber 与字段语义证据归纳出的唯一一条规则，其余规则待补充分析后回填。
---END REVIEW---