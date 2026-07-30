# Exp1 实验记录

## 实验索引

| 编号 | 日期 | 摘要 | 状态 | Task ID | checkpoint |
|------|------|------|------|---------|------------|
| exp0 | 2026-07-29 | RPO-Flat 基线训练，9001轮，训练日志趋势分析 | 训练中 | TASK_20260729_127 | - |
| exp1 | 2026-07-30 | 3001轮基线训练，max_iterations=3001，确保配置已推送 | 待训练 | - | - |

---

## 实验 exp0：RPO-Flat 基线训练

### 1. 上一实验结果与教训

> 本轮为 exp1 系列首个实验，无上一轮数据。
> 基于 `roboparty_train` 上游仓库默认 RPO-Flat 配置直接开训，作为基线。

### 2. 本轮修改目标

- 获取 RPO-Flat 基线训练数据，了解默认配置下训练曲线走势
- 通过训练日志初步评估各奖励项收敛情况
- 为后续实验提供对照基线

### 3. 修改内容

无修改，使用上游仓库默认配置。

### 4. 修改文件

无。

> **注意**：本地修改了 `rpo_agent_cfg.py`（max_iterations 9001→3001, save_interval 1000→100），但未提交推送，远程仓库仍为旧配置。实际训练使用的是远程仓库的旧配置。

### 5. 训练参数

| 参数 | 期望值 | 实际运行值 | 说明 |
|------|--------|-----------|------|
| 训练方式 | 从零 | 从零 | |
| max_iterations | 3001 | **9001** | 本地修改未推送 |
| save_interval | 100 | **1000** | 本地修改未推送 |
| num_envs | 8192 | 8192 | |
| num_steps_per_env | 24 | 24 | |
| seed | 42 | 42 | |
| learning_rate | 1.0e-3 | 1.0e-3 | |
| schedule | adaptive | adaptive | |
| gamma | 0.99 | 0.99 | |
| lam | 0.95 | 0.95 | |
| entropy_coef | 0.005 | 0.005 | |
| clip_param | 0.2 | 0.2 | |
| desired_kl | 0.01 | 0.01 | |
| num_learning_epochs | 5 | 5 | |
| num_mini_batches | 4 | 4 | |
| max_grad_norm | 1.0 | 1.0 | |
| symmetry_cfg | None | None | Flat 不启用对称 |
| clip_actions | 100.0 | 100.0 | |
| 算力 | 1×4090D 24G | 1×4090D 24G | ESKU000001, ¥5.40/h |
| 镜像 | IsaacSim:5.1 \| IsaacLab:2.3.2 | 同左 | BJX00000178, V000220 |
| 代码仓库 | lab_test.git, exp1 分支 | 同左 | commit f4a5e1d |
| 启动命令 | - | `gm-run lab_test/robolab/scripts/rsl_rl/train.py --task=RPO-Flat --headless --logger=tensorboard --num_envs=8192` | |

### 6. 预期与验收

> 本轮为基线训练，无量化目标。通过训练日志趋势判断训练是否正常收敛。

**关注指标**（训练日志）：

| 指标 | 异常信号 |
|------|---------|
| Mean reward | 持续下降或停滞 |
| Mean episode length | 不增长或下降 |
| track_lin_vel_xy_exp | 不增长 |
| track_ang_vel_z_exp | 不增长 |
| action_noise_std | 不下降 |
| entropy_loss | 不下降 |
| termination_penalty | 持续 -0.20 不改善 |

### 7. 实验结果

> 训练进行中，以下为截至 iter ~311/9001（约 11.5 分钟）的训练日志分析。

#### 训练进度趋势（iter 220 → 311）

| 指标 | iter ~220 | iter ~311 | 趋势 | 判定 |
|------|-----------|-----------|------|------|
| Mean reward | -5.12 | -4.74 | ↑ | ✅ 改善 |
| Mean episode length | 66.5 | 108.7 | ↑ 1.6× | ✅ 显著改善 |
| track_lin_vel_xy_exp | 0.0186 | 0.0530 | ↑ 2.8× | ✅ 显著改善 |
| track_ang_vel_z_exp | 0.0155 | 0.0374 | ↑ 2.4× | ✅ 显著改善 |
| upward | 0.0234 | 0.0544 | ↑ 2.3× | ✅ 显著改善 |
| feet_distance | 0.0066 | 0.0140 | ↑ 2.1× | ✅ 改善 |
| knee_distance | 0.0066 | 0.0134 | ↑ 2.0× | ✅ 改善 |
| feet_height | 0.0044 | 0.0059 | ↑ | ✅ 略有改善 |
| action_noise_std | 0.45 | 0.40 | ↓ | ✅ 策略收敛中 |
| entropy_loss | 14.40 | 11.61 | ↓ | ✅ 策略收敛中 |
| termination_penalty | -0.2000 | -0.1882 | ↑ | ⚠️ 略有改善但仍高 |
| feet_slide | -0.0068 | -0.0122 | ↓ | ⚠️ 恶化（滑动增加） |
| action_smoothness | -0.0280 | -0.0530 | ↓ | ⚠️ 恶化（平滑度下降） |
| joint_deviation_torso | -0.0253 | -0.0489 | ↓ | ⚠️ 恶化（躯干偏移增大） |
| feet_force | -0.0019 | -0.0049 | ↓ | ⚠️ 恶化（地面冲击增大） |
| Computation | ~92k steps/s | ~84k steps/s | → | 稳定，~2.1-2.4s/iter |

#### 分析

