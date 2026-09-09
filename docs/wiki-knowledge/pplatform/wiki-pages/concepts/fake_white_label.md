---
type: concept
title: 假贴牌
page_key: fake_white_label
belong: concepts
domain: 租户迁移
status: published
aliases: ["假贴牌"]
oid: 1
sources: ["semantic_analysis_v0.1"]
contract_version: "0.1"
maps_to: "代码未见专属字段；疑似通过 tenant_flg_en/app_tenant_code/band_name 间接区分"
also_confused_with: ["贴牌", "自营租户"]
adjudication: boundary
scope:
  databases: [lowcode_pplatform]
---

# 假贴牌

业务定位：假贴牌是需求中定义的一种特殊租户贴牌类型，但当前提供代码中无直接实现字段，仅能通过相关字段间接推断。

## 需求背景

需求中假贴牌具有明确业务定义：在租户配置表单内不可见（仅后台可见），作为二级贴牌挂在自营贴牌下，且内管端可正常创建该二级贴牌下的项目。但代码中未找到对应的可见性控制、二级贴牌建模或项目创建判断逻辑，因此无法锚定具体实现。

## 版本演进

- (document_claim，未证实) 假贴牌在租户配置表单内不可见（仅后台）
- (document_claim，未证实) 假贴牌作为二级贴牌挂在自营贴牌下
- (document_claim，未证实) 内管端可正常创建该二级贴牌下的项目

[[数据租户标识]] [[app_tenant_code]]