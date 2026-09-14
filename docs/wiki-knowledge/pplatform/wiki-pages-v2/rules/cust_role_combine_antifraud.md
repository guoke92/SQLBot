---
type: rule
title: 企业角色组合反欺诈
page_key: cust_role_combine_antifraud
domain: 平台产品配置
status: draft
aliases: [checkCustRoleCombine, 2.3 角色组合校验]
oid: 1
scope:
  databases: [platform]
sources:
  - code:TenantProductApplication.java#checkCustRoleCombine
  - code:TenantProductApplication.java#checkProjectProductByCustType
  - reqdoc:2.3
contract_version: "0.1"
belong: rules
---

同一企业在同一产品下聚合其 `companyType` 集合，仅当角色数 ≥ 2 且该集合不在 [[platform_product]] 的 `cust_role_combine` 允许集合内时抛 `BaseException(系统暂不支持该角色组合)`。该规则阻断「一企业一产品扮演多角色」的欺诈路径，作用于企业加入项目与开通产品两个入口。

## 需求背景

需求文档 2.3「客户加入项目-角色组合校验」与实现一致（confirmed）：`checkCustRoleCombine` 聚合角色集合后读取 `cust_role_combine` 判定，`checkProjectProductByCustType` 做产品维度收敛。角色取值域见 [[company_type]]。

## 版本演进

- `cust_role_combine` 为文本字段，需解析为 `Set<Set<String>>` 后比较，属实现侧约定。



关联：[[platform_product]]、[[company_type]]、[[platform_operator_exemption]]