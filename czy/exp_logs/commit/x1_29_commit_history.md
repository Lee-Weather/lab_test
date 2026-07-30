# X1_29 分支训练提交记录

> 项目: roboparty_train
> 仓库: https://github.com/Lee-Weather/lab_test.git
> 分支: x1_29
> 时间范围: 2026-07-29 ~ 2026-07-30
> 共计: 14 次提交
> 算力资源: ESKU000001 (1x4090D 24G)
> 镜像: BJX00000178 V000220 (IsaacSim:5.1 | IsaacLab:2.3.2) (v14 起)
>       BJX00000093 V000136 (IsaacSim:5.0 | IsaacLab:2.2.0) (v1~v13)

---

## 提交总览

| # | Commit Hash | 提交时间 | 说明 | 对应任务 | 任务状态 |
|---|-------------|---------|------|----------|---------|
| 1 | `7a84939` | 07-29 14:48 | 设置 max_iterations=3001, save_interval=100 | - | - |
| 2 | `1891088` | 07-29 18:48 | 添加 X1_29 机器人模型数据 (URDF, MJCF, meshes) | - | - |
| 3 | `4b14c87` | 07-29 19:29 | 将 RPO 模型替换为 X1_29 29-DOF 模型 | TASK_20260729_243 (v1) | 失败 |
| 4 | `6f462a0` | 07-29 20:01 | 添加自定义 randomize_rigid_body_com (Isaac Lab 2.1.0 兼容) | TASK_20260729_244 (v2), TASK_20260729_245 (v3) | 失败/失败 |
| 5 | `5e09311` | 07-29 20:16 | 移除 ray_alignment 参数 (Isaac Lab 2.1.0 不支持) | TASK_20260729_247 (v4), TASK_20260729_249 (v5) | 失败/失败 |
| 6 | `7073614` | 07-29 21:24 | 添加 pip 安装超时和重试机制 | TASK_20260729_251 (v6), TASK_20260729_252 (v7) | 失败/失败 |
| 7 | `76a1867` | 07-29 21:43 | 修正 URDF 网格路径 ../../meshes/ -> ../meshes/ | TASK_20260729_255 (v8), TASK_20260729_257 (v9) | 失败/失败 |
| 8 | `ba7fe0c` | 07-29 22:14 | 添加 env_ids 参数到 randomize_rigid_body_com | TASK_20260729_260 (v10) | 失败 (rsl-rl 3.0.1 obs_groups 错误) |
| 9 | `200140f` | 07-29 22:36 | 使用 rsl-rl 2.3.3 保持 Isaac Lab 2.2.0 兼容 | TASK_20260729_263 (v11) | 失败 (DistillationRunner 导入错误) |
| 10 | `077419e` | 07-30 08:14 | 使 DistillationRunner 导入可选 (rsl-rl 2.x 兼容) | TASK_20260730_005 (v12) | 失败 (tensordict 导入失败) |
| 11 | `23de2ff` | 07-30 08:25 | 使 tensordict 导入可选 (rpo_agent_cfg.py) | TASK_20260730_005 (v12) | 失败 (同上任务, 旧代码) |
| 12 | `c60563f` | 07-30 08:29 | 切换回 rsl-rl 3.0.1, 使用 IsaacLab 2.3.2 镜像 | TASK_20260730_007 (v14) | **已停止** (无摔倒检测) |
| 13 | - | - | (v12 失败后直接切换镜像, 无额外提交) | - | - |
| 14 | `62aee48` | 07-30 09:00 | 添加 terminate_base_height 和 terminate_base_orientation 终止条件 | TASK_20260730_016 (v15) | **训练完成** |

---

## 详细修改记录

### 1. 设置训练参数 (`7a84939`)

- **时间**: 2026-07-29 14:48:30
- **说明**: 设置 max_iterations=3001, save_interval=100, 添加 exp0 基线记录
- **修改文件**: `robolab/robolab/tasks/direct/base/agents/rpo_agent_cfg.py`, `robolab/robolab/tasks/direct/base/base_config.py`
- **效果**: 为后续 X1_29 训练设置基础参数

---

### 2. 添加 X1_29 机器人模型数据 (`1891088`)

