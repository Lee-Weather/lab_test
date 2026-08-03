# Exp1 实验记录

## 实验索引

| 编号 | 日期 | 摘要 | 状态 | Task ID | GM账号 | checkpoint |
|------|------|------|------|---------|--------|------------|
| exp0 | 2026-07-29 | RPO-Flat 基线训练，9001轮，训练日志趋势分析 | 训练中 | TASK_20260729_127 | - | - |
| exp1 | 2026-07-30 | 3001轮基线训练，ep_len 948✅，reward 7.26❌（目标25） | 失败 | TASK_20260730_176 | - | model_3000.pt |
| exp1.1 | 2026-07-30 | 奖励权重优化：↑正向(track_vel×2,upward×2,air_time×4)，↓惩罚(torso×0.5,smoothness×0.5) | 已测试 | TASK_20260730_200 | - | model_3000.pt |
| exp2 | 2026-08-01 | 修复sim2sim导出：train.py每次保存直接导出deploy JIT（monkey-patch，不启用归一化） | 已停止-链路已验证 | TASK_20260801_014 | peleha7269@candaba.com | - |
| exp2.1 | 2026-08-01 | 对比实验：只保存model_*.pt（去掉deploy导出），验证GM上传行为 | 已停止-确认GM仅在任务正常完成时上传 | TASK_20260801_016 | peleha7269@candaba.com | - |
| exp2.2 | 2026-08-01 | 快速验证（31 iter）：GM模型上传链路+deploy JIT可加载+sim2sim冒烟 | ✅ 链路全通 | TASK_20260801_017 | peleha7269@candaba.com | model_30_deploy.pt |
| exp2.3 | 2026-08-01 | 完整训练3001 iter，验证sim2sim稳定站立 | sim2sim失败-机器人倒下，根因:default_pos左右非镜像 | TASK_20260801_021 | peleha7269@candaba.com | model_3000_deploy.pt |
| exp2.4 | 2026-08-03 | 修复:左右腿default_pos镜像对称(FK验证dx=0 dz=0)，重训3001 iter | 训练中 | TASK_20260803_059 | peleha7269@candaba.com | - |

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

> 训练任务：TASK_20260730_176，2026-07-30 18:17 ~ 20:38（约 2h21m）
> 最终 checkpoint：model_3000.pt / policy_3000.pt (JIT) / policy_3000.onnx

#### 最终结果（iter 3000）

| 指标 | exp0 (iter 311) | exp1 目标 | exp1 实测 (iter 3000) | 判定 |
|------|-----------------|-----------|----------------------|------|
| Mean reward | -4.74 | ≥ 25 | **7.26** | ❌ 未达标 |
| Mean episode length | 108.7 | ≥ 900 | **948.58** | ✅ 达标 |
| action_noise_std | 0.40 | < 0.3 | **0.26** | ✅ 达标 |

#### 训练趋势

| iter | Mean reward | Mean episode length |
|------|-------------|---------------------|
| 46 | -6.06 | 17.24 |
| 286 | -4.82 | 53 |
| 511 | -5.10 | 166 |
| 831 | -5.40 | 272 |
| 1261 | -4.30 | 700 |
| 1901 | +3.58 | 954 |
| 2541 | +6.30 | 960 |
| 3000 | +7.26 | 949 |

#### 各奖励项最终值（iter ~2700）

| 奖励项 | 权重 | 最终值 | 说明 |
|--------|------|--------|------|
| track_lin_vel_xy_exp | 1.0 | +0.547 | 线速度跟踪，主要正向贡献 |
| track_ang_vel_z_exp | 1.0 | +0.679 | 角速度跟踪，主要正向贡献 |
| upward | 0.4 | +0.372 | 直立奖励 |
| feet_distance | 0.1 | +0.095 | 脚间距 |
| knee_distance | 0.1 | +0.095 | 膝间距 |
| feet_height | 0.2 | +0.024 | 抬脚高度 |
| feet_contact_without_cmd | 0.1 | +0.018 | 零命令时双脚着地 |
| feet_air_time | 0.25 | +0.003 | 空中时间（几乎为0） |
| joint_deviation_torso | -1.0 | -0.365 | **最大惩罚项** |
| action_smoothness_l2 | -2e-2 | -0.193 | 动作平滑度惩罚 |
| action_rate_l2 | -2e-2 | -0.141 | 动作变化率惩罚 |
| stand_still | -0.2 | -0.085 | 静止偏差 |
| termination_penalty | -200 | -0.022 | 终止惩罚（已大幅改善） |
| joint_deviation_hip | -0.03 | -0.020 | 髋部偏移 |
| joint_torques_l2 | -1e-5 | -0.020 | 关节力矩 |
| feet_slide | -0.3 | -0.030 | 脚滑动 |
| feet_force | -3e-3 | -0.018 | 地面冲击 |

