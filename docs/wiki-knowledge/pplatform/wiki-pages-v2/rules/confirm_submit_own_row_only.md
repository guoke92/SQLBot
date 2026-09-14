---
type: rule
title: 协议确认只上送本企业行
page_key: confirm_submit_own_row_only
domain: CA证书认证
status: draft
aliases: [confirm 上送范围, 只上送 N 行]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationConfirmApplication.java
  - db:ca_certification_info
contract_version: "0.1"
belong: rules
---

CaCertificationConfirmApplication.confirm 中总公司行 submitOrThrow 被注释，仅上送 head_company_data='N' 主行；与类 Javadoc「先总后分」表述不一致。

**影响**：分公司场景总公司行不会在协议确认阶段上送（仅运营推送链路 CaActivationApplication 并行上送 N/Y 两行）。因此"总公司行一直 PENDING"在协议确认入口下是预期现象，不是漏推。

## 需求背景

与 [[head_company_row|总公司主体行口径]]、[[operation_platform_source]] 联读可还原两条链路的上送范围差异。类 Javadoc 与本实现的不一致需后续确认是回退还是有意调整。

## 版本演进

- v0：首次记录被注释代码与文档表述的冲突。

```ground:rule
name: 协议确认只上送本企业行
content: CaCertificationConfirmApplication.confirm 中总公司行 submitOrThrow 被注释，仅上送 head_company_data='N' 主行；与类 Javadoc「先总后分」表述不一致
impact: 分公司场景总公司行不会在协议确认阶段上送（仅运营推送链路 CaActivationApplication 并行上送 N/Y 两行）
field_targets:
  - ca_certification_info.head_company_data
  - ca_certification_info.submit_status
evidence: "code_path:CaCertificationConfirmApplication.java#confirm（//submitOrThrow(ctx.headCertId...) 被注释）"
```

关联页面：[[head_company_row]]、[[head_company_data]]、[[operation_platform_source]]、[[ca_submit_status]]。