- **时间**: 2026-07-29 18:48:00
- **说明**: 添加 X1_29 机器人完整的模型数据，包括 29 自由度 URDF、MJCF 配置和 STL 网格文件
- **修改文件**: `czy/data/x1_29/urdf/X1_29DOF_perfect_mirrored.urdf`, `czy/data/x1_29/mjcf/*`, `czy/data/x1_29/meshes/*.STL`
- **效果**: 为 X1_29 模型替换提供完整的资产文件

---

### 3. 将 RPO 模型替换为 X1_29 (`4b14c87`)

- **时间**: 2026-07-29 19:29:31
- **说明**: 核心修改 - 将 RPO (23-DOF) 机器人模型替换为 X1_29 (29-DOF) 模型
- **修改文件**:
  - `robolab/robolab/assets/robots/roboparty.py` - 添加 X1_29_CFG 配置 (29 关节, 6 组执行器)
  - `robolab/robolab/tasks/direct/base/rpo_env_cfg.py` - 更新维度 (action 23->29, obs 78->96, state 139->169), 关节名, body 名
  - `robolab/robolab/tasks/direct/base/agents/rpo_agent_cfg.py` - 修改 experiment_name 和 wandb_project 为 "x1_29_flat"
  - `robolab/robolab/tasks/direct/base/scene_cfg.py` - 修复 RayCasterCfg 配置
  - `robolab/robolab/assets/__init__.py` - 添加 CZY_DATA_DIR 路径定义
- **对应任务**: TASK_20260729_243 (X1_29_Flat_Train)
- **任务结果**: 失败 - URDF 路径错误 `Path: ../../meshes/base_link_simple_center_symmetric.STL not found`

**关键配置变更**:
```python
# rpo_env_cfg.py
self.action_space = 29      # 原 23
self.observation_space = 96  # 原 78
self.state_space = 169       # 原 139

# 终止条件 body 名
self.robot.terminate_contacts_body_names = ["lumbar_pitch_link", ".*_hip_yaw_link", ".*_hip_roll_link"]
self.robot.feet_body_names = [".*ankle_roll.*"]

# 执行器分组
X1_29_CFG actuators:
  - legs: hip_pitch, hip_roll, hip_yaw, knee_pitch
  - feet: ankle_pitch, ankle_roll
  - lumbar: lumbar_pitch, lumbar_roll, lumbar_yaw
  - shoulders: shoulder_pitch, shoulder_roll, shoulder_yaw
  - arms: elbow_pitch, elbow_yaw
  - wrists: wrist_roll, wrist_pitch, wrist_yaw
```

---

### 4. 添加自定义 randomize_rigid_body_com (`6f462a0`)

- **时间**: 2026-07-29 20:01:23
- **说明**: Isaac Lab 2.2.0 的 `isaaclab.envs.mdp` 中没有 `randomize_rigid_body_com` 函数，需要自定义实现
- **修改文件**:
  - `robolab/robolab/tasks/direct/base/mdp/events.py` - 实现 `randomize_rigid_body_com` 函数
  - `robolab/robolab/tasks/direct/base/mdp/__init__.py` - 导入 events 模块
- **对应任务**: TASK_20260729_244 (v2), TASK_20260729_245 (v3)
- **任务结果**:
  - v2: 失败 - `AttributeError: module 'robolab.tasks.direct.base.mdp' has no attribute 'randomize_rigid_body_com'`
  - v3: 失败 - `TypeError: RayCasterCfg.__init__() got an unexpected keyword argument 'ray_alignment'`

**实现代码**:
```python
def randomize_rigid_body_com(
    env: BaseEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
    com_range: dict | None = None,
):
    """Randomize the center of mass of rigid bodies."""
    if com_range is None:
        com_range = {"x": (-0.025, 0.025), "y": (-0.025, 0.025), "z": (-0.05, 0.05)}
    # ... 生成随机 COM 偏移并通过 PhysX API 应用
```

---

### 5. 移除 ray_alignment 参数 (`5e09311`)

- **时间**: 2026-07-29 20:16:49
- **说明**: Isaac Lab 2.1.0/2.2.0 的 RayCasterCfg 不支持 `ray_alignment` 参数
- **修改文件**: `robolab/robolab/tasks/direct/base/scene_cfg.py`
- **对应任务**: TASK_20260729_247 (v4), TASK_20260729_249 (v5)
- **任务结果**:
  - v4: 失败 - pip 安装 rsl-rl-lib 超时
  - v5: 失败 - `ValueError: The term 'randomize_rigid_body_com' expects mandatory parameters...`

