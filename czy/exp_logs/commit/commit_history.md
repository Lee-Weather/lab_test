# GM 平台训练提交记录

> 项目: roboparty_train
> 仓库: https://github.com/Lee-Weather/lab_test.git
> 分支: main
> 时间范围: 2026-07-28 ~ 2026-07-29
> 共计: 24 次提交（2 次初始设置 + 22 次修复）

---

## 提交总览

| # | Commit Hash | 提交时间 | 说明 |
|---|-------------|---------|------|
| 1 | `74c7fd7` | 07-28 18:11 | 首次提交，推送代码到 lab_test 仓库 |
| 2 | `933bfa8` | 07-28 18:18 | 移除子模块，转为普通文件 |
| 3 | `c92ac9c` | 07-28 18:49 | rsl-rl-lib 版本不匹配，自动安装替代 exit(1) |
| 4 | `4e1757d` | 07-28 19:06 | 用 --no-deps 避免升级 torch |
| 5 | `d3bf60e` | 07-28 19:18 | 同时安装 tensordict 及其依赖 |
| 6 | `5a93ed4` | 07-28 19:57 | 无条件检查并安装 tensordict |
| 7 | `e41d9ac` | 07-28 20:16 | 用 --target 指定 tensordict 安装路径 |
| 8 | `bcacf8e` | 07-29 08:27 | --no-deps + --target 组合 |
| 9 | `c4cf886` | 07-29 08:40 | 加 --upgrade 和 sys.path.insert |
| 10 | `155ec62` | 07-29 09:02 | invalidate_caches 清除导入缓存 |
| 11 | `bf1ddbb` | 07-29 09:03 | 用 pip show 找 tensordict 安装路径 |
| 12 | `040cd76` | 07-29 09:19 | AMPRunner 改为条件导入 |
| 13 | `ce5ea18` | 07-29 09:41 | RslRlOnPolicyRunnerCfg 作为别名 |
| 14 | `6f00b2d` | 07-29 09:51 | handle_deprecated_rsl_rl_cfg 可选导入 |
| 15 | `eaea9c4` | 07-29 10:03 | 自动安装 robolab 包 |
| 16 | `6c02d56` | 07-29 10:15 | robolab 源码目录加入 sys.path |
| 17 | `850475c` | 07-29 10:29 | MultiMeshRayCaster 回退到 RayCaster |
| 18 | `652cc1b` | 07-29 10:30 | 黑名单过滤 parkour/amp/beyondmimic 模块 |
| 19 | `f348c5e` | 07-29 10:54 | 添加 RPO 机器人 URDF 和 mesh 文件 |
| 20 | `43fe06e` | 07-29 11:09 | getattr 处理 class_name 属性 |
| 21 | `44df7f4` | 07-29 11:26 | 添加默认 obs_groups 字段 |
| 22 | `6ffa425` | 07-29 11:44 | obs_groups 设置 policy/critic 键 |
| 23 | `dcf3bdc` | 07-29 12:51 | 禁用 debug_vis 避免缺失 USD 资源 |
| 24 | `f4a5e1d` | 07-29 13:09 | wandb 切换为 tensorboard 日志 |

---

## 详细修改记录

### 1. 首次提交 (`74c7fd7`)

- **时间**: 2026-07-28 18:11:41
- **说明**: 将 roboparty_train 代码首次推送到 lab_test 远程仓库
- **修改文件**: 全量推送

---

### 2. 移除子模块 (`933bfa8`)

- **时间**: 2026-07-28 18:18:52
- **说明**: 将 git 子模块（robolab、rsl_rl）转为普通文件提交，以便 GM 平台能直接拉取代码
- **修改文件**: `.gitmodules`, `robolab/`, `rsl_rl/`

---

### 3. rsl-rl-lib 版本自动安装 (`c92ac9c`)

- **时间**: 2026-07-28 18:49:39
- **问题**: 镜像预装 rsl-rl-lib 2.3.1，但 train.py 要求 >= 3.0.1，原代码直接 `exit(1)` 退出
- **修复**: 将版本不匹配时的 `exit(1)` 改为自动 `pip install rsl-rl-lib==3.0.1`
- **修改文件**: `robolab/scripts/rsl_rl/train.py`

