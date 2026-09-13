# NCBI Datasets 18.37.0：第三方告知复核

这是固定候选的封装告知审查，不是完整二进制 SBOM，也不是法律保证。
上游两个程序原样分发；包内的 NCBI Public Domain 告知只覆盖 NCBI 自有部分，
不覆盖第三方库、CA 证书或基础运行时。许可原文不作修改。

## 证据与判断方法

- `binary-providers.json` 绑定四个官方二进制 SHA256，合并 DWARF compilation unit 与
  嵌入源码路径的 provider 证据。包括字符串扫描漏掉的 grpc-gateway/v2/runtime。
- `go.mod`/`go.sum` 是 NCBI 固定 commit 的公开 datasets 声明，不冒充 dataformat 锁。
  22 个声明中保留 21 个许可模块的原始源码 ZIP、告知与校验；MPL-2.0 的
  go-cleanhttp / go-retryablehttp 对应公开源码随包提供，未修改这些模块。
- `bou.ke/monkey` 的 LICENSE 不授予使用许可。它只有公开依赖声明，没有 NCBI
  源码 import 或四个二进制中的链接证据；不下载、执行或分发其代码，仅保留排除记录。
- dataformat 的 20 个已观察 provider 全部有独立的许可参考来源。参考 ZIP 用 SHA256
  和 Go checksum database 的 h1 校验，完整保留原始文件级版权与嵌入告知，另外提供
  可直接阅读的 LICENSE/NOTICE/AUTHORS/PATENTS 与版权注释片段。
- 对各 provider 根许可的公开默认分支历史检查截止 2026-09-09；更名前路径也检查
  （grpc-gateway 的 LICENSE.txt）。历史原文/commit/digest 均保留。参考源码版本只用于
  定位告知文本；实际 dataformat 依赖版本未知，字段保持 null，不能用于漏洞版本判断。

## dataformat 许可义务覆盖

| provider | 告知与处理 |
| --- | --- |
| quicktest | MIT；保留 Francesco Banconi 和 Canonical 两代版权署名 |
| btree | Apache-2.0，原始源码头版权一并保留 |
| go-cmp | BSD-3-Clause / Go Authors |
| grpc-gateway/v2 | BSD-3-Clause / Gengo；原 LICENSE.txt 与改名后文本，另保留内嵌 casing 的 Go Authors BSD 告知 |
| kr/pretty、kr/text | MIT / Keith Rarick；pretty 的历史差异仅许可标题/格式，原文均保留 |
| go-isatty | MIT / Yasuhiro Matsumoto |
| fastuuid | BSD-3-Clause / Roger Peppe |
| go-internal | BSD-3-Clause / Go Authors |
| xmlwriter | Apache-2.0；嵌入的 Little Star Media BSD 文件头原文保留 |
| cobra | Apache-2.0；Cobra Authors 及 kr/text 相关告知保留 |
| pflag | BSD-3-Clause / Alex Ogier、Go Authors |
| xlsx/v3 | BSD-3-Clause / Geoffrey Teale；保留 Paul Smith MIT 改编、Rodrigo Moraes 文件头和 AUTHORS |
| genproto api/rpc | Apache-2.0 / Google，原始生成源码版权保留 |
| grpc | 当前 Apache-2.0、NOTICE.txt、AUTHORS；2017 年前 BSD 历史文本也保留，不推断旧版本链接 |
| protobuf | BSD-3-Clause、PATENTS，Google/Go Authors 文件头均保留 |
| x/net、x/sys、x/text | BSD-3-Clause、PATENTS；2024 年版权格式调整前后原文均保留 |

已观察 dataformat provider 的义务为保留许可、版权、适用的 NOTICE/专利告知；没有
发现需要其私有应用源码的适用条款。参考版本未知不等于这些原文无法保留；这里不把
“完整 SBOM”或“必须先得到上游回复”增加为发布条件。若后续出现未观察组件、许可
冲突、修改过的 copyleft 代码或其它具体义务证据，应重新审查并发布不可变后继修复。

## 基础运行时

Go 1.23.4 身份由四个二进制 build-info 确认，Go/runtime/vendor 的原始告知随包提供。
BusyBox 1.37.0 的完整源码 tar、两架构官方镜像 source commit 中实际使用的 Dockerfile、
配置生成步骤和三个补丁随包提供，保留 GPL-2.0 及组件告知；没有重新编译或修改基础程序。
另保留 getconf 的 NetBSD BSD-2-Clause 源文件、musl COPYRIGHT/参考源码、Buildroot
许可/实际 skeleton 来源，以及 UTC tzdata 的 Public Domain 告知。musl/tzdata 参考版本
不用于声称基础镜像的精确 APK 构建版本。Debian CA-certificates copyright 另随证书复制。

材料位置：`/opt/ncbi-datasets/share/licenses/third-party/`。`sources/` 提供公开 Go 模块
源码；`reference-sources/` 是 dataformat 告知参考，不能冒充私有 dataformat 对应源码；
`base/sources/` 与 `base/recipes/` 提供 BusyBox 源码与原始构建材料。
`SHA256SUMS` 和独立固定的校验表哈希验证材料完整性，不替代上述人工义务审查。

依据：各材料的固定来源见 notices.lock.json；Apache-2.0 第 4 节、MPL-2.0 第 3 节
以及原始 MIT/BSD/GPL 文本。未代表维护者向上游发送任何消息。