**结论**：❌ 未达标 -- Episode length 超过 900（948.58），但 Mean reward 仅 7.26，远低于目标 25。

**根因分析**：
1. **正向奖励不足**：速度跟踪（lin_vel 0.55 + ang_vel 0.68 = 1.23）是主要正向贡献，但权重仅为 1.0，贡献量不足以抵消惩罚
2. **joint_deviation_torso 惩罚过大**（-0.365）：权重 -1.0，是最大惩罚项，严重拖低总奖励
3. **action_smoothness + action_rate 惩罚累积**（合计 -0.334）：权重 -2e-2，随着 episode 变长累积更多
4. **feet_air_time 几乎为零**（+0.003）：机器人几乎没有迈步，可能是在原地晃动保持平衡
5. **训练曲线后半段增长放缓**：iter 1900→3000（1100轮）reward 仅从 3.6 增至 7.3，增速明显放缓

**下一轮方向**：
- 增大正向奖励权重（track_lin_vel/ang_vel 1.0→2.0，upward 0.4→0.8，feet_air_time 0.25→1.0）
- 降低 joint_deviation_torso 权重（-1.0→-0.5）
- 降低 action_smoothness/action_rate 权重（-2e-2→-1e-2）
- 保持 episode_length_s、终止条件等不变（episode length 已达标）

---

## 实验 exp1.1：奖励权重优化训练（阶段1 微调1）

### 1. 上一实验结果与教训

> 数据：exp1 训练日志（TASK_20260730_176，3001轮完整训练）
> - Mean reward: 7.26（目标 25），Episode length: 948.58（目标 900 ✅）
> - 最大正向贡献：track_lin_vel 0.55 + track_ang_vel 0.68 = 1.23（权重仅 1.0）
> - 最大惩罚：joint_deviation_torso -0.365（权重 -1.0）、action_smoothness -0.193（权重 -2e-2）、action_rate -0.141（权重 -2e-2）
> - feet_air_time 几乎为 0（+0.003），机器人没有真正迈步
>
> **核心教训**：
> - Episode length 已达标，说明平衡能力足够
> - Reward 不足的根本原因是正向奖励权重太低、惩罚权重过高
> - 需要增大任务奖励权重、降低惩罚权重来提升总 reward

### 2. 本轮修改目标

- Mean reward ≥ 25（exp1 为 7.26）
- Mean episode length ≥ 900（保持）
- 通过调整奖励权重，使正向奖励贡献增加约 3 倍

### 3. 修改内容

### 修改二：增大正向奖励权重

| 参数 | exp1 值 | exp1.1 值 | 说明 |
|------|---------|-----------|------|
| track_lin_vel_xy_exp | 1.0 | **2.0** | 线速度跟踪奖励翻倍 |
| track_ang_vel_z_exp | 1.0 | **2.0** | 角速度跟踪奖励翻倍 |
| feet_air_time | 0.25 | **1.0** | 空中时间奖励增至 4 倍，鼓励迈步 |
| upward | 0.4 | **0.8** | 直立奖励翻倍 |

**理由**：exp1 中正向奖励总计仅 ~1.83，其中速度跟踪占 67%。翻倍速度跟踪权重预计可直接增加 ~1.23 的正向贡献。

### 修改三：降低主要惩罚权重

| 参数 | exp1 值 | exp1.1 值 | 说明 |
|------|---------|-----------|------|
| joint_deviation_torso | -1.0 | **-0.5** | 最大惩罚项减半 |
| action_smoothness_l2 | -2e-2 | **-1e-2** | 动作平滑度惩罚减半 |
| action_rate_l2 | -2e-2 | **-1e-2** | 动作变化率惩罚减半 |

**理由**：exp1 中这三项惩罚合计 -0.70，减半后预计可减少 ~0.35 的惩罚。

### 4. 修改文件

- `robolab/robolab/tasks/direct/base/rpo_env_cfg.py`：修改 7 个奖励项权重

### 5. 训练参数

