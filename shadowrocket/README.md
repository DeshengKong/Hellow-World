# We Neuro Shadowrocket v31

更新日期：2026-11-27。适用于已经在各设备导入节点的 Shadowrocket 用户；本仓库不包含节点密码或订阅凭据。

## 从哪里更新

长期更新地址只有一个：

<https://raw.githubusercontent.com/DeshengKong/Hellow-World/master/shadowrocket/we-neuro-shadowrocket.conf>

旧 `we-neuro-shadowrocket-home.conf` 地址继续可用。两个入口的内容完全相同，旧入口内的 `update-url` 已指向上述长期地址，因此旧 v25 家宽配置也能迁移。今后编辑 `profile.template.conf` 并统一生成两个入口，避免重新分叉。

### 这次升级怎么操作

1. iPhone 和 Mac 分别更新当前使用的配置，并确认该配置处于启用状态。若远程配置尚未添加，使用上面的完整 URL 导入。确认文件首行显示 **v31**。
2. 使用 **配置模式**。全局代理模式会改变这里的分流行为，不能用来验收这些规则。客户端须支持本配置的语法，最低 **2.2.65**；保持客户端更新。
3. 确认本机存在精确名称 `HOME-Verizon-LAX`、`DMIT-LAX-TLS`、`DMIT-TYO-TLS`。Bybit 应只匹配 **台湾高级 IEPL 专线 1**；允许截图中的 `🇨🇳`、`🇹🇼` 前缀或无旗名称，不允许专线 2、10、11、标准或实验节点。若候选为空或有重复，先纠正本机节点名称/订阅。
4. 在分组里核对 **Google、Claude、WebRTC、出口检测 → HOME-Verizon-LAX**。YouTube 只有 Google 一个上级分组。OpenAI、Muse、海外主力默认 LAX；GrokBot 保留原来的手动选项。更新配置可能保留设备上的旧选择，不能只看文件默认值。
5. 让配置的 24 份远程域名表全部下载成功，然后重新连接 Shadowrocket，关闭旧应用连接、重新打开需要验收的应用。不要把旧连接日志当成新版结果。“测试并选择最快”应保持关闭。

旧 N26、Starryblu、Wise、IBKR、嘉信、OKX 分组被移除是预期行为：这些已知业务域现在直接命中 `DIRECT`，无需再给这些组手动选节点。

## 路径表

下表是配置模式、资源加载成功、节点名称正确时的配置意图；设备保存的手动选择仍需核对。

| 业务 | 新版策略 | 说明 |
|---|---|---|
| N26 | 已知业务域固定 DIRECT | `n26.com`、`number26.de`、新增 `tech26.de`，包括子域 |
| Wise、IBKR、嘉信、Starryblu、OKX | 已知业务域固定 DIRECT | 补齐已核验的地区、交易和 API 域；不再经过可变业务分组 |
| 国内支付、银行 | DIRECT | 保留国内金融白名单；抖音两个已核验登录/支付入口也提前保护 |
| Coinbase | 仅 DMIT-LAX-TLS | 删除 DIRECT/PROXY 备选，避免误选 |
| Bybit | 台湾高级 IEPL 专线 1 | 限定候选，不再接受任意台湾高级节点；补 `api.bytick.com` |
| PayPal | LAX 首选，保留手动选项 | 保持原有使用方式 |
| Safepal | 海外主力 | 保持原策略 |
| Google / YouTube / Gemini / Antigravity / Colab / Cloud | 家宽首选，手动 LAX 备选 | 统一 Google 组；补 `.google`、`.goog`、`pkg.dev`、Tenor 等核心覆盖 |
| Claude 体系 | 家宽首选，手动 LAX 备选 | 保留用户给出的域名，补专用身份/CDN租户和两个官方列出的遥测主机 |
| OpenAI / Muse | LAX 首选，手动家宽备选 | `chat.com`、`sora.com` 回到 OpenAI；Muse 保持原来三个业务根域 |
| Grok / Cursor | 原 GrokBot 手动分组 | 默认 LAX；保留家宽及原美国高级专线备选 |
| 苹果官网和在线商店指定主机 | 固定 DMIT-LAX-TLS | `apple.com`、`www.apple.com`、`*.store.apple.com`、`*.storeimages.cdn-apple.com` |
| Apple ID、iCloud、普通苹果服务 | 苹果服务，默认 DIRECT | 原有 Apple AI/Siri/relay 例外明确保留；Apple `17/8` 兜底放在业务域之后 |
| 微软普通服务 | 微软服务，默认 DIRECT | Copilot 例外保持 LAX；共享云租户不再整个归为微软直连 |
| 出口检测网站 | 家宽默认 | 增加 `ippure.com`；测试结果只代表测试网站本身的路由 |
| 已知 STUN / 指定 UDP 端口 | WebRTC，默认家宽 | 与应用业务分组独立，不能据此宣称所有 WebRTC 均已覆盖 |
| 其他服务、国内 / 海外兜底 | 保留原分组默认 | 流媒体等仍可手动选择原节点；普通国内 DIRECT，普通海外主力默认 LAX |

