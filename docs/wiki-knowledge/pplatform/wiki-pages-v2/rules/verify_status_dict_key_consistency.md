---
type: rule
title: 核查状态字典键一致性规则
page_key: verify_status_dict_key_consistency
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - getDictParam 与 getDictKey 一致性
  - 读写键不一致风险
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java
contract_version: "0.1"
belong: rules
---

# 核查状态字典键一致性规则

## 业务定位

约束 [[tables/cust_certification_info|认证记录表]] 中核查状态字段的取值口径：`auto_verify_status` 与 `manual_verify_status` 写入使用 `getDictParam()`，而人脸通过判断读取使用 `getDictKey()`。

## 需求背景

同一字段存在写入键与读取键两套取值来源时，若字典 param 与 key 不相等，会出现「已写入通过但判断不通过」的取数偏差，进而阻断 [[concepts/h5_face_intent|H5刷脸意愿]] 回填与 [[processes/ca_submit_status|CFCA 上送状态]] 推进。

## 版本演进

从代码可见，写入路径（`saveOrUpdate` / `saveManual`）与判断路径（`isFaceVerifyPassed`）取值方法不同，构成读写键不一致风险；[[tables/cust_person_info|联系人表]] 的 `face_status`/`phone_realname_status` 采用 `getDictKey()` 写入，与之口径又不同。

```ground:rule
name: 核查状态字典键一致性
predicate: "cust_certification_info.auto_verify_status 与 cust_certification_info.manual_verify_status 写入取 CustCertificationTypeEnum 体系 getDictParam()，人脸通过判断取 getDictKey()；两者须指向同一字典值，否则判定失效"
scope: 认证记录写入与人脸通过判断链路
evidence: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java:saveOrUpdate, lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/verify/impl/AutoVerifyServiceImpl.java:saveManual, lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/FaceVerifyController.java:isFaceVerifyPassed
```

关联页面：[[calibers/face_verify_passed|人脸认证通过]]、[[concepts/face_auth_passed|人脸认证通过（术语）]]。

---REVIEW: rule | 核查状态字典键一致性规则---
语义分析指出写入用 `getDictParam()`、判断用 `getDictKey()` 且「存在读写键不一致风险」，但未给出两个方法对应的具体字典键/参数值。本页按证据原样登记风险，predicate 中的枚举归属待与枚举写值点核对后修正（以写值点 + DB 为准）。
---END REVIEW---