---
type: caliber
title: CA 证书参数错误码映射
page_key: ca_cert_error_code_mapping
belong: calibers
domain: 支付宝蚂蚁档案与清算
status: published
aliases: []
oid: 1
sources: ["semantic_analysis"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该口径定义了 CA 证书相关错误消息前缀到具体业务错误码的显式映射，包括参数无效、初始化参数缺失、信息不完整、实名方法不匹配/不支持、意图不支持等场景。

## 需求背景

CA 证书错误种类多，需标准化为数字错误码，便于系统间交互。

## 版本演进

初始版本，暂无变更。

```ground:caliber
name: CA 证书参数错误码映射
predicate: message STARTS_WITH 'CA_CERT_PARAM_INVALID' -> 201110；'CA_CERT_INIT_PARAM_MISSING' -> 201111；'CA_CERT_INFO_INCOMPLETE' -> 201112；'CA_CERT_REALNAME_METHOD_MISMATCH'/'CA_CERT_REALNAME_UNSUPPORTED' -> 201113；'CA_CERT_INTENT_UNSUPPORTED' -> 201114
scope: AntArchiveErrorMapper.mapCaOrBusinessCode
evidence: code_path:AntArchiveErrorMapper.mapCaOrBusinessCode
```

[[tables/AlipayAntArchiveResp]] [[rules/CA 证书错误码显式映射]]