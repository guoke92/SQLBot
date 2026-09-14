---
type: concept
title: 是否需要验证码（需求文档串入）
page_key: captcha
domain: 项目报表/统计/上报
status: draft
aliases:
  - captcha
  - 行为验证码
oid: 1
scope:
  databases:
    - unknown
sources:
  - reqdoc:SSO验证码登录改造技术设计
contract_version: "0.1"
maps_to: "SSO 登录域字段，与项目报表/统计/上报主题无关"
also_confused_with: []
adjudication: boundary
boundary: "需求文档 reqdoc:SSO验证码登录改造技术设计 对本主题无结构性贡献，仅在 cust_project_rel / tenant_project 表字段附录处与本主题交叉，不作为字段值来源。"
belong: concepts
---

# 是否需要验证码（需求文档串入）

「是否需要验证码 / captcha / 行为验证码」属于 SSO 登录域的字段，语义上与本主题（项目报表/统计/上报）无交集。

## 需求背景

该词出现在需求文档 reqdoc:SSO验证码登录改造技术设计中，仅在 cust_project_rel / tenant_project 的表字段附录处与本主题发生文本交叉。本主题的任何字段说明、口径、规则都不得以该文档作为字段值来源；如遇引用，应按登录域归档。

## 版本演进

无本主题内的版本演进；该术语的存在仅为避免跨主题混引。相关表见 [[tables/cust_project_rel]]。