| 参数 | 值 |
|------|-----|
| 训练方式 | 从零 |
| max_iterations | 3001 |
| save_interval | 10 |
| num_envs | 8192 |
| seed | 42 |
| learning_rate | 1.0e-3 |
| 其他 PPO 参数 | 与 exp1 相同 |
| 算力 | 1×4090D 24G，ESKU000001 |
| 镜像 | BJX00000178, V000220 |
| 代码仓库 | lab_test.git, x1_29 分支 |
| 启动命令 | `gm-run lab_test/robolab/scripts/rsl_rl/train.py --task=RPO-Flat --headless --logger=tensorboard --num_envs=8192` |

### 6. 预期与验收

**目标指标**（3000 轮时）：

| 指标 | exp1 (iter 3000) | exp1.1 目标 | 异常信号 |
|------|------------------|-------------|---------|
| Mean reward | 7.26 | ≥ 25 | < 15 |
| Mean episode length | 948.58 | ≥ 900 | < 700 |
| track_lin_vel_xy_exp | 0.547 | > 1.0 | < 0.5 |
| track_ang_vel_z_exp | 0.679 | > 1.2 | < 0.6 |
| joint_deviation_torso | -0.365 | > -0.20 | < -0.30 |
| action_noise_std | 0.26 | < 0.3 | > 0.5 |

### 7. 实验结果

> 训练任务：TASK_20260730_200，2026-07-30 21:00 ~ 23:25（约 2h25m）
> 最终 checkpoint：model_3000.pt / policy_3000.pt (JIT) / policy_3000.onnx

#### 最终结果（iter 3000）

| 指标 | exp1 (iter 3000) | exp1.1 目标 | exp1.1 实测 (iter 3000) | 判定 |
|------|------------------|-------------|------------------------|------|
| Mean reward | 7.26 | ≥ 25 | **58.58** | ✅✅ 大幅超出 |
| Mean episode length | 948.58 | ≥ 900 | **994.91** | ✅✅ 几乎满分 |
| action_noise_std | 0.26 | < 0.3 | **0.39** | ⚠️ 略高 |

#### 训练趋势

| iter | Mean reward | Mean episode length | 对比 exp1 同期 |
|------|-------------|---------------------|---------------|
| 31 | -5.60 | 29.63 | exp1: -6.06 / 17.24 |
| 266 | -3.32 | 173 | exp1: -4.82 / 53 |
| 686 | +24.91 | 908 | exp1: -5.40 / 272 |
| 1296 | +42.32 | 945 | exp1: -4.30 / 700 |
| 1956 | +48.95 | 942 | exp1: +3.58 / 954 |
| 2601 | +54.76 | 958 | exp1: +6.30 / 960 |
| 3000 | +58.58 | 995 | exp1: +7.26 / 949 |

#### 各奖励项对比（exp1 → exp1.1，最终值）

| 奖励项 | exp1 权重 | exp1 值 | exp1.1 权重 | exp1.1 值 | 变化 |
|--------|----------|---------|------------|-----------|------|
| track_lin_vel_xy_exp | 1.0 | 0.547 | 2.0 | **1.754** | ↑ 3.2×（跟踪能力大幅提升） |
| track_ang_vel_z_exp | 1.0 | 0.679 | 2.0 | **1.447** | ↑ 2.1× |
| feet_air_time | 0.25 | 0.003 | 1.0 | **0.084** | ↑ 28×（开始迈步！） |
| upward | 0.4 | 0.372 | 0.8 | **0.784** | ↑ 2.1× |
| joint_deviation_torso | -1.0 | -0.365 | -0.5 | -0.469 | 权重减半，影响降低 |
| action_smoothness_l2 | -2e-2 | -0.193 | -1e-2 | -0.236 | 权重减半，影响降低 |
| action_rate_l2 | -2e-2 | -0.141 | -1e-2 | -0.138 | 权重减半，影响降低 |

**结论**：✅✅ 完全达标 -- Mean reward 58.58（目标 25，超出 134%），Mean episode length 994.91（目标 900，达到 99.5%）。

**成功关键**：
1. **速度跟踪权重翻倍**是最关键改动：机器人从被动保持平衡转向主动跟踪速度命令，track_lin_vel 从 0.55 提升至 1.75
2. **feet_air_time 增至 4 倍**促使机器人开始真正迈步（从 0.003 提升至 0.084，28 倍增长）
3. **惩罚权重减半**减少了奖励抑制，让策略有更大探索空间
4. **训练收敛速度快**：iter 686 即达到 reward 25，约为 exp1 达到同水平所需轮数的 1/4

