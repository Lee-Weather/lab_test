#!/usr/bin/env python3
"""Convert X1_29 training checkpoint to JIT policy for sim2sim.

Usage:
    python convert_x1_29_checkpoint.py --checkpoint czy/data/x1_29_models/model_300.pt --output policy_300.pt
"""
import argparse
import torch
import torch.nn as nn


class PolicyMLP(nn.Module):
    """Pure MLP actor matching the trained X1_29 policy structure."""
    def __init__(self, input_dim=960, hidden_dims=(512, 256, 128), output_dim=29):
        super().__init__()
        layers = []
        prev = input_dim
        for h in hidden_dims:
            layers += [nn.Linear(prev, h), nn.ELU()]
            prev = h
        layers.append(nn.Linear(prev, output_dim))
        self.actor = nn.Sequential(*layers)

    def forward(self, x):
        return self.actor(x)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=str, required=True)
    parser.add_argument("--output", type=str, default="policy.pt")
    args = parser.parse_args()

    ckpt = torch.load(args.checkpoint, map_location="cpu")
    sd = ckpt["model_state_dict"]

    # Verify structure
    actor_keys = [k for k in sd if k.startswith("actor.")]
    print(f"Checkpoint iter: {ckpt.get('iter')}")
    print(f"Actor keys: {actor_keys}")

    # Build MLP and load weights
    policy = PolicyMLP(input_dim=sd["actor.0.weight"].shape[1],
                       output_dim=sd["actor.6.weight"].shape[0])
    policy_sd = {k: v for k, v in sd.items() if k.startswith("actor.")}
    policy.load_state_dict(policy_sd)
    policy.eval()

    # Test forward pass
    dummy = torch.zeros(1, policy.actor[0].in_features)
    with torch.no_grad():
        out = policy(dummy)
    print(f"Forward pass: input {dummy.shape} -> output {out.shape}")

    # Export as JIT
    scripted = torch.jit.script(policy)
    scripted.save(args.output)
    print(f"Saved JIT policy to: {args.output}")

    # Verify loadable
    loaded = torch.jit.load(args.output)
    with torch.no_grad():
        out2 = loaded(dummy)
    assert torch.allclose(out, out2), "JIT verification failed!"
    print("JIT verification passed.")


if __name__ == "__main__":
    main()
