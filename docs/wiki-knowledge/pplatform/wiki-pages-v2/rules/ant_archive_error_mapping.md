---
type: rule
title: 蚂蚁建档错误码映射
page_key: ant_archive_error_mapping
domain: 外部渠道与银行对接
status: draft
aliases:
  - AntArchiveErrorMapper
  - 201110~201121
oid: 1
scope:
  databases:
    - cust
sources:
  - code:AntArchiveErrorMapper.toResponse
  - code:AntArchiveErrorMapper.mapCaOrBusinessCode
contract_version: "0.1"
belong: rules
---

蚂蚁渠道建档的异常按消息前缀映射为稳定错误码，便于渠道方定位问题。

## 需求背景
映射区间为 201110~201114（CA_CERT_PARAM_INVALID / INIT_PARAM_MISSING / INFO_INCOMPLETE / REALNAME_* / INTENT_UNSUPPORTED）、sftp 与影像类 201120、协议告知与影像类 201121；含「企业已建档」映射为 REG_EXIST_EXCEPTION，非业务异常统一 SERVER_BUSY。渠道侧语义见 [[channel]]，查重相关口径见 [[build_fail_reusable]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 蚂蚁建档错误码映射
content: 消息前缀 CA_CERT_PARAM_INVALID/INIT_PARAM_MISSING/INFO_INCOMPLETE/REALNAME_*/INTENT_UNSUPPORTED 依次映射 201110~201114，sftp/影像→201120，协议告知与影像→201121；含"企业已建档"→REG_EXIST_EXCEPTION；非业务异常→SERVER_BUSY
impact: 渠道方错误语义可读性
field_targets: []
evidence: "code:AntArchiveErrorMapper.toResponse / mapCaOrBusinessCode"
```