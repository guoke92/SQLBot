---
type: rule
title: 资质文件必传校验
page_key: qualification-file-required-check
domain: 企业建档与准入
status: published
aliases: [资质文件校验]
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 资质文件必传校验

本规则要求必须上传授权书、法人身份证正反面、联系人身份证正反面、营业执照，缺少任一文件抛出异常。

## 需求背景

企业建档时影像文件作为资质证明材料，必须完整上传。校验在代码入口执行。

## 版本演进

证据来自代码路径 `CustAccessApplication.validateMedia`。

```ground:rule
name: 资质文件必传校验
content: 必须上传授权书、法人身份证正反面、联系人身份证正反面、营业执照
impact: 缺少任一文件抛出异常
field_targets:
  - 影像文件类型
evidence: "code_path:CustAccessApplication.validateMedia"
```

相关表：[[cust_company_info]]