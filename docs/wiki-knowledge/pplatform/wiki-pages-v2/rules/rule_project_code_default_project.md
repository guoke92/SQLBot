---
type: rule
title: 项目码必填联动默认项目
page_key: rule_project_code_default_project
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [项目码必填联动, projectCodeRequired 校验, TASK-0003]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code_path:TenantDomainService.java:checkBeforeSave（注释 TASK-0003）"
  - "reqdoc:租户管理业务规则文档"
contract_version: "0.1"
belong: rules
---

本规则约束 [[project_code_required]] 与 `default_project_id` 的联动：当 projectCodeRequired='Y' 时必须提供 defaultProjectId，否则抛出 COMMON_EXCEPTION『项目码为必填时，请先配置默认关联项目』，租户保存或迁移会被拦截。字段语义见 [[project_code_required]] 与 [[tenant_setting_config]]。

## 需求背景
该规则有双源证据：代码侧为 `TenantDomainService.checkBeforeSave`（源码注释标注 TASK-0003），业务侧见租户管理业务规则文档 reqdoc:租户管理业务规则文档。文档明确项目码必填的租户必须先配置默认关联项目，代码据此前置校验；两处描述一致，故作为锚点证据登记。校验失败的信息文案与代码一致，导出/保存路径共用同一拦截。

## 版本演进
v0.1（本页）：首版契约，锚点证据为代码 + 需求文档双源；暂无历史版本记录。

```ground:rule
name: 项目码必填联动默认项目
content: "projectCodeRequired='Y' 时必须提供 defaultProjectId，否则抛 COMMON_EXCEPTION『项目码为必填时，请先配置默认关联项目』"
impact: "租户保存/迁移被拦截"
field_targets:
  - tenant_setting_config.project_code_required
  - tenant_setting_config.default_project_id
evidence: "code_path:TenantDomainService.java:checkBeforeSave（注释 TASK-0003）+ reqdoc:租户管理业务规则文档"
```