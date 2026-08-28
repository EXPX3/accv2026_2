# Variant 4: FiLM-DPT depth + V-JEPA2.1/DPT context + 128-channel VoxDet

Variant 4 is the controlled context-encoder successor to Variant 3. Both use
the exact same validation-selected FiLM-DPT depth checkpoint, stable metric
depth-to-probability conversion, calibrated OccuFly lifting, 128-channel WHD
volume, auxiliary SSC head, reference-aligned SSC losses, spatially decoupled
voxel encoder, TDP and VoxNT supervision.

The only intended architectural change from Variant 3 is the RGB context path:
Variant 3 uses a randomly initialized ResNet-50; Variant 4 reuses the frozen
V-JEPA2.1 ViT-G features at layers `[11, 23, 37, 47]` and the existing audited
geometry-aware DPT context adapter. Depth and context share the frozen V-JEPA
feature extraction, but retain separate trainable heads.

Mandatory depth checkpoint:

```text
/datatank/giridhar.vb/data/checkpoints/my_checkpoints/01_shared_film_dpt_rgb_occufly_rerun_fullsweep/lr_8e_4__wd_1e_4/dpt_film_best.pt
```

The lifted volume contract is `[B,128,96,64,64]` in OccuFly WHD order. The
training entry point `run_train_8gpu.sh` refuses to overwrite nonempty output.

For numerical compatibility with FoundationSSC's DFA3D CUDA depth sampler, the
normalized Gaussian lifting distribution includes a total uniform floor mass
of `1e-6` (each of 256 bins receives `3.90625e-9`). This prevents FP32 Gaussian
tails from becoming exact zero-support columns while changing the expected
depth by at most `4e-5` m over the configured 80 m range. It is probability
normalization at the sampler input, not downstream NaN replacement.
