---
type: rule
title: "旧状态处理器已废弃"
page_key: legacy_status_processor_deprecated
domain: "customer-onboarding"
status: draft
aliases:
  - "CustStatusCommitProcessor 废弃"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustStatusCommitProcessor.java:类注解"
contract_version: "0.1"
belong: rules
---

`CustStatusCommitProcessor` 已标注 `@Deprecated`，且其 `@DubboService` 注解被注释掉，变更消息等逻辑已由新处理器替代。因此以该类为证据的状态流转描述只能作为旁证，正式口径应以新链路为准，见 [[rules/workflow_callback_routing]]。

## 需求背景

需求文档描述的状态流转与旧实现一致，但当前运行时生效的是新链路；引用旧类结论时必须在文档中声明其旁证地位。

## 版本演进

- 从「唯一状态处理器」到「废弃旁证」：本仓库中多个页面的状态机证据源自该类，后续若新链路补齐同类分支，应把证据迁移到新处理器；迁移影响 [[processes/company_build_status_machine]]、[[processes/workflow_check_status_machine]]、[[processes/change_record_check_machine]] 三个状态机的证据可信度。

```ground:rule
name: "旧状态处理器已废弃"
content: "CustStatusCommitProcessor 标注 @Deprecated 且 @DubboService 被注释，变更消息逻辑已被新处理器替代。"
impact: "相关状态流转仅供参考，需以新链路为准"
field_targets:
  - "cust_change_record.status"
evidence: "code_path:CustStatusCommitProcessor.java:类注解"
```

相关：[[processes/change_record_check_machine]]、[[rules/workflow_callback_routing]]。