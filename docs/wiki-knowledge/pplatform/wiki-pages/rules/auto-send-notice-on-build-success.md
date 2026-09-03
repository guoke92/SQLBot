---
type: rule
title: "添加新子级关系时，如果企业认证成功则立即发送待办"
page_key: auto-send-notice-on-build-success
domain: 集团与关联关系
status: published
aliases: []
oid: 1
sources: ["语义分析"]
contract_version: "0.1"
field_targets: [cust_company_info.cust_build_status]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

在企业添加为新子级关系时，若企业已认证成功（`BUILD_SUCCESS`），自动触发协议签署待办流程。

## 需求背景

- 在 `addExistSubCustGroupRel` 和 `addNewSubCustGroupRel` 中，如果企业 `cust_build_status` 为 `BUILD_SUCCESS`，则调用 `sendCustGroupRelNotice` 发送待办。

## 版本演进

- 暂无变更。

```ground:rule
name: 添加新子级关系时，如果企业认证成功则立即发送待办
content: 在 addExistSubCustGroupRel 和 addNewSubCustGroupRel 中，如果企业 cust_build_status 为 BUILD_SUCCESS，则调用 sendCustGroupRelNotice 发送待办
impact: 自动触发协议签署流程
field_targets:
  - cust_company_info.cust_build_status
evidence: code_path:CustGroupRelApplication.addExistSubCustGroupRel / addNewSubCustGroupRel
```

相关：[[cust_company_info]] [[build-success]] [[build-success-company]]