---
type: concept
title: 运营邮件
page_key: operator_email
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [sendEmail, send_email, operator_email, 运营邮件]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantDomainService / TenantAppliactionService 运营邮件开关与收件人"
contract_version: "0.1"
maps_to: tenant_setting_config.send_email
field_targets:
  - tenant_setting_config.send_email
  - tenant_setting_config.operator_email
adjudication: boundary
also_confused_with:
  - tenant_project.send_email
  - tenant_setting_config.operator_email
belong: concepts
field_targets: [tenant_setting_config.send_email]
---

「运营邮件」在契约上指 [[tenant_setting_config]].send_email，即「是否发送」的 Y/N 开关；与之配套的 `operator_email` 是收件地址，两者共同决定触达对象——开关为 Y 且存在收件人时才真正发送。

边界：send_email 是开关，operator_email 是地址，不可互相替代；tenant_project 与 tenant_setting_config 各有一份同名开关，分别对应项目级与租户级运营触达，引用时必须指明所属表。

## 需求背景
运营触达需要按租户（以及按项目）可开关、可指定收件人，避免全量广播。

## 版本演进
v0.1（本页）：首版契约，语义与边界来自语义分析；DB 中 operator_email 存在测试脏值（如 1198273@qq.com），投产前需清理。