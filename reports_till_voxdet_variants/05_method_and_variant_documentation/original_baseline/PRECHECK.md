# Pre-training verification

- Reference checkout reused without modification: `VoxDet`, commit
  `e10d8280de96d4f03f54b616e57e7c6754044fa4`, branch `wacv27-support`.
- The archived MMDetection3D 0.17.1 build was tested in an isolated copy of
  the compatible Python 3.7/CUDA 11.3 environment.  Its sparse extension
  cannot build against installed `spconv-cu113==2.3.6`: it requires removed
  spconv-1 headers such as `spconv/geometry.h`; CUDA 11.3 also rejects the
  host compiler without an unsupported override.  The reference checkout was
  not changed.
- Selected runtime: existing `occufly_foundationssc_py311_torch21`
  (Python 3.11, Torch 2.1.0+cu118, CUDA available, torchvision deformable
  convolution available).  A real CUDA forward/backward completed.
- Immutable VoxNT coverage: 14,804 train, 1,965 val, 3,842 test samples;
  every source sample has one NPZ.  See `voxnt_audit_pretraining.json`.
- Axis contract: `W,H,D = camera-right,camera-down,camera-forward`, full
  shape `(192,128,128)`, directions `(w+,w-,h+,h-,d+,d-)`.  `valid_whd` is
  unpacked with `np.unpackbits(..., count=prod(shape_whd))`.
- The original reference uses `img_metas["stereo_depth"]` in its forward and
  proposal path.  This adapter intentionally uses learned depth probabilities
  only; OccuFly depth maps are not model inputs.
