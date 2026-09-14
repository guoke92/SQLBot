---
type: rule
title: 批量更换运营模板二选一
page_key: batch_change_operator_template
domain: 经办人/联系人/管理员管理
status: draft
aliases: [batchChangeOperatorTemplateDownload, 批量换运营]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonApplication.java#batchChangeOperatorTemplateDownload"]
contract_version: "0.1"
belong: rules
---

batchChangeOperatorTemplateDownload 要求 operatorIds 与 projectIds 互斥（XOR），且各自勾选数量 ≤ BATCH_CHANGE_OPERATOR_TEMPLATE_SELECTION_MAX；导入时按"企业名+租户名"定位企业，同名新运营人员（>1）报错（[[operator]]、[[cust_person_info]]）。

## 需求背景
- 该规则限制批量换运营的输入规模并消除企业定位歧义，避免一次导入命中多义企业或超量数据（[[operator_assign_before_invite]]）。

## 版本演进
- 当前版本导出模板使用 operator_realname 作为运营人员标识（[[operator]]）。

```ground:rule
name: 批量更换运营模板二选一
content: "batchChangeOperatorTemplateDownload 要求 operatorIds 与 projectIds 互斥（XOR），且各自勾选数量 ≤ BATCH_CHANGE_OPERATOR_TEMPLATE_SELECTION_MAX；导入按“企业名+租户名”定位企业，同名新运营人员（>1）报错"
impact: 限制批量换运营的输入规模与歧义
field_targets:
  - cust_person_info.operator_id
  - cust_person_info.operator_realname
evidence: "code_path:CustPersonApplication.java#batchChangeOperatorTemplateDownload"
```

相关页面：[[operator]]、[[cust_person_info]]、[[operator_assign_before_invite]]。