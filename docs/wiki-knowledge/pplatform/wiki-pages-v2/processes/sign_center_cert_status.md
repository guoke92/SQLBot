---
type: process
title: 签章中台证书状态归一（外部态，非落库字段）
page_key: sign_center_cert_status
domain: CA证书认证
status: draft
aliases: [certStatus, rawCertStatus, 中台证书状态]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationPreCheckApplication.java
contract_version: "0.1"
belong: processes
---

签章中台返回的原始证书态（SUCCESS / NEW_APPLY / INVALID / TIME_OUT 等）由 mapSignCenterStatus 归一为 NORMAL / APPLYING / CANCELLED / EXPIRED / FAIL / UNKNOWN 六类。这是一个**归一化视图**，不落 ca_certification_info 的列：它的用途是驱动 [[ca_register_status]] 的回写（CANCELLED/EXPIRED/FAIL 触发置 N）以及 [[need_register_ca_judgement|需开通 CFCA 判定口径]] 的失效判断。

## 需求背景

预检链路把"未注册记录"也按失效处理，因此 CANCELLED 的 label 同时覆盖注销/作废与查无记录两种情况；UNKNOWN 表示查询失败，属于需要人工/重试的分支，不应被当作有效态。该归一结果与本地上送态 [[ca_submit_status]] 不可互换，详见 [[cert_status]]。

## 版本演进

- v0：首次记录归一集合。原始态到归一态的映射表尚未逐值展开，纳入后续版本补充。

```ground:process
name: 签章中台证书状态（外部态归一化，非落库字段）
field: cfca_sign_center.cert_status
states:
  - value: NORMAL
    label: 正常
    source: code_const
  - value: APPLYING
    label: 申请中
    source: code_const
  - value: CANCELLED
    label: 注销/作废（含未注册记录按失效处理）
    source: code_const
  - value: EXPIRED
    label: 到期失效
    source: code_const
  - value: FAIL
    label: 申请失败
    source: code_const
  - value: UNKNOWN
    label: 未知/查询失败
    source: code_const
transitions: []
note: 由 mapSignCenterStatus 把中台 SUCCESS/NEW_APPLY/INVALID/TIME_OUT 等归一到上述集合（CaCertificationPreCheckApplication），不落 ca_certification_info 列
```

关联页面：[[ca_register_status]]、[[cert_status]]、[[ca_submit_status]]、[[cust_company_info]]。