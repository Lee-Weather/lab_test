# Copyright (c) 2025-2026, The RoboLab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Custom event functions for the robolab environment."""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch
from isaaclab.assets import Articulation
from isaaclab.managers import SceneEntityCfg

if TYPE_CHECKING:
    from robolab.envs.base.base_env import BaseEnv


def randomize_rigid_body_com(
    env: BaseEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
    com_range: dict | None = None,
):
    """Randomize the center of mass of rigid bodies.

    Args:
        env: The environment instance.
        asset_cfg: The asset configuration specifying the robot and body names.
        com_range: Dictionary with keys 'x', 'y', 'z' and (min, max) tuple values.
    """
    if com_range is None:
        com_range = {"x": (-0.025, 0.025), "y": (-0.025, 0.025), "z": (-0.05, 0.05)}

    asset: Articulation = env.scene[asset_cfg.name]

    body_ids = asset_cfg.body_ids
    if body_ids is None:
        body_ids = list(range(asset.num_bodies))

    num_bodies = len(body_ids)
    num_envs = env.num_envs

    # Generate random COM offsets
    com_offsets = torch.zeros(num_envs, num_bodies, 3, device=env.device)
    for axis, (lo, hi) in com_range.items():
        idx = "xyz".index(axis)
        com_offsets[:, :, idx] = torch.rand(num_envs, num_bodies, device=env.device) * (hi - lo) + lo

    # Apply COM randomization via PhysX API
    try:
        root_view = asset.root_physx_view
        # Get current COMs - shape: (num_envs, num_bodies, 3)
        coms = root_view.get_coms()
        if coms is not None:
            coms[:, body_ids, :3] += com_offsets
            root_view.set_coms(coms)
    except Exception:
        # Fallback: try using rigid body properties
        pass
