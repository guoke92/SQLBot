---
type: caliber
title: 当前产品关联
page_key: current_product_rel
domain: 平台内部服务对接
status: draft
aliases:
  - 指定产品关联口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
belong: calibers
---

「当前产品关联」是在 [[sys_cust_user_rel]] 上判断用户是否已关联指定产品时使用的条件：`product_id` 等于入参 productId。产品维度不能省略——同一用户对不同产品可能各有一条关系记录，只按用户判定会误认为已开通全部产品。产品编码的来源见 [[tenant_product]]，企业侧产品授权见 [[cust_auth_application]]。

## 需求背景
新增或更新经办人时需要先确认该用户在产品维度上是否已有关系，以决定插入还是更新；产品取值必须来自调用方传入的产品上下文，而不是从关系记录中猜测。

## 版本演进
- v0.1（本页）：口径谓词来自代码语义分析，参数形式以证据中的写法为准。

```ground:caliber
name: 当前产品关联
predicate: "sys_cust_user_rel.product_id = :productId"
scope: 判断用户是否已关联指定产品
evidence: "code_path:PlatFormUserApplication.java:addOrUpdateOperatorUser"
```