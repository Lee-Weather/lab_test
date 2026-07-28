# SPDX-License-Identifier: BSD-3-Clause
"""roboparty_train meta-package: install both submodules in one command.

    pip install -e .

This pulls in the LOCAL ./rsl_rl (distribution `rsl-rl-lib`, the Roboparty fork
that includes AMPRunner/DistillationRunner) and ./robolab. Because both register
the same distribution names as any pre-installed upstream versions, pip uninstalls
the upstream one and installs the local fork in its place — fixing the
``ImportError: cannot import name 'AMPRunner'`` caused by the environment's
pre-installed rsl_rl.
"""
from pathlib import Path

from setuptools import setup

_HERE = Path(__file__).resolve().parent

setup(
    name="roboparty_train",
    version="1.0.0",
    description="Roboparty RPO training workspace (bundles robolab + the Roboparty rsl_rl fork)",
    install_requires=[
        f"rsl-rl-lib @ file://{(_HERE / 'rsl_rl').as_posix()}",
        f"robolab @ file://{(_HERE / 'robolab').as_posix()}",
    ],
    python_requires=">=3.10",
)
