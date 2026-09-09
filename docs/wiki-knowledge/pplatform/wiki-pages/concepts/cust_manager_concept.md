---
type: concept
title: "客户管理员"
page_key: cust_manager_concept
belong: concepts
domain: "授权协议与电子授权"
status: published
aliases: ["企业管理员", "管理员"]
oid: 1

sources: ["db:cust_person_info", "code:CustAuthAgreementDomainService", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "cust_person_info.user_type='admin'"
field_targets: []
adjudication: "boundary"
also_confused_with: ["经办人(operator)", "AMS 经办人"]
coverage_note: "用户角色"
scope:
  databases: [lowcode_pplatform]
---

“客户管理员”指企业内拥有管理员角色的用户，有签署 [[授权书]] 的义务。与经办人不同，经办人一般无需签署授权书。

## 需求背景

企业管理员变更时，会触发 [[授权书认证状态机]] 中禁用旧管理员记录及创建新管理员记录的操作。[[存量迁移企业需补签平台授权书口径]] 亦针对管理员判断补签义务。

## 版本演进

暂无。

相关：[[cust_person_info]]