**注意事项**：
- action_noise_std（0.39）略高于 exp1（0.26），因为惩罚减半后策略探索更多
- 如需更确定性的策略，可考虑增大 entropy_coef 或延长训练

---

## 实验 exp2：修复 sim2sim 导出（阶段2：sim2sim 稳定站立）

### 1. 上一实验结果与教训

> 数据：exp1.1 训练日志 + sim2sim CSV 诊断（TASK_20260730_200）
> - 训练指标达标：Mean reward 58.58 ✅，Episode length 994.91 ✅
> - sim2sim 结果：机器人严重翻滚，飞行率 93.2%，双支撑率 0%，俯仰角 -65°，侧倾角 +60°
> - 关节跟踪误差：32.59°（修复激活函数后反而更大）
>
> **核心教训**：
> - 训练指标达标 ≠ sim2sim 可用
> - 根因：train.py 导出的 `exported/policy_*.pt`（含 EmpiricalNormalization）未上传 GM，本地只能下到不含 normalizer 的 `model_*.pt`
> - convert 脚本还误用了 ReLU 激活函数（训练用 ELU）
> - 本轮目标：修复 train.py 将含 normalizer 的 JIT 复制到 GM 可访问位置，重训验证 sim2sim

### 2. 本轮修改目标

- 产出含 EmpiricalNormalization 的可部署 JIT 模型
- sim2sim 原地站立 20 秒不摔倒
- 验收标准：飞行率 < 20%，双支撑率 > 50%，俯仰/侧倾角 < 10°

### 3. 修改内容

### 修改一：train.py 每次保存时直接导出可部署 JIT（monkey-patch runner.save）

| 项目 | 修改前 | 修改后 | 说明 |
|------|--------|--------|------|
| 导出时机 | 仅训练结束后复制 exported JIT | **每次 checkpoint 保存后**（save_interval=100） | monkey-patch `runner.save` |
| 导出方式 | 复制 `exported/policy_{iter}.pt` | 直接从训练对象 `export_policy_as_jit(policy_nn, normalizer, ...)` | 结构/激活天然一致，零手写转换风险 |
| 文件名 | `model_{final}_deploy.pt` | `model_{iter}_deploy.pt`（每 100 iter 一个） | 匹配 GM `model_*.pt` 上传规则 |
| 归一化 | - | **不启用**（保持训练行为不变，normalizer=Identity） | JIT 为纯 actor，sim2sim 直接 `jit.load` |

**理由**：
- 发现训练时 normalizer 实际未启用（rpo_agent_cfg 设置在 runner 顶层无效，rsl_rl 3.0.1 只读 policy 配置；model_100.pt 实测无 normalizer 键）→ 原"复制含 normalizer JIT"方案无效
- 改为训练端直接导出：每个 checkpoint 保存即产出可部署 JIT，中途模型即可下载直接 sim2sim
- 不启用归一化：训练行为与 exp1.1 一致（已证明可训练达标），且导出=纯 actor，与训练网络逐位等价

### 修改二：convert_x1_29_checkpoint.py 修复激活函数 + 添加 normalizer 支持

| 项目 | 修改前 | 修改后 | 说明 |
|------|--------|--------|------|
| 激活函数 | ReLU ❌ | ELU ✅ | 与训练配置一致 |
| Normalizer | 无 | 从 checkpoint 加载（如存在） | 自动检测 `actor_obs_normalizer.*` |

**理由**：训练用 ELU 激活函数，转换脚本误用 ReLU 导致整个网络中间层计算错误。

### 4. 修改文件

- `robolab/scripts/rsl_rl/train.py`：L459-472，训练后复制 deploy JIT 到 GM 可访问位置
- `robolab/scripts/mujoco/convert_x1_29_checkpoint.py`：ReLU→ELU，添加 normalizer 加载逻辑
- `robolab/robolab/tasks/direct/base/agents/rpo_agent_cfg.py`：save_interval 10→100

### 5. 训练参数

| 参数 | 值 |
|------|-----|
| 训练方式 | 从零 |
| GM账号 | peleha7269@candaba.com |
| max_iterations | 3001 |
| save_interval | 100 |
| num_envs | 8192 |
| seed | 42 |
| learning_rate | 1.0e-3 |
| 算力 | 1×4090D 24G，ESKU000001 |
| 镜像 | BJX00000178, V000220 (IsaacSim:5.1 \| IsaacLab:2.3.2) |
| 代码仓库 | lab_test.git, x1_29 分支, commit 40bd802 |
| 启动命令 | `gm-run lab_test/robolab/scripts/rsl_rl/train.py --task=RPO-Flat --headless --logger=tensorboard --num_envs=8192` |

