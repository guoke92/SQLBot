---
type: entity
title: AMS
created: 2026-08-28
updated: 2026-08-28
tags: [AMS, SaaS产品, 业务系统, 供应链金融]
related: [chanrong-platform, xunyilian, product-chanrong]
sources: ["需求文档/产品需求规格说明书_产融平台V1.0.0.docx"]
---

# AMS

AMS是被提及的现有SaaS产品之一，将被集成到[[chanrong-platform|产融平台]]中。

## 在产融平台中的定位

AMS属于产融平台底座的已上架产品列表，[[tenant|租户]]可以为终端用户选择提供AMS产品的服务。

## 与其他系统的关系

- AMS与[[xunyilian|讯易链]]同属"业务系统"范畴
- AMS的项目数据需从业务系统同步至产融平台
- AMS旧客户（如项目公司）要开通其他产品时，需补充企业材料，走企业升级流程

## 注意事项

文档中提到企业维护字段的运营中台与产融平台存在字段差异（红色字体标注的新增或必填变更字段，黄底标注的产融有但运营中台缺失字段），这表明AMS作为已运行系统，其数据迁移和对接需要特别关注字段映射。