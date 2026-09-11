---
type: process
title: CA认证提交状态机
page_key: process/ca_certification_submit_status
domain: CA证书认证
status: draft
aliases: [submit_status 状态流转, CA上送签章中台状态]
oid: 1
scope:
  databases: [unknown]
sources: [code]
contract_version: "0.1"
---

本状态机描述 ca_certification_info 行在「上送签章中台」这条链路上的生命周期。状态字段为 ca_certification_info.submit_status，三个取值 PENDING / SUCCESS / FAIL 均为代码枚举。

正常路径是：认证行以 PENDING 创建（幂等口径见 [[calibers/ca_row_idempotent_key]]），由 submitToSignCenter 上送签章中台；上送成功置 SUCCESS，上送失败置 FAIL。已经进入 FAIL 的行允许再次上送，成功即回到 SUCCESS；也存在不经上送、由运营侧手动标记失败进入 FAIL 的入口（markFailed）。

上送前的准入条件不在本状态机内表达，而由完整性校验规则约束（[[rules/submit_sign_center_completeness]]），超长 data 字段会在打包上送报文时被截断（[[rules/data_field_truncate]]）。SUCCESS 与 enable=Y 共同构成下游取数口径（[[calibers/latest_success_report]]）。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。三态取值与四条流转的判定点均来自代码枚举与代码路径证据。

## 版本演进

暂无文档化的版本演进证据。当前可见的流转入口集中在 CaCertificationInfoAppServiceImpl 的 submitToSignCenter 与 markFailed 两个方法，尚无其他状态取值出现在分析证据中。

```ground:process
name: CA认证提交状态机
field: ca_certification_info.submit_status
states:
  - value: PENDING
    label: 待提交
    source: code_enum
  - value: SUCCESS
    label: 提交成功
    source: code_enum
  - value: FAIL
    label: 提交失败
    source: code_enum
transitions:
  - from: PENDING
    event: 提交签章中台成功
    to: SUCCESS
    evidence: "code_path:CaCertificationInfoAppServiceImpl.java:submitToSignCenter"
  - from: PENDING
    event: 提交签章中台失败
    to: FAIL
    evidence: "code_path:CaCertificationInfoAppServiceImpl.java:submitToSignCenter"
  - from: PENDING
    event: 手动标记失败
    to: FAIL
    evidence: "code_path:CaCertificationInfoAppServiceImpl.java:markFailed"
  - from: FAIL
    event: 重新提交签章中台成功
    to: SUCCESS
    evidence: "code_path:CaCertificationInfoAppServiceImpl.java:submitToSignCenter"
```

相关页面：[[tables/ca_certification_info]]、[[rules/submit_sign_center_completeness]]、[[concepts/ca]]。