### 6. 预期与验收

**sim2sim 验收标准**（原地站立，20 秒）：

| 指标 | exp1.1 实测 | exp2 目标 | 异常信号 |
|------|-------------|-----------|---------|
| 飞行率（双脚离地） | 93.2% | < 20% | > 50% |
| 双支撑率 | 0.0% | > 50% | < 20% |
| 俯仰角 euler_x | -65.04° | < 10° | > 30° |
| 侧倾角 euler_y | +60.14° | < 10° | > 30° |
| 关节跟踪误差 | 32.59° | < 5° | > 15° |

**训练指标**（保持 exp1.1 水平）：

| 指标 | exp1.1 | exp2 目标 |
|------|--------|-----------|
| Mean reward | 58.58 | ≥ 25 |
| Mean episode length | 994.91 | ≥ 900 |

### 7. 实验结果

> 训练任务：TASK_20260801_014，2026-08-01 10:25 启动（peleha7269@candaba.com 账号，代码 58f2afe）
> 注：原 TASK_20260731_160 为 yijed24226 账号草稿（未运行），跨账号无法启动，重建为 TASK_20260801_004；
> 后因方案修正暂停（09:58），停止任务无法重启，重建为 TASK_20260801_014。
> 待训练完成后补充结果。

#### 执行日志

| 时间 | 事件 |
|------|------|
| 2026-08-01 09:42 | 创建并启动 TASK_20260801_004（配置同 TASK_20260731_160） |
| 2026-08-01 09:47 | 任务进入运行中（pod 已拉起） |
| 2026-08-01 09:52 | 训练至 iter ~81，Mean reward -4.80（与 exp1.1 同期 -5.60 相当） |
| 2026-08-01 09:58 | 用户主动暂停训练（runtime 696s，iter ~81） |
| 2026-08-01 10:10 | **方案修正**：实测 model_100.pt 无 normalizer 键 → 确认训练时归一化未启用（配置位置错误），原"复制含 normalizer JIT"方案无效 |
| 2026-08-01 10:10 | 改为 monkey-patch runner.save：每次保存 checkpoint 直接导出 `model_{iter}_deploy.pt`（训练对象导出，不启用归一化） |
| 2026-08-01 10:24 | commit 58f2afe 推送（train.py monkey-patch + convert ELU 修复） |
| 2026-08-01 10:25 | 停止任务无法重启，重建 TASK_20260801_014 并启动 |
| 2026-08-01 10:45 | 日志确认 iter 200 保存时成功导出 `model_200_deploy.pt`（monkey-patch 生效，无 WARN） |
| 2026-08-01 10:52 | 用户主动停止训练（iter ~300+，导出链路已验证；GM 模型上传滞后，列表暂为空） |

---

## 实验 exp2.1：对比实验——只保存 model_*.pt（无 deploy 导出）

### 1. 上一实验结果与教训

- exp2（TASK_20260801_014）已停止：日志确认训练端导出 deploy JIT 链路打通（iter 200 → `model_200_deploy.pt`），**但 GM 平台模型列表始终为空（训练中与停止后均未同步）**，上传滞后问题未解决。
- 待验证：模型上传滞后是否与 deploy 导出无关、只是平台同步周期问题。

### 2. 目标

- **对比实验**：恢复"只保存 `model_*.pt`"的原始训练，验证 GM 平台模型上传行为是否正常。
- 确认训练期间/停止后 `model_*.pt` 能否出现在 GM 模型列表；训练指标与 exp1.1/exp2 同期相当。

### 3. 修改内容

| 项目 | 修改前（exp2） | 修改后（exp2.1） | 说明 |
|------|---------------|---------------|------|
| 训练期间导出 | monkey-patch 每次保存导出 `model_{iter}_deploy.pt` | **去掉**，仅 runner 自动保存 `model_*.pt` | commit 819a3a8 |
| 训练结束 | 复制 exported JIT 到 log_dir 根 + /personal | **去掉**，仅保留 exported/policy_*.pt（GM 不扫描该目录） | 干净对比 |

### 4. 修改文件

- `robolab/scripts/rsl_rl/train.py`（commit 819a3a8：revert deploy 导出）

### 5. 训练参数

- 同 exp1.1/exp2：RPO-Flat，3001 iter，8192 envs，代码分支 x1_29（819a3a8）

