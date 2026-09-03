---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:wechat-project-initiation@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 立项数据来源
page_key: data_source
domain: 项目审批
aliases:
- 企微同步
- 手工创建
- 模拟立项
- 模拟立项
- 数据来源标记
- MN-前缀
anchors:
- data_source
---
# 立项数据来源

WECHAT=企微 API 同步（小时级 Job）；MANUAL=手工模拟立项（spNo=MN-yyyyMMdd-XXXX 后端生成，dataSource 强制 MANUAL、spType 固定'金融科技业务'、systemDelivery='SaaS'、projectPhase='IMPLEMENTATION'、方案经理=当前登录用户）。导出仅含 WECHAT。

```ground:enum
enum: data_source
fields:
- wechat_project_approval_apply.data_source
values:
  WECHAT:
    label: 企微同步
  MANUAL:
    label: 手工创建
```

## 关联
- [[wechat_project_approval_apply|wechat_project_approval_apply]]
