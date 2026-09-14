---
type: concept
title: 建档结果出站
page_key: archive_result_outbound
domain: 外部渠道与银行对接
status: draft
aliases:
  - archiveCallback
  - notifyArchiveResult
  - ITmCustEventListener
  - IAlipayAntArchiveEventListener
oid: 1
scope:
  databases:
    - cust
sources:
  - code:ITmCustEventListener
  - code:IAlipayAntArchiveEventListener
  - code:TianmaConsumer
contract_version: "0.1"
maps_to: cust_company_info.cust_build_status
also_confused_with:
  - cust_company_info.check_status
adjudication: boundary
belong: concepts
field_targets: [cust_company_info.cust_build_status]
sources: ["enrich:wiki-admin"]
---

> (document_claim，未证实)

「建档结果出站」指把本地建档结果回推给渠道方的能力，各渠道实现方式不同。

## 需求背景
蚂蚁渠道为 Dubbo 事件 → FBP 通知（有效）；天马渠道的出站逻辑仅存在于已整体注释的 TianmaConsumer，实际未生效，因此天马侧不能按有效链路理解。出站结果的状态依据是建档状态而非审核状态，二者边界见 [[company_archive]] 与 [[check_status]]。

## 版本演进
- (document_claim，未证实) 天马客户信息同步出站：产融内部事件 → TmCustEventListener → BeanUtils.copyProperties 至 CompanyArchivePushReq → 日期格式化为 yyyy-MM-dd → TianmaService.companyArchiveDetail → HTTP POST。该主张在代码侧被证伪：TianmaConsumer 整文件被块注释，@RabbitListener/@Component/@Autowired 均被注释，实际未生效。
- (document_claim，未证实) HSCC 蜂巢出站：WhhimService 组装 → Md5Utils 签名 → WhhimHttpClientOpenApiClient → 失败抛 WhhimOpenApiException。本次链路未覆盖对应类，待补证。

相关：[[cust_company_info]]