Google Cloud 的 `run.app`、`appspot.com`、`web.app`、`pkg.dev` 等托管命名空间仍按用户“整个 Google 体系走家宽”的偏好处理。因此这些宿主下的第三方租户也可能走家宽；更早的已知业务域规则优先。

## 这次为什么要改结构

v30 的问题不止漏了一个域名。`tech26.de` 没有 N26 专属规则，会落到 Global/海外主力；N26、Starryblu 分组又混用了 DIRECT 默认、地区正则和设备保存的选择。没有历史连接日志，不能把那次 N26 登录的确切原因断言成其中某一项。

另外，旧版 53 个外部文件跟随上游分支变化，里面还混有整个共享平台、IP 段、ASN、关键词和 User-Agent 规则。按顺序匹配时，早出现的宽泛规则能截获后面本来属于其他业务的连接。例如：

- Netflix 的整个 `us-west-2.amazonaws.com` 与大量共享地址；Amazon 的整个 `amazonaws.com`、`cloudfront.net`。
- 微软/China 的整个 `windows.net`、`msecnd.net`；Apple、微软和 China 重复收录整个 `akadns.net`。
- 共享 Auth0、Stripe、Sentry 等被归入 OpenAI；`chat.com`、`sora.com` 和 Facebook 被泛 AI 表抢先匹配。
- TikTok 的整个 `snssdk.com` 抢在抖音 DIRECT 规则之前，影响已确认的抖音登录和支付主机。
- China 表的整个 `.ms` 顶级域。它不是“微软/中国域名”的判据。

v31 将关键域写在主配置前部；保留业务的手动选择，只删除六个需要固定 DIRECT 的金融分组。其他规则由 49 个**固定 commit、固定 SHA-256** 的上游输入生成 24 份本仓库快照，每个配置引用都固定到数据提交的完整 SHA，发布后不会跟着上游悄悄变化。

清理是取消错误分类，不是封锁这些平台。明确的专用租户仍保留；无法归属的共享地址回到正常兜底。共享的 `.cn` 地址仍遵循国内 DIRECT，这是有意保留的国内策略。社区域名表是覆盖线索，不等于对每一个域名的所有权作了独立认证。

## DNS 如何工作

```ini
dns-server = https://cloudflare-dns.com/dns-query#proxy=HOME-Verizon-LAX
fallback-dns-server = https://dns.google/dns-query#proxy=HOME-Verizon-LAX
proxy-dns-server = 223.5.5.5,119.29.29.29
dns-direct-system = true
dns-direct-fallback-proxy = false
```

主解析和备用解析都通过**实际节点 HOME-Verizon-LAX**，不是通过名称相似的分组。备用解析提供解析服务的冗余，不提供出口线路的冗余。旧 `fallback-dns-server = system` 以及 `[Host]` 下 Apple/iCloud 的系统 DNS 覆盖已移除。

`proxy-dns-server` 只用于解析代理节点自身的域名，帮助建立代理连接；它不是“所有代理业务域名的 DNS”。DIRECT 业务仍使用本地/系统解析，这是有意的国内直连行为。浏览器或应用自行建立的 DoH、系统绕过、其他模块覆盖及未接管的流量需要另行观察，本配置不把它们当成已经受控。

### 家宽完全断线时的手动应急

仅把 Google/Claude 切到 LAX **不能**处理家宽 DNS 同时断线的场景。完整操作是：

1. 将当前配置的这两项一起改为：

   ```ini
   dns-server = https://cloudflare-dns.com/dns-query#proxy=DMIT-LAX-TLS
   fallback-dns-server = https://dns.google/dns-query#proxy=DMIT-LAX-TLS
   ```

2. Google、Claude、WebRTC 手动选 `DMIT-LAX-TLS`；出口检测选 `海外主力`，并确认海外主力选择 `DMIT-LAX-TLS`。如 OpenAI/Muse/GrokBot 当时手动用了家宽，也一起选回 LAX。
3. 重新连接，验证新连接与解析结果。家宽恢复后更新统一配置恢复两条 HOME DNS，并核对相应分组回到家宽。

配置更新会覆盖本地 DNS 应急改动。这里不设置自动跨出口切换；“指定节点丢失/不可用时客户端究竟怎样失败”仍须在真实设备上验收，不能以文本配置冒充已验证的全系统断网保护。

## 实机验收：看新连接，而不是只看 IP 检测页