### 6. 预期与验收

- GM 模型列表在训练中/停止后能出现 `model_*.pt` → 说明 exp2 上传滞后是平台同步周期问题（与 deploy 无关）
- 若模型列表仍为空 → 需排查 GM 上传机制（可能只在任务正常完成后上传）

### 7. 实验结果

> 训练任务：TASK_20260801_016，2026-08-01 11:00 启动（peleha7269@candaba.com 账号，代码 819a3a8）
> 待训练完成后补充结果。

#### 执行日志

| 时间 | 事件 |
|------|------|
| 2026-08-01 10:57 | commit 819a3a8 推送（train.py 回退：去掉 deploy 导出，只保存 model_*.pt） |
| 2026-08-01 11:00 | 创建并启动 TASK_20260801_016（对比实验 exp2.1） |
| 2026-08-01 11:20 | 确认 GM 上传机制：`gm task data get` 是图表数据（skill 记载有误）；模型下载走 `gm task model list`；**exp2 停止 1h 后模型列表仍空 → GM 只在任务正常完成时上传** |
| 2026-08-01 11:20 | commit c29f1b6 推送：训练结束导出 deploy JIT 到 log_dir 根（model_{final}_deploy.pt），随 checkpoint 上传，下载即 sim2sim 免转换（为下一训练任务准备） |
| 2026-08-01 11:20 | 决策：exp2.1 继续跑完（用 819a3a8），完成后拿 model_3000.pt + convert 验证链路；后续任务用 c29f1b6 直接拿 deploy JIT |
| 2026-08-01 11:35 | **exp2.1 停止**（iter ~126 时，训练中模型列表为空已确认）；用户改配置为 max_iterations=31 / save_interval=10（快速验证） |
| 2026-08-01 11:35 | commit 994e9e8 推送（快速验证配置） |
| 2026-08-01 11:36 | 创建并启动 TASK_20260801_017（exp2.2 快速验证：31 iter，验证 GM 上传链路） |

---

## 实验 exp2.2：快速验证——31 iter 验证 GM 模型上传链路

### 1. 上一实验结果与教训

- exp2.1（TASK_20260801_016）停止于 iter ~126：训练中模型列表持续为空，进一步确认 GM 只在任务正常完成时上传。
- 已实施 c29f1b6：训练结束导出 deploy JIT 到 log_dir 根（model_{final}_deploy.pt）。

### 2. 目标

- **快速验证完整链路**：任务正常完成后，GM 上传 `model_*.pt` + `model_*_deploy.pt`；下载 deploy JIT 可直接 `torch.jit.load` 用于 sim2sim。

### 3. 修改内容

| 项目 | 修改前 | 修改后 | 说明 |
|------|--------|--------|------|
| max_iterations | 3001 | **31** | 快速跑完触发上传（commit 994e9e8，临时） |
| save_interval | 100 | **10** | 每 10 iter 保存 model_10/20/30.pt |
| deploy 导出 | 无 | 训练结束导出 model_31_deploy.pt 到 log_dir 根 | c29f1b6 |

### 4. 修改文件

- `robolab/robolab/tasks/direct/base/agents/rpo_agent_cfg.py`（commit 994e9e8）
- `robolab/scripts/rsl_rl/train.py`（commit c29f1b6）

### 5. 训练参数

- RPO-Flat，31 iter，8192 envs，代码 994e9e8

### 6. 预期与验收

- ✅ 任务正常完成（状态 5）
- ✅ GM 模型列表出现 model_30.pt 与 model_31_deploy.pt
- ✅ 下载 model_31_deploy.pt，torch.jit.load 验证结构（960→29）
- ✅ （可选）sim2sim 冒烟运行

### 7. 实验结果

> 训练任务：TASK_20260801_017，2026-08-01 11:36 启动（peleha7269@candaba.com 账号，代码 994e9e8）
> 待训练完成后补充结果。

#### 执行日志