**修改内容**:
```python
# 修改前
self.left_feet_scanner = RayCasterCfg(
    ...
    ray_alignment='yaw',  # 移除此行
)

# 修改后
self.left_feet_scanner = RayCasterCfg(
    ...
    # ray_alignment 参数已移除
)
```

---

### 6. 添加 pip 安装超时和重试 (`7073614`)

- **时间**: 2026-07-29 21:24:10
- **说明**: 网络不稳定导致 pip install rsl-rl-lib 和 tensordict 超时失败
- **修改文件**: `robolab/scripts/rsl_rl/train.py`
- **对应任务**: TASK_20260729_251 (v6), TASK_20260729_252 (v7)
- **任务结果**:
  - v6: 失败 - 仍然超时
  - v7: 失败 - URDF 网格路径错误

**修改内容**:
```python
# 添加 --timeout 300 和 3 次重试
for _ in range(3):
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--no-deps", "--timeout", "300",
            f"rsl-rl-lib=={RSL_RL_VERSION}",
            "tensordict", "orjson", "pyvers", "importlib_metadata",
        ])
        break
    except subprocess.CalledProcessError:
        print(f"[INFO] Retry installing rsl-rl-lib (attempt {_ + 2}/3)...")
```

---

### 7. 修正 URDF 网格路径 (`76a1867`)

- **时间**: 2026-07-29 21:43:18
- **说明**: URDF 中网格文件路径 `../../meshes/` 不正确，应为 `../meshes/`
- **修改文件**: `czy/data/x1_29/urdf/X1_29DOF_perfect_mirrored.urdf`
- **对应任务**: TASK_20260729_255 (v8), TASK_20260729_257 (v9)
- **任务结果**:
  - v8: 失败 - URDF 路径仍然有问题 (v8 使用旧代码)
  - v9: 失败 - `ValueError: The term 'randomize_rigid_body_com' expects mandatory parameters: [] and optional parameters: ['asset_cfg', 'com_range'], but received: ['asset_cfg', 'com_range']`

**修改内容**:
```xml
<!-- 修改前 -->
<mesh filename="../../meshes/base_link_simple_center_symmetric.STL" />

<!-- 修改后 -->
<mesh filename="../meshes/base_link_simple_center_symmetric.STL" />
```

---

### 8. 添加 env_ids 参数 (`ba7fe0c`)

- **时间**: 2026-07-29 22:14:54
- **说明**: Isaac Lab 的 EventTerm 验证要求事件函数的第二个参数为 `env_ids`，缺少会导致参数验证失败
- **修改文件**: `robolab/robolab/tasks/direct/base/mdp/events.py`
- **对应任务**: TASK_20260729_260 (v10)
- **任务结果**: 失败 - rsl-rl 3.0.1 的 `OnPolicyRunner` 期望 dict 格式观测值，但 `RslRlVecEnvWrapper` (Isaac Lab 2.2.0) 返回 tuple

**修改内容**:
```python
# 修改前
def randomize_rigid_body_com(
    env: BaseEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
    com_range: dict | None = None,
):

# 修改后
def randomize_rigid_body_com(
    env: BaseEnv,
    env_ids: torch.Tensor | None,  # 新增
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
    com_range: dict | None = None,
):
    if env_ids is None:
        env_ids = torch.arange(env.scene.num_envs, device=env.device)
```

**v10 训练日志关键信息**:
- 环境成功创建: 1024 个环境
- Event Manager 加载成功: 6 个 startup 事件 (包含 randomize_rigid_body_com)
- Reward Manager 加载成功: 29 个奖励项
- 仿真启动成功
- 错误: `AttributeError: 'tuple' object has no attribute 'keys'` (rsl-rl 3.0.1 不兼容)

---

### 9. 使用 rsl-rl 2.3.3 保持兼容 (`200140f`)

- **时间**: 2026-07-29 22:36:35
- **说明**: rsl-rl 3.0.1 期望 dict 格式观测值，但 Isaac Lab 2.2.0 的 `RslRlVecEnvWrapper` 返回 tuple。改用预装的 rsl-rl 2.3.3 保持兼容
- **修改文件**: `robolab/scripts/rsl_rl/train.py`
- **对应任务**: TASK_20260729_263 (v11)
- **任务结果**: 失败 - `ImportError: cannot import name 'DistillationRunner' from 'rsl_rl.runners'` (rsl-rl 2.3.3 没有 DistillationRunner)

