---
type: caliber
title: 上送 data 字段长度上限
page_key: caliber/submit_data_length_limit
domain: 微信生态/小程序/扫脸
status: draft
aliases: [data长度上限, 上送裁剪口径]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
---

# 上送 data 字段长度上限

上送前对 `data` 字段的长度约束口径：单字段不超过 1000，仅对 authPersonPoliceTwo / authEnterpriseThree / authEnterpriseFour / checkCode / h5Face 五处裁剪。

## 需求背景

中台对报文体积有限制，h5Face 的原始 requestData / data 可能较大，需按 JSON 叶子长度从长到短剔除，最后硬截断兜底。

## 版本演进

v0.1 记录长度上限与裁剪范围。

```ground:caliber
name: 上送 data 字段长度上限
predicate: "LENGTH(authRealNameJson.*.data / intentJson.*.data) <= 1000"
scope: "仅裁剪 authPersonPoliceTwo / authEnterpriseThree / authEnterpriseFour / checkCode / h5Face 五处 data，超长按 JSON 叶子从长到短剔除，最后硬截断兜底。"
evidence: code_path:CaCertificationInfoAppServiceImpl.java#truncateOversizedDataFieldsInSubmitPayload
```

相关：[[ca_certification_info]]、[[h5_face_persist_soft_fail]]、[[ca_submit_completeness_check]]。