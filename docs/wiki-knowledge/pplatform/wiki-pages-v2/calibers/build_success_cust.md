---
type: caliber
title: 建档成功企业
page_key: caliber.build_success_cust
domain: 数据权限与组织
status: draft
aliases: [建档成功, BUILD_SUCCESS 企业]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

「建档成功企业」是组织域最重要的过滤口径：组织根节点初始化、机构管理员绑定定时任务、企业查询前置校验三处都要求企业同时满足建档成功与启用。它依赖 [[processes/cust_build_status_fsm]] 到达 BUILD_SUCCESS，并叠加 [[tables/cust_company_info]].enable 维度，因此不能只判状态字段。此处引用的档案成功状态也决定 [[processes/cust_group_rel_status_fsm]] 中集团关系能否直接生效。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张。

## 版本演进

v0：依据 code 证据（CustSysOrgApplication）成文。

```ground:caliber
name: 建档成功企业
predicate: "cust_company_info.cust_build_status = 'BUILD_SUCCESS' AND cust_company_info.enable = 'Y'"
scope: 组织根节点初始化、机构管理员绑定定时任务、企业查询前置校验
evidence: code_path:CustSysOrgApplication.java#listBuildSuccessCusts / #checkCustBuildStatus
```