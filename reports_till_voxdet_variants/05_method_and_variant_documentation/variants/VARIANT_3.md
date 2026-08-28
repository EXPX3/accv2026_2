# Variant 3: FiLM-DPT depth + ResNet context + 128-channel VoxDet

Variant 3 uses the original VoxDet `resnet50(weights=None)` RGB context path,
but replaces its learned 32-bin depth branch with the checkpoint-initialized
V-JEPA2.1 FiLM-DPT depth frontend and increases the calibrated OccuFly lifted
volume to 128 channels. The downstream model uses the spatially decoupled voxel
encoder, VoxDet TDP/VoxNT, auxiliary occupancy head and reference-aligned loss
weights from Variant 2.

The mandatory depth checkpoint is:

```text
/datatank/giridhar.vb/data/checkpoints/my_checkpoints/01_shared_film_dpt_rgb_occufly_rerun_fullsweep/lr_8e_4__wd_1e_4/dpt_film_best.pt
```

The V-JEPA2.1 backbone is evaluated only for the FiLM-DPT depth branch. Its
features are not supplied to the RGB context path. The ResNet context tensor and
depth distribution first meet inside the reused calibrated OccuFly hybrid view
transformer. The required low-resolution volume is `[B,128,96,64,64]` in
OccuFly WHD order.

The selected checkpoint's `run_config.json` records a 256-channel DPT decoder,
linear depth normalization and metric range `[0.001, 80.0]` m. Those channels
were trained through `FeaturesToDepth`; they are not categorical depth-bin
logits. Variant 3 therefore uses FSSC's `gaussian_dense` adapter (sigma 1 m) to
convert the checkpoint's metric prediction into the lifting distribution. This
choice avoids the invalid alternative of applying a categorical softmax to
dense-depth features. The predicted depth maps provide direct supervision to
this branch; depth probabilities are detached from the SSC path so this direct
depth objective cannot be overridden by SSC gradients.

Both the 256-bin diagnostic distribution and its 256-bin FoundationSSC lifting
remap are normalized with a log-domain softmax of the Gaussian log density.
This is algebraically the normalized Gaussian but remains defined when a
metric prediction lies beyond the lifting volume and every direct exponential
would otherwise underflow to zero. The stable path is opt-in for Variant 3;
legacy FSSC runs retain their original numerical behavior.

Checkpoints embed the resolved depth-checkpoint path, V-JEPA checkpoint,
selected layers, grid contract, class-frequency artifact and full run config.

The reproducible eight-GPU entry point is `run_train_8gpu.sh`. It refuses to
write into a nonempty output directory.