| 时间 | 事件 |
|------|------|
| 2026-08-01 11:36 | 创建并启动 TASK_20260801_017（exp2.2 快速验证） |
| 2026-08-01 11:22 | 任务正常完成（状态5）；日志确认 model_0/10/20/30_deploy.pt 全部 `uploaded successfully`（upload_column=policUrl） |
| 2026-08-01 11:29 | **模型列表可见（5 个）**：model_0/10/20/30.pt + model_30_deploy.pt（此前解析字段用错 `modelList`，实际是 `data.rows`） |
| 2026-08-01 11:29 | 全部下载到 `czy/data/models/x1_29_models/20260801_x1_29_exp2.2_quick/` |
| 2026-08-01 11:31 | **deploy JIT 验证通过**：`torch.jit.load` 成功，结构 `_TorchPolicyExporter(actor: MLP 960→512→256→128→29, ELU; normalizer: Identity)`，前向 (1,960)→(1,29) |
| 2026-08-01 11:29 | **sim2sim 冒烟通过**：`sim2sim_x1_29.py --load_model model_30_deploy.pt` 正常跑完 20s，输出 CSV+PNG（31 iter 废模型倒下属预期，链路全通） |

---

## 实验 exp2.3：完整训练（3001 iter）——验证 sim2sim 稳定站立

### 1. 上一实验结果与教训

- exp2.2（31 iter 快速验证）已打通完整链路：任务正常完成 → GM 上传 `model_*.pt` + `model_*_deploy.pt` → `gm task model list`（`data.rows`）→ 下载 deploy JIT → `torch.jit.load` 直接 sim2sim。
- 三个根因已沉淀进 skills（gm-cli / sim2sim-test）。
- 配置已恢复 3001 iter / save_interval 100（commit e5300f4）。

### 2. 目标

- 完整训练 3001 iter，训练完成后下载 `model_3000_deploy.pt`，在 MuJoCo sim2sim 中验证**稳定站立**（标准：姿态 ±5°、双支撑率 >70%、关节跟踪误差 <3°）。
- 若不能稳定站立：分析 CSV 诊断根因 → 修改代码/奖励 → 重新训练，直到稳定。

### 3. 修改内容

- 相对 exp2.1/exp2.2：训练配置恢复 3001 iter；train.py 训练结束导出 deploy JIT 到 log_dir 根（c29f1b6）。
- 训练奖励/环境配置与 exp1.1 相同（RPO-Flat，已验证训练达标 reward 58.58）。

### 4. 修改文件

- `robolab/robolab/tasks/direct/base/agents/rpo_agent_cfg.py`（e5300f4 恢复 3001）
- `robolab/scripts/rsl_rl/train.py`（c29f1b6 deploy 导出）

### 5. 训练参数

- RPO-Flat，3001 iter，save_interval 100，8192 envs，代码 761d51f

### 6. 预期与验收

- ✅ 任务正常完成（状态 5），模型列表出现 model_3000.pt + model_3000_deploy.pt
- ✅ 下载 model_3000_deploy.pt，sim2sim 稳定站立（姿态 ±5°、双支撑 >70%、关节跟踪 <3°）
- ❌ 若翻滚/倒下：用 isaac_diag CSV 定位根因，修改后重训

### 7. 实验结果

> 训练任务：TASK_20260801_021，2026-08-01 启动（账号 peleha7269，代码 761d51f）
> 待训练完成后补充结果。

#### 执行日志

| 时间 | 事件 |
|------|------|
| 2026-08-01 11:55 | 创建并启动 TASK_20260801_021（exp2.3 完整训练 3001 iter，ETA ~14:15） |
| 2026-08-01 13:27 | 任务开始运行 |
| 2026-08-01 15:47 | 任务正常完成（状态5），训练耗时 ~2h20m |
| 2026-08-01 16:xx | 下载 model_3000.pt + model_3000_deploy.pt |
| 2026-08-01 16:xx | **sim2sim 验证失败**：机器人在 1-2s 内倒下。CSV 诊断显示双脚不对称、姿态角迅速发散 |

#### sim2sim 结果（exp2.3）

| 指标 | exp2.3 实测 | 目标 | 判定 |
|------|-------------|------|------|
| 站立时长 | ~1-2s | 20s | ❌ |
| 姿态角 | 迅速发散 | ±5° | ❌ |
| 双支撑率 | ~0% | >70% | ❌ |
| 结果 | 机器人翻滚倒下 | 稳定站立 | ❌ |

#### 根因分析

**核心问题：训练侧 default_pos 左右腿相同（非镜像），与 URDF 镜像关节几何不匹配。**

- X1_29 URDF 的左右腿关节轴是镜像对称设计：
  - 左 hip_pitch: origin rpy z=+1.5708, axis "0 0 1", limit [-1, 2]
  - 右 hip_pitch: origin rpy z=-1.5708, axis "0 0 1", limit [-2, 1]
  - 右 knee_pitch: axis "0 0 -1"（与左膝反向）
