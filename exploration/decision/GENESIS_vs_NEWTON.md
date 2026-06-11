# Genesis vs. NVIDIA Newton — Decision Notes

_Context: deciding the physics/sim stack for robot learning. Our situation: all-in on **NVIDIA RTX**, staying in the **Isaac/Omniverse** ecosystem, no plan to target Apple Metal / AMD / ARM._

## TL;DR for us
**Default to Newton (in Isaac Lab/Sim).** Our hardware and rendering strategy are exactly what Newton is built for, and its biggest tradeoff (NVIDIA-only) costs us nothing. Keep Genesis in our back pocket for laptop-side prototyping and non-rigid (fluids/granular/soft-body) work.

## What each one is
- **Newton** — open-source, GPU physics engine on **NVIDIA Warp + OpenUSD**, by NVIDIA + Google DeepMind + Disney, under the Linux Foundation. Shipped **1.0 at GTC 2026**. Core solver is **MuJoCo-Warp** (GPU MuJoCo) + Disney's **Kamino** (deformables / closed-loop linkages). It's the **native physics backend for Isaac Lab/Sim**.
- **Genesis** — `pip install genesis-world`. Its **own** unified multi-physics engine (rigid + MPM/FEM/PBD/SPH + IPC + fluids) on its **own cross-platform compiler (Quadrants)**. MuJoCo is only a *reference*, not the solver. Ships built-in renderers (Nyx/Luisa/Madrona) + sensors.

## Quick comparison
| | **Newton** | **Genesis** |
|---|---|---|
| Hardware | **NVIDIA only** (Warp/CUDA) | NVIDIA, AMD, Apple Metal, Vulkan, x86, ARM |
| Rigid solver | **Is MuJoCo** (MJWarp) — bit-for-bit fidelity | Own solver; MuJoCo-*like* |
| Physics scope | Rigid + Kamino deformables | **Broad** multi-physics + cross-solver coupling |
| Rendering | Isaac Sim / Omniverse RTX | Built-in (self-contained) |
| Isaac Lab | **Native backend** | Not integrated (separate stack) |
| Backing | NVIDIA + DeepMind + Disney + Linux Foundation | Genesis AI |
| Differentiable | Yes | Yes (with caveats per backend) |

## Genesis — pros / cons
**Pros**
- Runs anywhere (incl. Mac laptops) — great for prototyping; no vendor lock-in.
- Widest physics in one engine: fluids, granular, soft tissue, cloth, cutting, coupling.
- Lightweight, self-contained (sim + render + data-gen), readable/hackable.
- Very fast rigid-body throughput; trivial install.

**Cons (for us)**
- Cross-platform portability is wasted — we're NVIDIA-only.
- Not bit-for-bit MuJoCo; smaller ecosystem & task zoo than Isaac Lab.
- No native Isaac Lab/Omniverse integration → you own the glue code.
- Single-vendor backing; smaller community.

## Newton — pros / cons
**Pros (for us)**
- Native to **Isaac Lab/Sim** — USD assets, Omniverse RTX rendering, sim-to-real tooling, task zoo.
- **True MuJoCo fidelity** (MJWarp) + the whole MuJoCo/MJCF ecosystem transfers.
- Massive backing (NVIDIA/DeepMind/Disney/Linux Foundation) → likely the long-term standard.
- **Kamino** handles closed-loop/parallel-linkage mechanisms (dexterous hands, legged linkages); differentiable; RL-optimized.
- Tuned for our exact GPUs (RTX PRO 6000 Blackwell).

**Cons**
- **NVIDIA-only** (irrelevant to us).
- Heavier stack (Omniverse/USD) than a plain pip install.
- 1.0 is new — API still maturing fast.

## When to pick which
**Pick Newton (Isaac Lab) when** — _our case_ — you're on NVIDIA, want Omniverse rendering, need MuJoCo fidelity / sim-to-real, rigid-body robot RL, and ecosystem standardization.

**Pick Genesis when** you need hardware portability (Macs/AMD), non-rigid/multi-material physics or coupling, a lightweight self-contained engine with built-in rendering, or a hackable codebase to modify solver internals.

## Escape hatch
Both load **MJCF/URDF**, so assets/robots are portable. Realistic hybrid: prototype/iterate in Genesis on a laptop → run production training & sim-to-real in **Newton + Isaac Lab** on the RTX boxes.
