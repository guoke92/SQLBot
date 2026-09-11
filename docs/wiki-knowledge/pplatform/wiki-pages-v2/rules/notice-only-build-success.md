---
type: rule
title: 新增子级仅认证成功才发待办
page_key: rules/notice-only-build-success
domain: 企业集团关系
status: draft
aliases: [待办发送范围, sendCustGroupRelNotice]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupRelApplication.java:addExistSubCustGroupRel
  - code_path:CustGroupRelApplication.java:processChildCompany
contract_version: "0.1"
---

待办发送范围规则：仅对建档成功（BUILD_SUCCESS）的企业发送集团关系待办，导入场景同理。前置口径见 [[calibers/company-build-success]]，状态语义见 [[processes/cust-group-rel-status-state]]。

## 需求背景

建档未完成的企业尚未接入系统，此时推送待办既无人处理也会产生悬挂任务，因此以待办发送范围收敛为「建档成功节点」。

## 版本演进

v0 契约按现状固化；导入链路通过把 BUILD_SUCCESS 节点加入 needSends 复用同一规则。

## 规则锚点

```ground:rule
name: 新增子级仅认证成功才发待办
content: addExistSubCustGroupRel 中仅当企业 cust_build_status=BUILD_SUCCESS 才 sendCustGroupRelNotice；导入场景同样只对 BUILD_SUCCESS 的节点加入 needSends。
impact: 待办发送范围
field_targets:
  - cust_company_info.cust_build_status
  - cust_group_rel.status
evidence: code_path:CustGroupRelApplication.java:addExistSubCustGroupRel / processChildCompany
```