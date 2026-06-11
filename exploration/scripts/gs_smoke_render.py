"""Smoke test 2: render the simulation to an mp4 ("video") on macOS.
Uses the Rasterizer (Pyrender/OpenGL) path, which is the macOS-friendly renderer.
"""
import os
import math
import genesis as gs

gs.init(backend=gs.gpu, precision="32")

scene = gs.Scene(
    show_viewer=False,
    renderer=gs.renderers.Rasterizer(),
    rigid_options=gs.options.RigidOptions(dt=0.01),
)
scene.add_entity(gs.morphs.Plane())
franka = scene.add_entity(gs.morphs.MJCF(file="xml/franka_emika_panda/panda.xml"))

# Drop a few cubes so there's visible motion in the clip.
for i in range(3):
    scene.add_entity(gs.morphs.Box(size=(0.1, 0.1, 0.1), pos=(0.2 * i - 0.2, 0.0, 0.6 + 0.15 * i)))

cam = scene.add_camera(res=(640, 480), pos=(3.0, 0.0, 1.5), lookat=(0, 0, 0.4), fov=40, GUI=False)
scene.build()

# Single-frame render first — proves the renderer returns pixels.
rgb, *_ = cam.render(rgb=True)
print("single-frame rgb shape:", None if rgb is None else rgb.shape)

cam.start_recording()
for i in range(120):
    scene.step()
    cam.set_pose(pos=(3.0 * math.cos(i / 60), 3.0 * math.sin(i / 60), 1.5), lookat=(0, 0, 0.4))
    cam.render()
out = os.path.join(os.path.dirname(__file__), "genesis_demo.mp4")
cam.stop_recording(save_to_filename=out, fps=30)
print("saved video:", out, "exists:", os.path.exists(out), "bytes:", os.path.getsize(out) if os.path.exists(out) else 0)
print("SMOKE_RENDER_OK")
