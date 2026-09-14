---
type: rule
title: 影像 zip 解压安全阈值
page_key: zip_unzip_safety
domain: 外部渠道与银行对接
status: draft
aliases:
  - unzipSafely
  - zip 炸弹防护
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.unzipSafely
  - code:CustAccessApplication.resolveZipEntry
contract_version: "0.1"
belong: rules
---

渠道上传影像压缩包解压时设双重防护：解压总字节超过 512MB 主动中断；entry 归一化后必须落在目标目录内，防止 zip 炸弹与路径穿越。

## 需求背景
影像由外部渠道提供，属于不可信输入；该防护是非自主建档影像入库的前置条件（[[independent_archive_validation]]），通道配置见 [[cust_sftp]]。

## 版本演进
暂无版本演进记录。

```ground:rule
name: 影像 zip 解压安全阈值
content: 解压总字节超过 512MB 主动中断；entry 归一化后必须落在目标目录内，防 zip 炸弹与路径穿越
impact: 渠道影像入库安全性
field_targets: []
evidence: "code:CustAccessApplication.unzipSafely / resolveZipEntry"
```