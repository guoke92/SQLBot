---
type: table
title: sys_cust_user_rel 客户用户关系表
page_key: sys_cust_user_rel
domain: 平台内部服务对接
status: draft
aliases:
  - 客户用户关联表
  - 经办人关系表
oid: 1
scope:
  databases:
    - lowcode_pplatform
sources:
  - code
contract_version: "0.1"
belong: tables
---

sys_cust_user_rel 描述客户（`cust_id`、`cust_type`）与系统用户（`user_id`）之间的授权关系，并记录角色 `role_id`、产品 `product_id` 以及冻结状态 `is_freeze`。在内部服务对接中，它是用户能否以某企业身份操作某产品的主要判据：查询侧使用未冻结口径 [[not_frozen_user_rel]]，产品维度使用 [[current_product_rel]]，冻结/解冻的流转见 [[operator_freeze_flow]]。

## 需求背景
运营侧需要对经办人执行冻结与解冻，冻结后该用户与该客户/产品的关联不应再参与权限判定；同时同一用户可能关联多个产品，判断「是否已关联指定产品」必须带上产品条件，不能只看关系是否存在。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，字段物理类型与字典绑定尚未在证据中出现，暂留空。

