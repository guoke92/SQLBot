---
type: rule
title: client_type=AGW 跳过机构租户过滤
page_key: org_agw_skip_tenant_filter
domain: 数据权限与组织
status: draft
aliases: [AGW 跳过租户过滤, org_manage.client_type]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
belong: rules
---

[[tables/org_manage]] 的 client_type 用于区分端来源；OrgFacade 中以 clientType=='AGW' 判断是否跳过租户过滤。即来自 AGW 端调用时，机构数据不走租户维度裁剪，这是跨租户可见性的一个显式例外，与 [[concepts/tenant_code_layers]] 的租户层次直接相关。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本规则由 org_manage.client_type 字段语义得出。

## 版本演进

v0：依据 code 证据成文。

```ground:rule
name: AGW 端跳过租户过滤
statement: clientType=='AGW' 时跳过机构数据的租户过滤
condition: OrgFacade 收到 client_type=AGW 的调用
action: 不追加租户过滤条件
evidence: code_path:OrgFacade（clientType=='AGW' 判断）
```