---
type: rule
title: CA 证书错误码显式映射
page_key: ca_cert_error_code_explicit_mapping
belong: rules
domain: 支付宝蚂蚁档案与清算
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该规则将 CA 证书相关的多种错误前缀映射为具体数字错误码 201110～201114，并额外处理影像文件（201120）与协议告知（201121）错误。

## 需求背景

需要将下游多样化的 CA 证书错误标准化，便于系统统一处理和展现。

## 版本演进

初始版本，暂无变更。

```ground:rule
name: CA 证书错误码显式映射
content: AntArchiveErrorMapper.mapCaOrBusinessCode 将 CA_CERT_PARAM_INVALID 映射为 201110，CA_CERT_INIT_PARAM_MISSING 映射为 201111，CA_CERT_INFO_INCOMPLETE 映射为 201112，CA_CERT_REALNAME_METHOD_MISMATCH/CA_CERT_REALNAME_UNSUPPORTED 映射为 201113，CA_CERT_INTENT_UNSUPPORTED 映射为 201114，包含 sftp/SFTP/影像文件 映射为 201120，包含 协议告知与影像/notifyAgreement 映射为 201121
impact: 标准化 CA 证书相关业务错误码
field_targets: ["code"]
evidence: code_path:AntArchiveErrorMapper.mapCaOrBusinessCode
```

[[tables/AlipayAntArchiveResp]] [[ca_cert_error_code_mapping]] [[image_file_error_code]] [[agreement_notify_error_code]]