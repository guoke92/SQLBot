---
type: rule
title: CA失效回写ca_register_status=N
page_key: rule/ca_invalidate_writeback
domain: CA证书认证
status: draft
aliases: [resetCaRegisterStatusToN, CA 回写失效]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CaCertificationPreCheckApplication.java:resetCaRegisterStatusToN"]
contract_version: "0.1"
---

规则要求：当签章中台证书状态归一化为 CANCELLED/EXPIRED/FAIL，或登记企业名与库中名称不一致时，将 cust_company_info.ca_register_status 置为 N。影响是前端据此引导用户重新发起 CA 开通。

这条回写把「外部证书状态」翻译成「企业侧开通标识」，是本主题里唯一把签章中台状态向企业主数据反向传播的规则。它使得 [[calibers/latest_success_report]] 的结果与企业侧标识可能短暂背离：历史成功行仍在，但企业已被判为未开通，直到重新认证成功。名称不一致的分支还衔接在线盖章的升级授权书流程（[[rules/upgrade_auth_online_seal]]）。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。三个失效状态取值、名称不一致条件与目标字段均来自代码路径证据。

## 版本演进

暂无文档化的版本演进证据。需要注意的是 ca_register_status 同时被多条规则写入：本规则置 N，简易认证规则也会校正其取值（[[rules/simple_auth_force_no_ca]]），存量打包口径则以 ca_register_status='Y' 为筛选条件（[[calibers/legacy_package_company_scope]]）。

```ground:rule
name: CA失效回写ca_register_status=N
content: 签章中台证书状态归一化为CANCELLED/EXPIRED/FAIL或登记企业名与库中名称不一致时，将cust_company_info.ca_register_status置为N。
impact: 前端引导用户重新发起CA开通
field_targets:
  - cust_company_info.ca_register_status
evidence: "code_path:CaCertificationPreCheckApplication.java:resetCaRegisterStatusToN"
```

相关页面：[[calibers/latest_success_report]]、[[rules/upgrade_auth_online_seal]]、[[rules/simple_auth_force_no_ca]]。