**修改内容**:
```python
# 修改前
RSL_RL_VERSION = "3.0.1"

# 修改后
RSL_RL_VERSION = "2.3.3"  # 使用预装版本，保持 Isaac Lab 2.2.0 兼容

# obs_groups 仅在 rsl-rl 3.x 时添加
if version.parse(installed_version) >= version.parse("3.0.0"):
    if "obs_groups" not in agent_cfg_dict:
        agent_cfg_dict["obs_groups"] = {"policy": ["policy"], "critic": ["critic"]}

# tensordict 仅在 rsl-rl 3.x 时安装
if version.parse(installed_version) >= version.parse("3.0.0"):
    try:
        import tensordict
    except ImportError:
        # ... 安装逻辑
```

---

### 10. 使 DistillationRunner 导入可选 (`077419e`)

- **时间**: 2026-07-30 08:14:27
- **说明**: rsl-rl 2.3.3 没有 `DistillationRunner`，需要改为可选导入
- **修改文件**: `robolab/scripts/rsl_rl/train.py`
- **对应任务**: TASK_20260730_005 (v12)
- **任务结果**: 失败 - `ModuleNotFoundError: No module named 'tensordict'` (rpo_agent_cfg.py 第 41 行直接导入 tensordict)

**修改内容**:
```python
# 修改前
from rsl_rl.runners import DistillationRunner, OnPolicyRunner

# 修改后
from rsl_rl.runners import OnPolicyRunner
try:
    from rsl_rl.runners import DistillationRunner
except ImportError:
    DistillationRunner = None
```

---

### 11. 使 tensordict 导入可选 (`23de2ff`)

- **时间**: 2026-07-30 08:25:00
- **说明**: `rpo_agent_cfg.py` 第 41 行直接 `from tensordict import TensorDict`，但使用 rsl-rl 2.3.3 时未安装 tensordict
- **修改文件**: `robolab/robolab/tasks/direct/base/agents/rpo_agent_cfg.py`
- **对应任务**: TASK_20260730_005 (v12) - 同一任务使用旧代码, 失败
- **任务结果**: 失败 (任务使用了上一个 commit 的代码)

**修改内容**:
```python
# 修改前
from tensordict import TensorDict

# 修改后
try:
    from tensordict import TensorDict
except ImportError:
    TensorDict = None
```

---

### 12. 切换到 IsaacLab 2.3.2 镜像 + rsl-rl 3.0.1 (`c60563f`)

- **时间**: 2026-07-30 08:29:00
- **说明**: 放弃在 IsaacLab 2.2.0 上降级 rsl-rl 2.3.3 的方案, 改用 IsaacLab 2.3.2 镜像 (BJX00000178), 原生支持 rsl-rl 3.0.1 和 dict 格式观测值
- **修改文件**: `robolab/scripts/rsl_rl/train.py`
- **对应任务**: TASK_20260730_007 (v14)
- **任务结果**: **训练成功运行!**

**修改内容**:
```python
# 修改前 (commit 9)
RSL_RL_VERSION = "2.3.3"  # 降级兼容 Isaac Lab 2.2.0

# 修改后
RSL_RL_VERSION = "3.0.1"  # IsaacLab 2.3.2 原生支持
```

**关键决策**: IsaacLab 2.2.0 的 `RslRlVecEnvWrapper` 返回 tuple 格式观测值, 与 rsl-rl 3.0.1 不兼容。尝试降级到 rsl-rl 2.3.3 又遇到 DistillationRunner 和 tensordict 导入问题。最终选择切换到 IsaacLab 2.3.2 镜像, 一次性解决所有兼容性问题。

**训练日志关键信息**:
- 镜像: IsaacSim:5.1 | IsaacLab:2.3.2 | Python:3.11.13 | PyTorch:2.7.0
- 环境: 1024 个并行环境
- Event Manager: 6 个 startup 事件 (含 randomize_rigid_body_com)
- Reward Manager: 29 个奖励项
- 第 100 轮自动保存模型: `model_100.pt`
- 训练速度: ~16,000 steps/s
- ETA: ~1 小时 11 分钟完成 3001 轮