```python
# 修改前
print(f"Please install the correct version...")
exit(1)

# 修改后
subprocess.check_call([sys.executable, "-m", "pip", "install", f"rsl-rl-lib=={RSL_RL_VERSION}"])
```

---

### 4. --no-deps 避免 torch 升级 (`4e1757d`)

- **时间**: 2026-07-28 19:06:16
- **问题**: `pip install rsl-rl-lib==3.0.1` 会拉取 torch 2.13.0（526MB），破坏镜像中的 torch 2.5.1
- **修复**: 添加 `--no-deps` 参数
- **修改文件**: `robolab/scripts/rsl_rl/train.py`

---

### 5. 同时安装 tensordict 依赖 (`d3bf60e`)

- **时间**: 2026-07-28 19:18:47
- **问题**: `--no-deps` 导致 tensordict 未安装，rsl-rl-lib 3.0.1 依赖 tensordict
- **修复**: 同时安装 tensordict, orjson, pyvers, importlib_metadata
- **修改文件**: `robolab/scripts/rsl_rl/train.py`

---

### 6. 无条件检查 tensordict (`5a93ed4`)

- **时间**: 2026-07-28 19:57:06
- **问题**: 新镜像预装了 rsl-rl-lib 3.0.1（版本检查不触发），但缺少 tensordict
- **修复**: 在版本检查代码块后，无条件 try-import tensordict
- **修改文件**: `robolab/scripts/rsl_rl/train.py`

---

### 7. --target 指定安装路径 (`e41d9ac`)

- **时间**: 2026-07-28 20:16:32
- **问题**: pip install 安装到系统 Python，Isaac Sim 的 Python 找不到 tensordict
- **修复**: 使用 `--target` 参数指定安装到 rsl_rl 所在的 site-packages 目录
- **修改文件**: `robolab/scripts/rsl_rl/train.py`

```python
import rsl_rl
_site_packages = os.path.dirname(os.path.dirname(rsl_rl.__file__))
subprocess.check_call([..., "--target", _site_packages])
```

---

### 8. --no-deps + --target 组合 (`bcacf8e`)

- **时间**: 2026-07-29 08:27:57
- **问题**: 只用 `--target` 没加 `--no-deps`，导致下载 torch 2.13.0 超时
- **修复**: 同时使用 `--no-deps` 和 `--target`
- **修改文件**: `robolab/scripts/rsl_rl/train.py`

---

### 9. --upgrade 和 sys.path.insert (`c4cf886`)

- **时间**: 2026-07-29 08:40:07
- **问题**: `--target` 目录已存在旧文件，pip 跳过安装（WARNING: already exists）
- **修复**: 添加 `--upgrade` 强制覆盖，并 `sys.path.insert(0, _site_packages)` 确保路径可搜索
- **修改文件**: `robolab/scripts/rsl_rl/train.py`

---

### 10. invalidate_caches 清除导入缓存 (`155ec62`)

- **时间**: 2026-07-29 09:02:02
- **问题**: pip install 报告成功，但 Python 仍找不到 tensordict（导入缓存问题）
- **修复**: 调用 `importlib.invalidate_caches()` 并立即 `import tensordict` 验证
- **修改文件**: `robolab/scripts/rsl_rl/train.py`

---

### 11. pip show 找安装路径 (`bf1ddbb`)

- **时间**: 2026-07-29 09:03:13
- **问题**: 不确定 tensordict 实际安装位置
- **修复**: 用 `pip show tensordict` 获取 Location 字段，添加到 sys.path
- **修改文件**: `robolab/scripts/rsl_rl/train.py`

```python
result = subprocess.run([sys.executable, "-m", "pip", "show", "tensordict"], capture_output=True, text=True)
for line in result.stdout.splitlines():
    if line.startswith("Location:"):
        _loc = line.split(":", 1)[1].strip()
        if _loc not in sys.path:
            sys.path.insert(0, _loc)
```

---