**积极信号**：
1. **奖励持续上升**：Mean reward 从 -5.12 升至 -4.74，机器人正在学习有用行为
2. **存活时间显著增加**：Episode length 从 66 增至 109-157（1.6×-2.4×），机器人摔倒频率降低
3. **速度跟踪能力提升**：lin_vel 跟踪提升 2.8×，ang_vel 跟踪提升 2.4×，核心任务目标在改善
4. **策略收敛**：action_noise_std 从 0.45 降至 0.40，entropy 从 14.4 降至 11.6，策略逐渐确定性化
5. **直立奖励提升**：upward 提升 2.3×，机器人正在学习保持直立

**需关注的问题**：
1. **termination_penalty 仍高**（-0.188）：尽管有改善，机器人仍频繁终止，说明还不够稳定
2. **feet_slide 恶化**：滑动惩罚从 -0.0068 增至 -0.0122，可能是在学习过程中脚部拖地
3. **action_smoothness 恶化**：动作平滑度下降，可能因为策略还在探索阶段
4. **joint_deviation_torso 恶化**：躯干关节偏移增大，可能是为保持平衡而过度扭动躯干
5. **feet_force 恶化**：地面冲击力增大，可能与更激进的动作有关

**局限**：
- 仅有训练日志数据，无法进行 isaac-diag-eval 诊断分析（需 CSV 数据）
- 训练未完成，最终收敛状态未知
- 远程仓库配置与本地不一致（max_iterations 9001 vs 3001）

**结论**：⚠️ 部分改善 -- 核心指标（reward、episode length、velocity tracking）趋势良好，但部分惩罚项（feet_slide、action_smoothness、torso deviation）在恶化，需关注后续训练是否趋于稳定。

**下一轮方向**：
- 等待训练完成后，下载 checkpoint 并运行 isaac-diag-eval 进行完整诊断
- 若 feet_slide 持续恶化，考虑增大 feet_slide 惩罚权重
- 若 joint_deviation_torso 不收敛，考虑增大 torso 偏移惩罚
- 下次创建任务前确保本地修改已 commit 并 push 到远程仓库

---

## 实验 exp1：3001轮基线训练

### 1. 上一实验结果与教训

> 数据：exp0 训练日志（截至 iter ~311/9001）
> - Mean reward: -4.74（iter 311），趋势上升但绝对值远低于目标 25
> - Mean episode length: 108.7（iter 311），目标 900
> - termination_penalty: -0.1882，机器人仍频繁摔倒
> - feet_slide / action_smoothness / joint_deviation_torso 均在恶化
>
> **核心教训**：
> - exp0 因本地修改未推送，实际使用旧配置（max_iterations=9001, save_interval=1000），无法精确评估 3000 轮时的表现
> - 核心指标（reward、episode length）趋势良好，但距离目标差距巨大
> - 本轮需确保配置正确推送，用 max_iterations=3001 精确评估 3000 轮训练效果

### 2. 本轮修改目标

- 确保 max_iterations=3001、save_interval=10 的配置正确推送到远程仓库
- 获取 3000 轮训练的完整结果数据
- 验收标准：Mean reward ≥ 25，Mean episode length ≥ 900
- 若不达标，分析原因并为下一轮优化提供方向

### 3. 修改内容

### 修改一：训练轮数和保存间隔

| 参数 | 旧值 | 新值 | 说明 |
|------|------|------|------|
| max_iterations | 9001（exp0实际值） | 3001 | 目标评估 3000 轮效果 |
| save_interval | 1000（exp0实际值） | 10 | 每 10 轮保存 checkpoint，便于精细追踪 |

**理由**：exp0 因配置未推送导致实际训练参数与预期不符。本轮确保配置正确推送，精确评估 3000 轮训练效果。

### 4. 修改文件

- `robolab/robolab/tasks/direct/base/agents/rpo_agent_cfg.py`：max_iterations 301→3001，save_interval 保持 10

### 5. 训练参数

| 参数 | 值 |
|------|-----|
| 训练方式 | 从零 |
| max_iterations | 3001 |
| save_interval | 10 |
| num_envs | 8192 |
| num_steps_per_env | 24 |
| seed | 42 |
| learning_rate | 1.0e-3 |
| schedule | adaptive |
| gamma | 0.99 |
| lam | 0.95 |
| entropy_coef | 0.005 |
| clip_param | 0.2 |
| desired_kl | 0.01 |
| num_learning_epochs | 5 |
| num_mini_batches | 4 |
| symmetry_cfg | None（Flat 不启用对称） |
| clip_actions | 100.0 |
| 算力 | 1×4090D 24G，ESKU000001 |
| 镜像 | BJX00000178, V000220 (IsaacSim:5.1 \| IsaacLab:2.3.2) |
| 代码仓库 | lab_test.git, x1_29 分支 |
| 启动命令 | `gm-run lab_test/robolab/scripts/rsl_rl/train.py --task=RPO-Flat --headless --logger=tensorboard --num_envs=8192` |

### 6. 预期与验收

**目标指标**（3000 轮时）：

| 指标 | exp0 (iter 311) | exp1 目标 | 异常信号 |
|------|-----------------|-----------|---------|
| Mean reward | -4.74 | ≥ 25 | < 10 |
| Mean episode length | 108.7 | ≥ 900 | < 500 |
| track_lin_vel_xy_exp | 0.0530 | > 0.5 | < 0.2 |
| track_ang_vel_z_exp | 0.0374 | > 0.5 | < 0.2 |
| termination_penalty | -0.1882 | > -0.05 | < -0.10 |
| action_noise_std | 0.40 | < 0.3 | > 0.5 |

**关注指标**（训练日志趋势）：

| 指标 | 异常信号 |
|------|---------|
| Mean reward | 停滞或下降 |
| Mean episode length | 不增长 |
| termination_penalty | 持续高位不改善 |
| feet_slide | 持续恶化 |

### 7. 实验结果

> 待训练完成后补充。