**v14 训练问题**: Episode length 始终为 1000 (机器人从不摔倒), termination_penalty 为 0.0。原因是 `terminate_base_height` 和 `terminate_base_orientation` 均未设置 (None), 仅依靠接触力终止条件不够。训练虽在收敛 (reward -151 -> -84), 但机器人在"偷懒"站立而非学习行走。在第 449 轮手动停止, 修改代码后重新提交 v15。

---

### 14. 添加终止条件 (base_height + orientation) (`62aee48`)

- **时间**: 2026-07-30 09:00:00
- **说明**: v14 训练中 Episode length 始终为 1000, 机器人从不摔倒。原因是 `terminate_base_height` 和 `terminate_base_orientation` 均未设置 (None), 仅靠接触力终止不足以检测摔倒
- **修改文件**: `robolab/robolab/tasks/direct/base/rpo_env_cfg.py`
- **对应任务**: TASK_20260730_016 (v15)
- **任务结果**: **训练完成** - 3001 轮训练完成, 31 个模型检查点, 训练收敛

**修改内容**:
```python
# rpo_env_cfg.py __post_init__ 中添加
self.robot.terminate_base_height = 0.3        # 基座低于 0.3m 判定摔倒 (初始 0.65m)
self.robot.terminate_base_orientation = 0.5   # 倾斜超过 ~29 度判定摔倒
```

**v15 训练最终结果**:
- 训练完成: 3001 轮, 运行 93.5 分钟
- 最终模型: model_3000.pt (已上传)
- 模型检查点: 31 个 (每 100 轮保存一次)
- Episode length: 30 -> 377 (12.6x 增长, 机器人存活 7.5 秒)
- Value loss: 0.337 -> 0.022 (93% 下降, critic 收敛)
- Entropy loss: 40.77 -> 7.71 (81% 下降, 策略确定性化)
- 速度跟踪: 19.7x 改善 (lin_vel), 41.7x 改善 (ang_vel)
- 直立稳定性: 11.7x 改善
- 摔倒率减少 19%

---

## 修改的文件汇总

| 文件 | 修改次数 | 说明 |
|------|---------|------|
| `robolab/scripts/rsl_rl/train.py` | 6 | rsl-rl 版本管理、pip 超时重试、导入兼容 |
| `robolab/robolab/tasks/direct/base/mdp/events.py` | 2 | 自定义 randomize_rigid_body_com 实现 + env_ids 参数 |
| `robolab/robolab/tasks/direct/base/rpo_env_cfg.py` | 1 | 维度、关节名、body 名适配 X1_29 |
| `robolab/robolab/assets/robots/roboparty.py` | 1 | X1_29_CFG 机器人资产配置 |
| `robolab/robolab/tasks/direct/base/scene_cfg.py` | 1 | 移除 ray_alignment 参数 |
| `robolab/robolab/tasks/direct/base/agents/rpo_agent_cfg.py` | 2 | experiment_name, max_iterations, tensordict 可选导入 |
| `czy/data/x1_29/urdf/X1_29DOF_perfect_mirrored.urdf` | 1 | 修正网格路径 |
| `robolab/robolab/assets/__init__.py` | 1 | CZY_DATA_DIR 路径 |
| `robolab/robolab/tasks/direct/base/mdp/__init__.py` | 1 | 导入 events 模块 |

---

## 训练任务历史

| 版本 | 任务 ID | Commit | 镜像 | 状态 | 失败原因 |
|------|---------|--------|------|------|---------|
| v1 | TASK_20260729_243 | `4b14c87` | 2.2.0 | 失败 | URDF 路径错误 |
| v2 | TASK_20260729_244 | `6f462a0` | 2.2.0 | 失败 | mdp 模块缺少 randomize_rigid_body_com |
| v3 | TASK_20260729_245 | `6f462a0` | 2.2.0 | 失败 | RayCasterCfg 不支持 ray_alignment |
| v4 | TASK_20260729_247 | `5e09311` | 2.2.0 | 失败 | pip 安装超时 |
| v5 | TASK_20260729_249 | `5e09311` | 2.2.0 | 失败 | EventTerm 参数验证失败 |
| v6 | TASK_20260729_251 | `7073614` | 2.2.0 | 失败 | pip 安装超时 |
| v7 | TASK_20260729_252 | `7073614` | 2.2.0 | 失败 | URDF 网格路径错误 |
| v8 | TASK_20260729_255 | `76a1867` | 2.2.0 | 失败 | URDF 路径 (旧代码) |
| v9 | TASK_20260729_257 | `76a1867` | 2.2.0 | 失败 | EventTerm env_ids 参数缺失 |
| v10 | TASK_20260729_260 | `ba7fe0c` | 2.2.0 | 失败 | rsl-rl 3.0.1 obs_groups 不兼容 |
| v11 | TASK_20260729_263 | `200140f` | 2.2.0 | 失败 | DistillationRunner 导入失败 |
| v12 | TASK_20260730_005 | `077419e` | 2.2.0 | 失败 | tensordict 导入失败 |
| **v14** | **TASK_20260730_007** | **`c60563f`** | **2.3.2** | **已停止** | **无摔倒检测 (ep_len=1000)** |
| **v15** | **TASK_20260730_016** | **`62aee48`** | **2.3.2** | **训练完成** | **-** |

