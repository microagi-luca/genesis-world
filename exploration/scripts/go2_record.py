"""Headless recorder for a trained Go2 policy -> mp4 (follow camera).
Run from examples/locomotion/ so `from go2_env import Go2Env` resolves.
"""
import argparse, os, glob, pickle, re
import torch
from rsl_rl.runners import OnPolicyRunner
import genesis as gs
from go2_env import Go2Env

p = argparse.ArgumentParser()
p.add_argument("-e", "--exp_name", default="go2-walking")
p.add_argument("--ckpt", type=int, default=-1)          # -1 = latest checkpoint
p.add_argument("--seconds", type=float, default=8.0)
p.add_argument("--vx", type=float, default=0.5)         # forward command (m/s)
p.add_argument("--out", default="/tmp/go2_walk.mp4")
args = p.parse_args()

gs.init(backend=gs.gpu, precision="32", logging_level="warning")

log_dir = f"logs/{args.exp_name}"
with open(f"{log_dir}/cfgs.pkl", "rb") as f:
    env_cfg, obs_cfg, reward_cfg, command_cfg, train_cfg = pickle.load(f)
reward_cfg["reward_scales"] = {}

ckpt = args.ckpt
if ckpt < 0:
    models = glob.glob(os.path.join(log_dir, "model_*.pt"))
    ckpt = max(int(re.findall(r"model_(\d+)\.pt", os.path.basename(m))[0]) for m in models)
print("using checkpoint", ckpt)

# Inject a follow-camera into the scene right before Go2Env builds it.
_orig_build = gs.Scene.build
cap = {}
def patched_build(self, *a, **k):
    cap["cam"] = self.add_camera(res=(960, 640), pos=(2.5, -2.0, 1.4), lookat=(0, 0, 0.3), fov=40, GUI=False)
    return _orig_build(self, *a, **k)
gs.Scene.build = patched_build
env = Go2Env(num_envs=1, env_cfg=env_cfg, obs_cfg=obs_cfg, reward_cfg=reward_cfg,
             command_cfg=command_cfg, show_viewer=False)
gs.Scene.build = _orig_build
cam = cap["cam"]

runner = OnPolicyRunner(env, train_cfg, log_dir, device=gs.device)
runner.load(os.path.join(log_dir, f"model_{ckpt}.pt"))
policy = runner.get_inference_policy(device=gs.device)

obs = env.reset()
nframes = int(args.seconds / env.dt)
cam.start_recording()
with torch.no_grad():
    for i in range(nframes):
        env.commands[:, 0] = args.vx   # hold a constant forward command
        env.commands[:, 1] = 0.0
        env.commands[:, 2] = 0.0
        actions = policy(obs)
        obs, rew, done, info = env.step(actions)
        b = env.base_pos[0].detach().cpu().numpy()
        cam.set_pose(pos=(b[0] + 2.0, b[1] - 2.0, 1.2), lookat=(b[0], b[1], 0.3))
        cam.render()
cam.stop_recording(save_to_filename=args.out, fps=int(round(1.0 / env.dt)))
print("VIDEO_SAVED", args.out, os.path.exists(args.out),
      os.path.getsize(args.out) if os.path.exists(args.out) else 0)
