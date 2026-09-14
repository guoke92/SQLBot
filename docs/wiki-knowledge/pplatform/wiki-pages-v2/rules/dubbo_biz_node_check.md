---
type: rule
title: Dubbo业务节点校验规则
page_key: dubbo_biz_node_check
domain: CA证书收费
status: draft
aliases:
  - dualCheck
  - 业务节点校验
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeBizNodeCheckApplication.java
contract_version: "0.1"
belong: rules
---

统码维度若不存在**生效主数据的**供应商／核企角色，Dubbo `dualCheck` 直接放行；只有存在收费角色才进入缴费校验。该规则决定了讯易链签章前的拦截只针对收费对象，挂钩的字段为 `cust_company_info.certification_no` 与 `cust_company_info.cust_company_type`（该表未在本主题字段语义清单中展开，见页末 REVIEW）。

## 需求背景

签章链路被多个业务复用，若不先判断「该统码下是否存在收费角色」，会对非收费对象产生误拦截；因此把角色存在性作为放行条件。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: Dubbo业务节点校验规则
content: 统码维度若不存在生效主数据的供应商/核企角色，Dubbo dualCheck 直接放行；存在收费角色才进入缴费校验
impact: 讯易链签章前拦截只针对收费对象
field_targets:
  - cust_company_info.certification_no
  - cust_company_info.cust_company_type
evidence: CaFeeBizNodeCheckApplication.check
```