### 12. AMPRunner 条件导入 (`040cd76`)

- **时间**: 2026-07-29 09:19:28
- **问题**: `from rsl_rl.runners import AMPRunner` 失败，rsl-rl-lib 3.0.1 的 pip 包不含 AMPRunner
- **修复**: 改为 try-except 条件导入，RPO-Flat 不需要 AMPRunner
- **修改文件**: `robolab/scripts/rsl_rl/train.py`

```python
from rsl_rl.runners import DistillationRunner, OnPolicyRunner
try:
    from rsl_rl.runners import AMPRunner
except ImportError:
    AMPRunner = None
```

---

### 13. RslRlOnPolicyRunnerCfg 别名 (`ce5ea18`)

- **时间**: 2026-07-29 09:41:22
- **问题**: `RslRlBaseRunnerCfg` 在 IsaacLab 2.2.0 中不存在
- **修复**: 使用 `RslRlOnPolicyRunnerCfg as RslRlBaseRunnerCfg` 别名
- **修改文件**: `robolab/scripts/rsl_rl/train.py`, `robolab/scripts/rsl_rl/cli_args.py`

---

### 14. handle_deprecated_rsl_rl_cfg 可选导入 (`6f00b2d`)

- **时间**: 2026-07-29 09:51:23
- **问题**: `handle_deprecated_rsl_rl_cfg` 在 IsaacLab 2.2.0 中不存在
- **修复**: try-except 导入，失败时创建空操作 fallback 函数
- **修改文件**: `robolab/scripts/rsl_rl/train.py`

```python
try:
    from isaaclab_rl.rsl_rl import handle_deprecated_rsl_rl_cfg
except ImportError:
    def handle_deprecated_rsl_rl_cfg(agent_cfg, *args, **kwargs):
        return agent_cfg
```

---

### 15. 自动安装 robolab 包 (`eaea9c4`)

- **时间**: 2026-07-29 10:03:27
- **问题**: `import robolab.tasks` 失败，robolab 包未安装到 Python 环境
- **修复**: 自动 `pip install -e` 安装仓库中的 robolab 包
- **修改文件**: `robolab/scripts/rsl_rl/train.py`

---

### 16. robolab 源码目录加入 sys.path (`6c02d56`)

- **时间**: 2026-07-29 10:15:29
- **问题**: pip install 成功但 Python 仍找不到 robolab（Isaac Sim Python 环境隔离）
- **修复**: 将 robolab 源码目录直接插入 sys.path
- **修改文件**: `robolab/scripts/rsl_rl/train.py`

---

### 17. MultiMeshRayCaster 回退 (`850475c`)

- **时间**: 2026-07-29 10:29:35
- **问题**: `from isaaclab.sensors.ray_caster import MultiMeshRayCaster` 失败（IsaacLab 2.2.0 无此类）
- **修复**: try-except 导入，回退到 `RayCaster`
- **修改文件**: `robolab/robolab/sensors/grouped_ray_caster/grouped_ray_caster.py`

```python
try:
    from isaaclab.sensors.ray_caster import MultiMeshRayCaster
except ImportError:
    from isaaclab.sensors.ray_caster import RayCaster as MultiMeshRayCaster
```

---

### 18. 黑名单过滤不兼容模块 (`652cc1b`)

- **时间**: 2026-07-29 10:30:21
- **问题**: robolab.tasks 遍历导入所有子模块时，parkour/amp 模块触发 IsaacLab 2.2.0 兼容性错误
- **修复**: 将 parkour, amp, beyondmimic 加入 `_BLACKLIST_PKGS`
- **修改文件**: `robolab/robolab/tasks/__init__.py`

```python
_BLACKLIST_PKGS = ["utils", "parkour", "amp", "beyondmimic"]
```

---

### 19. 添加 URDF 和 mesh 文件 (`f348c5e`)

