# Codex Skill：旅行人像专业审片、醒图修图教学（A/B/C）

这是**可执行的 Codex Skill 包**：评片由具有图像理解能力的 Codex 完成，脚本只处理照片预览、文件归档和 DOCX 文档；没有内置算法私自给照片打分。**不会修改、移动、删除原件，也不会自动完成修图**。B 档提供在手机“醒图”中手动复现的详细方案。

## 一、安装到 Codex Desktop（Mac）

1. 将压缩包解压，得到 `portrait-photo-curator` 文件夹。
2. 打开 Mac「终端」，粘贴（把 `~/Downloads/portrait-photo-curator` 替换为实际解压位置）：

   ```bash
   mkdir -p ~/.agents/skills
   cp -R ~/Downloads/portrait-photo-curator ~/.agents/skills/
   python3 -m venv ~/.agents/skills/portrait-photo-curator/.venv
   ~/.agents/skills/portrait-photo-curator/.venv/bin/python -m pip install -r ~/.agents/skills/portrait-photo-curator/requirements.txt
   ```

   若安装过同名 Skill，先手动核对/合并版本，**不建议盲目覆盖原 Skill**。
3. 如果照片里有 HEIC/HEIF 或相机 RAW，额外运行：

   ```bash
   ~/.agents/skills/portrait-photo-curator/.venv/bin/python -m pip install pillow-heif rawpy
   ```

4. 重启 Codex Desktop，确认可以提及 `$portrait-photo-curator`。使用脚本时优先调用 `~/.agents/skills/portrait-photo-curator/.venv/bin/python`；下文示例的 `python3` 在使用虚拟环境时请替换为该路径。
5. 把一组照片放在本地目录，例如 `/Users/你的用户名/Pictures/2026_旅行人像`。确保 Codex 当前工作区对照片**有读取权限**，对结果文件夹**有写入权限**。

Codex 技能标准结构是 `<skill名>/SKILL.md`，个人技能通常放在 `~/.agents/skills/`。要仅在单个项目生效，可改放 `<项目>/.agents/skills/portrait-photo-curator/`。

## 二、给 Codex 的使用指令（复制这一段即可）

> 请使用 `$portrait-photo-curator` 对文件夹 `/Users/你的用户名/Pictures/2026_旅行人像` 中**全部**照片逐张从专业摄影师角度审片。把结果放到 `/Users/你的用户名/Pictures/2026_旅行人像_审片结果`。严格分 A 可直接出片、B 后期可修、C 不可用废片。A 逐张指出可学习的优点和摄影原则；B 逐张解释问题、醒图可复现操作步骤和调整起点、背后的摄影规则以及下次拍摄怎么避免；C 只筛出、不写原因。按 Skill 全流程逐批查看图片、填写评审 JSON、执行核验并归档原图副本，在 A/B 文件夹生成中文 Word 报告。不得跳片、覆盖或更改原件。看图能力不可用时必须说明并停止，不得伪造审片。

> 建议先用**10～20 张**跑一次体验，再跑大量照片。上百张分批执行可能跨越多个 Codex 会话，**必须续做，不应将未看照片默认分档**。

## 三、脚本命令（Codex 会按 Skill 自动使用）

```bash
# 生成清单、预览与联系表；这个步骤完全不会给照片评分
python3 ~/.agents/skills/portrait-photo-curator/scripts/photo_workflow.py prepare \
  --input "/你的/原图目录" --output "/你的/新结果目录" --batch-size 16

# Codex 逐张看图后填写 _work/reviews/batch_###.json，检查是否漏片
python3 ~/.agents/skills/portrait-photo-curator/scripts/photo_workflow.py verify \
  --output "/你的/新结果目录" --phase review

# 有争议的照片生成更大预览以二次确认（不修改原片）
python3 ~/.agents/skills/portrait-photo-curator/scripts/photo_workflow.py detail \
  --output "/你的/新结果目录" --id P0001 --size 4500

# 正式归档并产出 A/B 档的 docx；随后全量校验哈希
python3 ~/.agents/skills/portrait-photo-curator/scripts/photo_workflow.py finalize \
  --output "/你的/新结果目录"
python3 ~/.agents/skills/portrait-photo-curator/scripts/photo_workflow.py verify \
  --output "/你的/新结果目录" --phase final
```

脚本会严格要求每张都分档、每批 JSON 合法、A/B 内容齐全，C 仅有 `id` 和 `grade`。重复 ID、漏张、错误字段会中止。A/B 文件夹附图片和 `.docx`，C 文件夹只放副本图片；Word 文档张数过多时自动分册。为了防止误覆盖，准备与归档过程在原目的地已存在结果时会拒绝写入，改用新的结果目录即可。

## 四、目录布局

```text
portrait-photo-curator/
├── SKILL.md
├── README.md
├── requirements.txt
├── agents/openai.yaml
├── references/
│   ├── photography-rubric.md
│   ├── review-format.md
│   └── xingtu-playbook.md
└── scripts/
    ├── photo_workflow.py
    └── selftest.py
```

**局限**：是否真的具备 Codex 图像查看能力取决于当前 Codex Desktop 的工具和图片格式支持。脚本不提供视觉审片模型，也不会把原照片发送给任何远端 API。若看图功能不可用则只能建立目录/预览，不能正确自动分级。部分 RAW 可能因解码支持程度不同而不能生成预览，程序会报告失败而不是省略。对于闭眼和失焦，需要人工或视觉模型通过大图确认。

## 五、快速技术自测

```bash
python3 ~/.agents/skills/portrait-photo-curator/scripts/selftest.py
```

自测只用**程序生成的三张几何测试图**验证预览、JSON 约束、哈希复制和 Word 生成；不代表 Skill 已在真实人像上完成审美测试。