| 验收项目 | 应观察到什么 |
|---|---|
| `api.tech26.de` / `app.n26.com` | 连接记录命中主配置 DIRECT，不能显示 N26 地区组或海外主力 |
| Google / Claude 请求 | 业务组指向 HOME-Verizon-LAX；包括身份/API/内容域，不只首页 |
| `chat.com` / `sora.com` | 命中 OpenAI；`facebook.com` 命中 Facebook |
| Bybit | 分组只有确认的专线 1；`api.bytick.com` 命中 Bybit |
| 苹果官网 | `www.apple.com` 和指定商店主机命中 DMIT-LAX-TLS |
| 出口检测 | 当前选择家宽时，检测网站显示预期家宽公网地址 |
| DNS 测试 | 新解析经家宽绑定的加密 DNS；解析器品牌、城市或多个 anycast 地址本身不能等同于本地泄漏 |
| WebRTC 测试 | 关注公网候选是否出现非预期本地公网出口；私网地址或 mDNS 名称不能单独当作公网泄漏结论 |

验收时保留相同时间段的连接日志、域名、命中规则、实际节点及测试结果。不要为测试反复操作银行转账/付款；正常新连接的日志即可提供路由证据。

域名规则分不清同一主机上的 `/us` 与 `/cn` 路径，也无法根据“哪个 App 发起”区分完全共享的第三方主机。因此苹果官网规则同样作用于这些主机的其他地区页面；Apple Pay 的商户、发卡行和服务端后续通信也不能由手机代理统一控制。共享 STUN、npm、GitHub、支付及身份平台仍按它们自己的明确策略或普通兜底处理，不宣称所有第三方调用都属于 Claude/Google。配置一致性不等于账号风控保证。

## 维护和回归

从仓库根目录运行：

```bash
python shadowrocket/tools/build_rules.py --source-cache /path/to/verified-input-cache
python shadowrocket/tools/render_profile.py
python shadowrocket/tests/test_routing.py
```

没有本地缓存时，构建器只下载 `sources.lock.json` 指定的完整 commit URL，并校验 SHA-256；内容不一致直接报错，不悄悄接受变化。排除清单见 `domain-exclusions.json`，逐项记录范围、理由及证据强度。不要只改生成后的 `.list` 而不修改输入/排除清单。

升级规则的发布顺序：审阅并更新 source lock → 构建域名快照 → 静态回归 → 创建不可变数据提交 → 将 `release.json` 的 `rules_commit` 指向该提交 → 统一生成两个入口并再次验证 → 原子快进主分支。不要让配置引用可变 `master` 的业务清单。Google/Apple/Telegram 的本地 IP 例外需单独核验；本次快照证据放在 `rules/v31/evidence/`。

回归覆盖金融域边界、主力组切换后的不变量、Google/Claude/OpenAI/Apple/流媒体等业务归属、共享根回落、Bybit 候选筛选、分组引用、DNS URL 的 `#proxy` 片段、快照哈希和两个入口一致性。这是独立静态模型，**不是 Shadowrocket 原生测试，也不是手机 DNS/WebRTC 实测通过证明**。具体数量和发布记录见 [v31 变更与验证说明](CHANGELOG-v31.md)。

回退前保留当前可用配置副本。v30 的只读历史地址为：

<https://raw.githubusercontent.com/DeshengKong/Hellow-World/47e87c59ada75782aa12f4600a65dd8f3eb65463/shadowrocket/we-neuro-shadowrocket.conf>

回退也会恢复该版本已知问题；它是恢复连接的手段，不代表旧版已经安全修复。

## 主要依据与许可

- 金融域证据及继承范围：[domain-evidence.json](domain-evidence.json)。
- Shadowrocket 官方 DNS 代理、节点引导解析公告：[2.2.62](https://t.me/s/ShadowrocketNews/864)、[2.2.64](https://t.me/s/ShadowrocketNews/937)。
- [Claude 官方网络要求](https://code.claude.com/docs/en/network-config)。
- [Apple 自有地址及 APNs 说明](https://support.apple.com/en-us/102266)。
- [Google API 网络范围说明](https://docs.cloud.google.com/vpc/docs/access-apis-external-ip?hl=en)、[goog.json](https://www.gstatic.com/ipranges/goog.json)、[cloud.json](https://www.gstatic.com/ipranges/cloud.json)。
- [Telegram 官方网络范围](https://core.telegram.org/resources/cidr.txt)。
- [Akamai GTM 客户域名说明](https://techdocs.akamai.com/gtm/docs/traffic-mgmt-domains)。
- [抖音官方授权接口](https://open.douyin.com/platform/resource/docs/openapi/account-permission/douyin-default-get-permission-code)。
- [IANA `.ms` 顶级域说明](https://www.iana.org/domains/root/db/ms.html)。

域名快照源自 `blackmatrix7/ios_rule_script`，保留作者及来源标识，修改内容和日期见各文件头、排除清单及 manifest。上游 GNU GPL v2 全文随附于 [rules/v31/LICENSE](rules/v31/LICENSE)。本配置仅做流量选择，不启用 MITM，也不要求安装 CA 证书。
