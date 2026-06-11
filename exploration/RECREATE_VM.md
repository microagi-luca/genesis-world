# Recreate the RTX PRO 6000 VM from the saved image

A **custom disk image** of the eval VM (`luca4genesis`) was saved so the *ready-to-run
environment* (nvidia-open driver 610.43.02, CUDA 12.8 venv, `genesis-world` + torch, Go2 logs)
survives VM deletion — no driver re-install / `nvidia-open` dance needed.

- **Image:** `genesis-rtx6000-img`  (family `genesis-rtx6000`), project `research-490608`, region `europe-west2`
- **Source VM config:** `g4-standard-48`, 1× `nvidia-rtx-pro-6000` (Blackwell, 96GB), 100GB boot disk, SPOT
- (Machine images are **not** supported for the G4 series, so this is a boot-disk image; you re-specify the machine config below.)

## Recreate the VM
```bash
gcloud compute instances create luca4genesis-2 \
  --zone=europe-west2-b \
  --machine-type=g4-standard-48 \
  --image=genesis-rtx6000-img \
  --image-project=research-490608 \
  --boot-disk-size=100GB \
  --maintenance-policy=TERMINATE \
  --provisioning-model=SPOT \
  --instance-termination-action=STOP
```
Notes:
- On the **G4 series the RTX PRO 6000 is bundled with `g4-standard-48`** (no `--accelerator` needed).
  If gcloud ever asks for one, add: `--accelerator=type=nvidia-rtx-pro-6000,count=1`.
- Drop `--provisioning-model=SPOT --instance-termination-action=STOP` for a non-preemptible VM.
- GPU **quota/availability in the zone** still applies; try another zone if capacity is short.

## After it boots — verify the env is intact
```bash
gcloud compute ssh luca4genesis-2 --zone=europe-west2-b --command='nvidia-smi --query-gpu=name,driver_version --format=csv,noheader; cd ~/genesis-world && .venv/bin/python -c "import genesis, torch; print(genesis.__version__, torch.cuda.is_available())"'
```

## Housekeeping
- The image itself costs a small monthly storage fee (~a few GB compressed). Delete when no longer needed:
  `gcloud compute images delete genesis-rtx6000-img`
- List images: `gcloud compute images list --no-standard-images`