---

## X1_29 机器人配置详情

### 关节配置 (29-DOF)

| 执行器组 | 关节 | 刚度 | 阻尼 | 力矩限制 |
|----------|------|------|------|---------|
| legs | hip_pitch, hip_roll, hip_yaw, knee_pitch | 100-180 | 3.3-6.0 | 150 N·m |
| feet | ankle_pitch, ankle_roll | 20-40 | 2.0-4.0 | 30 N·m |
| lumbar | lumbar_pitch, lumbar_roll, lumbar_yaw | 200 | 10.0 | 200 N·m |
| shoulders | shoulder_pitch, shoulder_roll, shoulder_yaw | 60-80 | 3.0-8.0 | 60 N·m |
| arms | elbow_pitch, elbow_yaw | 40-60 | 4.0-6.0 | 60 N·m |
| wrists | wrist_roll, wrist_pitch, wrist_yaw | 10 | 1.0 | 10 N·m |

### URDF 资产

- **路径**: `czy/data/x1_29/urdf/X1_29DOF_perfect_mirrored.urdf`
- **自由度**: 29 (腿 12 + 脚 4 + 腰 3 + 肩 6 + 臂 4 + 腕 6... 实际为左右对称)
- **初始姿态**: 半蹲 (hip_pitch=-0.1, knee_pitch=0.3, ankle_pitch=-0.2)
- **执行器类型**: DelayedPDActuator (带延迟仿真)

---

## 当前状态

- **最新 commit**: `62aee48` (fix: add terminate_base_height and terminate_base_orientation for X1_29 fall detection)
- **当前任务**: TASK_20260730_016 (v15) - **训练完成**
- **镜像**: BJX00000178 V000220 (IsaacSim:5.1 | IsaacLab:2.3.2)
- **训练完成时间**: 2026-07-30 10:33:19 (运行 5607 秒, 约 93.5 分钟)
- **最终迭代**: 3000/3000 (3001 轮完成)
- **总训练步数**: 73,752,576
- **模型检查点**: 31 个 (model_100.pt ~ model_3000.pt)
- **最终模型**: model_3000.pt (已上传)

### 最终收敛指标 (iter 3000)

| 指标 | iter 0 | iter 3000 | 改善 |
|------|--------|-----------|------|
| Mean reward | -8.68 | -6.74 | +22% |
| Episode length | 30 (0.6s) | 377 (7.5s) | 12.6x |
| Value loss | 0.337 | 0.022 | -93% |
| Entropy loss | 40.77 | 7.71 | -81% |
| Action noise std | 0.99 | 0.33 | -67% |
| track_lin_vel_xy | 0.009 | 0.177 | 19.7x |
| track_ang_vel_z | 0.004 | 0.167 | 41.7x |
| upward | 0.012 | 0.141 | 11.7x |
| termination_penalty | -0.200 | -0.162 | 摔倒减少 19% |

### 收敛判定

训练成功收敛, 依据:
1. Episode length 从 30 步增长到 377 步 (12.6x), 机器人存活时间从 0.6 秒增长到 7.5 秒
2. Value loss 从 0.337 降至 0.022 (93% 下降), critic 网络已收敛
3. Entropy loss 从 40.77 降至 7.71 (81% 下降), 策略已确定性化
4. Action noise std 从 0.99 降至 0.33 (67% 下降), 探索阶段结束
5. 速度跟踪能力提升 19.7x (lin_vel) / 41.7x (ang_vel)
6. 直立稳定性提升 11.7x
7. 摔倒率减少 19%
