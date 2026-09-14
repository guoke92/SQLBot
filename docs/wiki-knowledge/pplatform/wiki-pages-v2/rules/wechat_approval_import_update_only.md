---
type: rule
title: 企微审批导入仅更新
page_key: wechat_approval_import_update_only
domain: 微企链立项与项目审批
status: draft
aliases: []
oid: 1
scope:
  databases:
    - wechat_project
sources:
  - code_path:WechatProjectApprovalApplication.java:validateAndImportData
contract_version: "0.1"
belong: rules
---

企微审批申请的导入校验与写入规则，决定了导入只做更新、不做新增，以及触发下游同步的条件。

```ground:rule
name: 企微审批导入仅更新
content: 导入企微审批申请时仅允许更新已存在的审批编号，不允许新增；为空不更新，"/"置空；审批编号重复、不存在、对接人不存在、字段超长等任一校验失败则整批不更新；更新后运营对接人A或风控对接人A至少一列有值则触发下游同步。
impact: 保证企微审批数据质量并触发下游项目配置同步。
field_targets:
  - wechat_project_approval_apply.sp_no
  - wechat_project_approval_apply.prd
  - wechat_project_approval_apply.op_contact
  - wechat_project_approval_apply.risk_control_contact
  - wechat_project_approval_apply.comment
evidence: code_path:WechatProjectApprovalApplication.java:validateAndImportData
```

## 需求背景

导入以 `sp_no` 为唯一匹配键，因此审批编号必须已存在；更新涉及是否投产、运营对接人、风控对接人与备注等列，其中对接人列语义见 [[concepts/op_contact]]。整批失败的设计避免了部分更新造成的数据不一致。

## 版本演进

当前语义分析未提供该规则的历史变更记录。