"""Smoke test 1: pure physics on Apple Metal GPU (no rendering).
Builds a batched rigid-body scene, steps it, and reports throughput.
"""
import time
import argparse
import genesis as gs

p = argparse.ArgumentParser()
p.add_argument("--backend", default="gpu", choices=["gpu", "cpu", "metal"])
p.add_argument("--n_envs", type=int, default=4096)
p.add_argument("--steps", type=int, default=300)
args = p.parse_args()

backend = {"gpu": gs.gpu, "cpu": gs.cpu, "metal": gs.metal}[args.backend]
gs.init(backend=backend, precision="32")

scene = gs.Scene(
    show_viewer=False,
    rigid_options=gs.options.RigidOptions(dt=0.01),
)
scene.add_entity(gs.morphs.Plane())
# A Franka arm — articulated rigid body, the flagship demo asset.
franka = scene.add_entity(gs.morphs.MJCF(file="xml/franka_emika_panda/panda.xml"))

# Batched/parallel environments — the headline scalability feature.
scene.build(n_envs=args.n_envs, env_spacing=(1.0, 1.0))

# Warmup (kernel compilation happens lazily on first steps).
for _ in range(10):
    scene.step()

t0 = time.perf_counter()
for _ in range(args.steps):
    scene.step()
# Force GPU sync by reading state back to host.
_ = franka.get_dofs_position().cpu()
dt = time.perf_counter() - t0

total = args.steps * args.n_envs
print("\n==== RESULT ====")
print(f"backend           : {gs.backend}")
print(f"n_envs            : {args.n_envs}")
print(f"steps             : {args.steps}")
print(f"wall time         : {dt:.3f} s")
print(f"env-steps/sec     : {total / dt:,.0f}")
print(f"sim FPS (1 env)   : {args.steps / dt:,.0f}")
print("SMOKE_PHYSICS_OK")