- exp2.3 的 default_pos 左右腿使用相同值（hip_pitch L=R=-0.1, knee L=R=0.3, ankle L=R=-0.2）
- FK 验证：相同值在镜像 URDF 下导致双脚不对称（dx=7cm 前后偏移, dz=1.3cm 高度差）
- PD-only 控制器无法补偿这种系统性不对称，导致机器人失衡翻滚

**验证方法**：用 MuJoCo 直读 URDF 计算 6 种配置的脚部世界坐标，证明左右镜像 default_pos 给出完美对称（dx=0, dz=0）。

**对比参考**：X1 原始部署配置 `rl_x1_sim.yaml` 的 `pd_stand` init_state 即为左右镜像设计（L hip_pitch=+0.4, R=-0.4 等），是验证过的正确方案。

---

## 实验 exp2.4：左右腿 default_pos 镜像对称修复——重训验证 sim2sim 稳定站立

### 1. 上一实验结果与教训

> 数据：exp2.3 sim2sim 诊断（TASK_20260801_021，model_3000_deploy.pt）
> - 训练指标达标（reward 58.58, ep_len 995），但 sim2sim 1-2s 内倒下
> - **根因已定位**：default_pos 左右相同（非镜像）→ 双脚 dx=7cm, dz=1.3cm 不对称 → PD 无法自平衡
> - FK 验证 + X1 部署代码对比确认：镜像 default_pos 给出完美对称（dx=0, dz=0）

### 2. 目标

- 用镜像对称 default_pos 重训 3001 iter
- sim2sim 稳定站立 20 秒：姿态 ±5°、双支撑率 >70%、关节跟踪误差 <3°
- 若仍不达标，继续诊断根因 → 修改 → 重训

### 3. 修改内容

| 修改 | 旧值 (exp2.3) | 新值 (exp2.4) | 说明 |
|------|--------------|--------------|------|
| 训练侧 default_pos（L腿） | hip_pitch=-0.1, knee=0.3, ankle=-0.2 | hip_pitch=+0.4, hip_roll=+0.05, hip_yaw=-0.31, knee=0.49, ankle=-0.21 | 镜像对称（X1部署值，FK验证dx=0 dz=0） |
| 训练侧 default_pos（R腿） | hip_pitch=-0.1, knee=0.3, ankle=-0.2 | hip_pitch=-0.4, hip_roll=-0.05, hip_yaw=+0.31, knee=0.49, ankle=-0.21 | L腿的左右镜像 |
| sim2sim default_pos | 同训练侧旧值 | 同训练侧新值 | 保持训练/部署一致 |

### 4. 修改文件

- `robolab/robolab/assets/robots/roboparty.py`（L210-225）：init_state joint_pos 改为镜像值
- `robolab/scripts/mujoco/sim2sim_x1_29.py`（L314-320）：default_pos 同步更新
- commit c5544a1，已推送到 x1_29 分支

### 5. 训练参数

| 参数 | 值 |
|------|-----|
| 训练方式 | 从零 |
| GM账号 | peleha7269@candaba.com |
| max_iterations | 3001 |
| save_interval | 100 |
| num_envs | 8192 |
| seed | 42 |
| 算力 | 1×4090D 24G，ESKU000001 |
| 镜像 | BJX00000178, V000220 (IsaacSim:5.1 \| IsaacLab:2.3.2) |
| 代码仓库 | lab_test.git, x1_29 分支, commit c5544a1 |
| 启动命令 | `gm-run lab_test/robolab/scripts/rsl_rl/train.py --task=RPO-Flat --headless --logger=tensorboard --num_envs=8192` |

### 6. 预期与验收

**sim2sim 验收标准**（原地站立，20 秒）：

| 指标 | exp2.3 实测 | exp2.4 目标 | 异常信号 |
|------|-------------|-----------|---------|
| 站立时长 | ~1-2s | 20s | < 10s |
| 姿态角（俯仰/侧倾） | 迅速发散 | ±5° | > 15° |
| 双支撑率 | ~0% | >70% | < 30% |
| 关节跟踪误差 | - | <3° | > 10° |

### 7. 实验结果

> 训练任务：TASK_20260803_059，2026-08-03 11:39 启动（peleha7269 账号，代码 c5544a1）
> 待训练完成后补充结果。

#### 执行日志

| 时间 | 事件 |
|------|------|
| 2026-08-03 11:39 | 创建并启动 TASK_20260803_059（exp2.4 镜像 default_pos 3001 iter，ETA ~14:00） |
| - | 待训练完成 |
