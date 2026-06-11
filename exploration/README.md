# Genesis World — Evaluation (June 2026)

Evaluation of **Genesis World** (genesis-world v1.1.1) as a robotics physics-sim / RL stack,
for a team committed to **NVIDIA RTX + Isaac Lab + Newton**. Self-contained record of what was
run, the results, and the decision.

## Verdict
**Standardize on Isaac Lab + Newton.** It fits our all-NVIDIA hardware + Omniverse rendering and
covers mainstream rigid-body RL + sim-to-real. We are **not** missing anything critical.
**Keep Genesis as a back-pocket tool** only for: unified multi-physics with cross-solver coupling
(soft-body/fluid/cloth/granular + rigid in one scene), differentiable-physics / tactile research,
or eval-in-sim. Revisit if Genesis AI proves to be a serious long-term player.
See `decision/GENESIS_vs_NEWTON.md` for the full pros/cons.

### Key findings (fact-checked)
- "10x–430,000x faster" launch marketing was independently debunked (~150x inflation under realistic
  settings); headline was vs Isaac, not MJX. MuJoCo maintainer called it "disingenuous."
- The viral **"generative" framework was never released** (still #1 open GitHub issue) — it became
  Genesis AI's closed commercial IP (their GENE robot foundation models).
- Largest 2025–26 sim-to-real locomotion work (CoRL 2025 embodiment-scaling-laws, Go2/H1 zero-shot)
  used **Isaac Lab, not Genesis**. Independent survey rates Genesis real-robot deploy readiness "Emerging."
- Genuine Genesis edges: unified multi-physics coupling, cross-platform (CUDA/ROCm/Metal/Vulkan/x86/ARM),
  partial differentiable sim (MPM/Tool only — rigid-body autodiff NOT shipped), tactile (DiffTactile).

## What was run
| Where | Result |
|---|---|
| **Mac M5 Pro (Metal)** | Genesis runs on Apple GPU. 4096 Franka envs ~1.9M env-steps/s. Rendered `artifacts/render/macos_metal_demo.mp4`. |
| **RTX PRO 6000 VM (CUDA)** | 4096 envs **5.5M**, 16384 **14.3M**, 65536 **25.8M** env-steps/s. Madrona batch render (CUDA-only, impossible on Mac) → `artifacts/render/vm_madrona_batch_samples/`. |
| **Go2 locomotion RL** | RSL-RL PPO, 4096 envs, 300 iters, ~3 min. Mean reward -0.18 → **21.35** (learned to walk). Video + checkpoints in `artifacts/go2/`. |

## VM setup gotcha (for next time)
GCP `g4-standard-48` + **NVIDIA RTX PRO 6000 Blackwell (96GB, sm_120)**, Debian 12.
- Blackwell **requires the OPEN kernel modules**: default `cuda-drivers` installs the proprietary
  module → `RmInitAdapter failed` / "No devices found". Fix: `apt-get install -y nvidia-open` + reboot.
- Env: uv + Python 3.12 + `torch ... --index-url .../cu128` (Blackwell needs CUDA 12.8) + `pip install -e .`.
- VM was **SPOT/preemptible** — deleted after eval.

## Contents
- `decision/GENESIS_vs_NEWTON.md` — decision doc (Genesis vs Newton pros/cons).
- `scripts/` — `gs_driver_setup.sh` (NVIDIA open driver), `gs_env_setup_vm.sh` (CUDA env),
  `.venv_setup.sh` (Mac/Metal env), `gs_smoke_physics.py`, `gs_smoke_render.py`, `go2_record.py` (headless policy recorder).
- `artifacts/render/` — Metal demo mp4 + Madrona batch-render RGB/depth samples.
- `artifacts/go2/` — trained policy (`logs/model_*.pt`, `cfgs.pkl`, tensorboard), `go2_walk.mp4`, training log, frame.

## Reproduce the Go2 policy
```bash
# in a genesis-world checkout, examples/locomotion/, with rsl-rl-lib>=5.0.0 + tensordict installed
python go2_train.py -e go2-walking -B 4096 --max_iterations 300
python go2_record.py -e go2-walking --ckpt -1 --out go2_walk.mp4   # headless recorder (this repo)
# tensorboard --logdir artifacts/go2/logs
```