- **时间**: 2026-07-29 10:54:35
- **问题**: `ValueError: The asset path does not exist: .../data/robots/roboparty/rpo/urdf/rpo.urdf`
- **修复**: 从 `https://github.com/Roboparty/rpo_description.git` 克隆并添加 URDF + 24 个 STL mesh 文件
- **修改文件**: `robolab/data/robots/roboparty/rpo/urdf/rpo.urdf`, `robolab/data/robots/roboparty/rpo/meshes/*.STL`（25 个文件）

---

### 20. getattr 处理 class_name (`43fe06e`)

- **时间**: 2026-07-29 11:09:13
- **问题**: `AttributeError: 'RPOFlatAgentCfg' object has no attribute 'class_name'`（IsaacLab 2.2.0 的配置类无此属性）
- **修复**: 使用 `getattr(agent_cfg, "class_name", "OnPolicyRunner")` 提供默认值
- **修改文件**: `robolab/scripts/rsl_rl/train.py`

```python
runner_class_name = getattr(agent_cfg, "class_name", "OnPolicyRunner")
```

---

### 21. 添加默认 obs_groups (`44df7f4`)

- **时间**: 2026-07-29 11:26:41
- **问题**: `KeyError: 'obs_groups'`（rsl-rl-lib 3.0.1 的 OnPolicyRunner 期望配置中有 obs_groups）
- **修复**: 如果 agent_cfg.to_dict() 中没有 obs_groups，添加空字典
- **修改文件**: `robolab/scripts/rsl_rl/train.py`

---

### 22. obs_groups 设置 policy/critic 键 (`6ffa425`)

- **时间**: 2026-07-29 11:44:01
- **问题**: `ValueError: obs_groups must contain 'policy' key`（空字典不够）
- **修复**: 设置 `{"policy": ["policy"], "critic": ["critic"]}`
- **修改文件**: `robolab/scripts/rsl_rl/train.py`

```python
if "obs_groups" not in agent_cfg_dict:
    agent_cfg_dict["obs_groups"] = {"policy": ["policy"], "critic": ["critic"]}
```

---

### 23. 禁用 debug_vis (`dcf3bdc`)

- **时间**: 2026-07-29 12:51:53
- **问题**: `FileNotFoundError: USD file not found: '/root/Assets/Isaac/5.1/.../arrow_x.usd'`（velocity command 可视化标记缺失）
- **修复**: 将 `base_config.py` 中 `debug_vis: bool = True` 改为 `False`
- **修改文件**: `robolab/robolab/tasks/direct/base/base_config.py`

---

### 24. wandb 切换为 tensorboard (`f4a5e1d`)

- **时间**: 2026-07-29 13:09:11
- **问题**: `wandb.errors.errors.UsageError: No API key configured`（rsl-rl-lib 3.0.1 默认使用 wandb 日志）
- **修复**: 将 `base_config.py` 中 `logger = "wandb"` 改为 `"tensorboard"`
- **修改文件**: `robolab/robolab/tasks/direct/base/base_config.py`

---

## 修改的文件汇总

| 文件 | 修改次数 | 说明 |
|------|---------|------|
| `robolab/scripts/rsl_rl/train.py` | 14 | 主要修改文件，处理依赖安装和 API 兼容性 |
| `robolab/robolab/tasks/direct/base/base_config.py` | 2 | 禁用 debug_vis、切换 logger |
| `robolab/scripts/rsl_rl/cli_args.py` | 1 | RslRlBaseRunnerCfg 别名 |
| `robolab/robolab/tasks/__init__.py` | 1 | 黑名单过滤 |
| `robolab/robolab/sensors/grouped_ray_caster/grouped_ray_caster.py` | 1 | MultiMeshRayCaster 回退 |
| `robolab/data/robots/roboparty/rpo/*` | 1 | 新增 URDF + 25 个 mesh 文件 |

## 最终结果

- **训练成功启动**: 是（IsaacLab 2.3.1 镜像）
- **完成任务**: TASK_20260729_124
- **训练迭代**: 221/9001 轮（被平台时间限制终止）
- **训练指标**: Value loss 0.2872 -> 0.0185，Entropy loss 31.88 -> 20.69（持续改善）
- **模型保存**: 未达到首次保存点（save_interval=1000）
- **ETA**: 约 7 小时完成全部 9001 轮
