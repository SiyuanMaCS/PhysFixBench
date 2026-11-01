# batch2 · PhysicsIQ 候选机器预标注（154 条）

> **状态：machine_preannotation 草案，非 human gold。** 本批 154 条来自 Physics-IQ v1/v2 各 197 段视频的机器粗筛（review_bucket=candidate），筛出可修物理问题。**未做逐帧人工复核**，`needs_human_frame_step_confirmation=true`。

## 入库范围

| 项 | 值 |
|---|---|
| 来源数据集 | Physics-IQ（受控物理演示实拍 + self-refine 版本） |
| 源 JSON | `PhysicsIQ_全量机器预标注.json`（SHA256 `e1408ec8…99dc6`） |
| 入库条数 | **154**（v1=70，v2=84） |
| 剔除条数 | 240（review_bucket=reject_no_clear_issue，**不入库**） |
| 每条 issue 数 | 1 |
| 视频时长 | ~5.06s / 段 |
| 标注语言 | 中文 fix_* 指令 + 英文 annotation（原场景 prompt） |

## 18 字段约定

严格对齐 [`docs/data_schema.md`](../../docs/data_schema.md) 与 batch1 四个来源的 key 顺序。本批因机器预标注阶段未采集到分类学字段，下列字段沿用权威 schema 的"未知"取值（**不编造类别**）：

- `generator` = null（v1 为真实拍摄受控演示；v2 self-refine 模型未记录）
- `error_family` / `scenario_domain` / `interaction_primitive` / `review_error_category` = null
- `glitch_category_official` = **null**（PhysicsIQ 无官方 glitch 分类；源 `scenario` 名仅在 `provenance.json` 的 `per_record_machine_trace[].source_scenario` 中溯源）
- `confidence` = null
- `obviousness` = `"unknown"`（沿用权威 schema 中同名字段）
- `all_claimed_errors_visible` = null
- `needs_human_frame_step_confirmation` = **true**
- `annotation` = 原英文场景 prompt（保真）
- `fix_problems` / `fix_expected` = 机器预标注的 issue_description / fix_expected（保真，不改动原文）
- `fix_keep` = **逐字提取自机器 fix_expected 中的"保留/保持/无需修改/其余…不变"子句**；机器未声明保持项则为空字符串 `""`（不编造）

## record key 与 HF 视频路径

- `record_id` = `physicsiq::<version>::<id4d>`，如 `physicsiq::v1::0003`
- `dir_name` = `physicsiq__<version>_<id4d>`，如 `physicsiq__v1_0003`
- HF 相对路径 = `videos/physicsiq/<dir_name>.mp4`（**全新独立子目录**，不触碰现有 `videos/` 扁平文件）

## ⚠️ 视频同步状态（请勿当作可达事实）

- **media_sync_status = pending_authorization**：尚未获得现有 HF 数据集的可用上传授权，未执行媒体同步。
- 在授权到位并完成远端字节/SHA256 校验前，`videos/physicsiq/*.mp4` **在 HF 上尚不存在**。
- 本批 JSONL/CSV 可先行代码评审；视频链接在上传完成前为预留路径，不可作为可点击样本使用。
- 本地源视频字节数合计 32,538,467（v1=15,153,890 / v2=17,384,577），SHA256 已三方核对通过。

## 待人工抽审记录

- `physicsiq::v1::0003` — 机器输出初轮 issues 为空，后补卡，需人工确认
- `physicsiq::v2::0003` — 物理主张存疑（机器称"同时落垫违反自由落体"，判断倒置，疑误报）
- `physicsiq::v2::0004` — 需逐帧视觉确认

## AI 视觉复核记录（非 human gold）

- `physicsiq::v2::0034` — AI 视觉复核收录样本，证据帧 pts=2.5/2.667/2.875s；fix_* 仍以机器预标注为准，本条仅溯源。

## 文件清单

| 文件 | 说明 |
|---|---|
| `physfixbench_physicsiq154.jsonl` | 权威格式，154 行，18 字段 |
| `physfixbench_physicsiq154.csv` | 同内容 + UTF-8 BOM + 3 列人工审核空列；布尔值小写 |
| `provenance.json` | 溯源：源 JSON SHA256、视频 bytes/SHA256 清单、per-record 机器原始输出字符串、submitted prompt 注册表（prompt_id → text）、待抽审记录、AI 复核样本、media_sync_status |
| `README.md` | 本文件 |

## 范围约束

- 不覆盖旧批次 606 条与根 `index.html`
- 本 PR 不合并；待人工复核与媒体同步完成后由维护方决定
