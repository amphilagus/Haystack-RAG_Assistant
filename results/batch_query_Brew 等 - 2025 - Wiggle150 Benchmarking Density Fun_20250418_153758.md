# BATCH QUERY RESULTS FOR TITLE: Brew 等 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform

**Collection:** jctc_recent_0418
**Timestamp:** 2025-04-18 15:37:58

---


## [1] background of this study (top_k=3)

Retrieved 3 documents

### Document 1 (score: 5.1580)

```
he structures these methods were optimized on. Future generations of xTB methods incorporating additional physics, like approximate nonlocal Fock exchange, may be able to address these shortcomings.
The 5 NNPs surveyed gave divergent performances. The models trained on materials data sets run with plane-wave PBE calculations, MACE-MP- and ORB-D3-V2 performed poorly. This is unsurprising: their training data contains few complex organic molecules like the ones shown here and few farfrom-equilibrium structures, vividly illustrating how current NNPs struggle to extrapolate beyond their training data with good quantitative accuracy. More surprising is the poor performance of SO3LR,42 which was trained on 3.5 M structures computed at the PBE0 + MBD level of theory with numerical atom-centered orbitals in FHI-aims. 
```

**Metadata:**

```json
{
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "encoding": "utf-8",
  "file_type": "md",
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "chunk_id": 29
}
```

---

### Document 2 (score: 4.9287)

```
f this article, our results highlight the reality that many research laboratories employ suboptimal methods, reducing the accuracy of the results they generate and the speed of their calculations.53
Finally, this benchmarking illustrates the remarkable progress made by NNPs over the past several years. The strained molecules studied in Wiggle150 might reasonably have been expected to serve as a "poison" set54 for machine-learning-based methods, given how few NNPs include structures like this in their training set�instead, NNPs like AIMNet2 and ANI-2x performed very well, approaching in some cases even exceeding the performance of dispersion-corrected DFT methods with quadruple-ζ basis sets. Given that improvement in NNPs continues to proceed at a rapid pace, and that considerable improvement is possible purely from scaling existing architectures to larger data sets,55 the present authors find it colorable that most quantum mechanical workflows will 1 day shift to be powered by NNPs.
```

**Metadata:**

```json
{
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "encoding": "utf-8",
  "chunk_id": 38,
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "file_type": "md"
}
```

---

### Document 3 (score: 4.7751)

```
e effect was inconsistent and small relative to the timing differences discussed in this study: calculations run in ORCA 6.0.0 completed in 91 ± 40% of the time that analogous calculations run in ORCA 5.0.4 took to complete. Given that the methods discussed in this study span approximately 17 orders of magnitude in speed, we do not anticipate that the difference between ORCA 5.0.4 and ORCA 6.0.0 will impact our conclusions.
NNP calculations and the Sage force field were run on a machine with 4 Intel Xeon E5-2666 v3 CPUs and 8 GB of memory. For NNPs, runtimes were quantified by recording the time to call get_potential_energy() in the Atomic Simulation Environment from an already initialized ase.Calculator object. For Sage, runtime was quantified by recording the time to (1) generate an openmm.State object from an already initialized openmm.Context object and (2) call getPotentialEnergy() from this object (The scripts employed have been provided in the Supporting Information). 
```

**Metadata:**

```json
{
  "encoding": "utf-8",
  "file_type": "md",
  "chunk_id": 14,
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md"
}
```

---


## [2] objective of this study (top_k=3)

Retrieved 3 documents

### Document 1 (score: 5.2628)

```
f this article, our results highlight the reality that many research laboratories employ suboptimal methods, reducing the accuracy of the results they generate and the speed of their calculations.53
Finally, this benchmarking illustrates the remarkable progress made by NNPs over the past several years. The strained molecules studied in Wiggle150 might reasonably have been expected to serve as a "poison" set54 for machine-learning-based methods, given how few NNPs include structures like this in their training set�instead, NNPs like AIMNet2 and ANI-2x performed very well, approaching in some cases even exceeding the performance of dispersion-corrected DFT methods with quadruple-ζ basis sets. Given that improvement in NNPs continues to proceed at a rapid pace, and that considerable improvement is possible purely from scaling existing architectures to larger data sets,55 the present authors find it colorable that most quantum mechanical workflows will 1 day shift to be powered by NNPs.
```

**Metadata:**

```json
{
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "encoding": "utf-8",
  "chunk_id": 38,
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "file_type": "md"
}
```

---

### Document 2 (score: 4.7984)

```
nchmarking Methods. We surveyed a wide variety of computational methods: 2 post-Hartree−Fock methods, 17 density functionals, 4 composite methods, 4 semiempirical methods, 5 NNPs, and 2 force fields. All calculations were run through ORCA 5.0.420 except for: r2SCAN-3c and ωB97X-3c which were run in ORCA 6.0.0; the NNPs, which were run through the Atomic Simulation Environment;21 and the Sage22 force field, which was run through OpenMM.23 Unless otherwise specified, DFT calculations were run using the def2- QZVP24 basis set and wave function-based methods were run using the cc-pVQZ25 basis set. Double hybrid methods were run with automatically generated auxiliary basis sets using the AutoAux keyword.26 DLPNO27 calculations were run with corresponding cc-pVnZ/C auxiliary basis sets and the TightPNO setting applied. 
```

**Metadata:**

```json
{
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "encoding": "utf-8",
  "file_type": "md",
  "chunk_id": 10
}
```

---

### Document 3 (score: 4.7529)

```
he structures these methods were optimized on. Future generations of xTB methods incorporating additional physics, like approximate nonlocal Fock exchange, may be able to address these shortcomings.
The 5 NNPs surveyed gave divergent performances. The models trained on materials data sets run with plane-wave PBE calculations, MACE-MP- and ORB-D3-V2 performed poorly. This is unsurprising: their training data contains few complex organic molecules like the ones shown here and few farfrom-equilibrium structures, vividly illustrating how current NNPs struggle to extrapolate beyond their training data with good quantitative accuracy. More surprising is the poor performance of SO3LR,42 which was trained on 3.5 M structures computed at the PBE0 + MBD level of theory with numerical atom-centered orbitals in FHI-aims. 
```

**Metadata:**

```json
{
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "encoding": "utf-8",
  "file_type": "md",
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "chunk_id": 29
}
```

---


## [3] methods of this study (top_k=3)

Retrieved 3 documents

### Document 1 (score: 6.8885)

```
nchmarking Methods. We surveyed a wide variety of computational methods: 2 post-Hartree−Fock methods, 17 density functionals, 4 composite methods, 4 semiempirical methods, 5 NNPs, and 2 force fields. All calculations were run through ORCA 5.0.420 except for: r2SCAN-3c and ωB97X-3c which were run in ORCA 6.0.0; the NNPs, which were run through the Atomic Simulation Environment;21 and the Sage22 force field, which was run through OpenMM.23 Unless otherwise specified, DFT calculations were run using the def2- QZVP24 basis set and wave function-based methods were run using the cc-pVQZ25 basis set. Double hybrid methods were run with automatically generated auxiliary basis sets using the AutoAux keyword.26 DLPNO27 calculations were run with corresponding cc-pVnZ/C auxiliary basis sets and the TightPNO setting applied. 
```

**Metadata:**

```json
{
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "encoding": "utf-8",
  "file_type": "md",
  "chunk_id": 10
}
```

---

### Document 2 (score: 6.0789)

```
he structures these methods were optimized on. Future generations of xTB methods incorporating additional physics, like approximate nonlocal Fock exchange, may be able to address these shortcomings.
The 5 NNPs surveyed gave divergent performances. The models trained on materials data sets run with plane-wave PBE calculations, MACE-MP- and ORB-D3-V2 performed poorly. This is unsurprising: their training data contains few complex organic molecules like the ones shown here and few farfrom-equilibrium structures, vividly illustrating how current NNPs struggle to extrapolate beyond their training data with good quantitative accuracy. More surprising is the poor performance of SO3LR,42 which was trained on 3.5 M structures computed at the PBE0 + MBD level of theory with numerical atom-centered orbitals in FHI-aims. 
```

**Metadata:**

```json
{
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "encoding": "utf-8",
  "file_type": "md",
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "chunk_id": 29
}
```

---

### Document 3 (score: 5.6843)

```
f this article, our results highlight the reality that many research laboratories employ suboptimal methods, reducing the accuracy of the results they generate and the speed of their calculations.53
Finally, this benchmarking illustrates the remarkable progress made by NNPs over the past several years. The strained molecules studied in Wiggle150 might reasonably have been expected to serve as a "poison" set54 for machine-learning-based methods, given how few NNPs include structures like this in their training set�instead, NNPs like AIMNet2 and ANI-2x performed very well, approaching in some cases even exceeding the performance of dispersion-corrected DFT methods with quadruple-ζ basis sets. Given that improvement in NNPs continues to proceed at a rapid pace, and that considerable improvement is possible purely from scaling existing architectures to larger data sets,55 the present authors find it colorable that most quantum mechanical workflows will 1 day shift to be powered by NNPs.
```

**Metadata:**

```json
{
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "encoding": "utf-8",
  "chunk_id": 38,
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "file_type": "md"
}
```

---


## [4] results of this study (top_k=5)

Retrieved 5 documents

### Document 1 (score: 6.1691)

```
f this article, our results highlight the reality that many research laboratories employ suboptimal methods, reducing the accuracy of the results they generate and the speed of their calculations.53
Finally, this benchmarking illustrates the remarkable progress made by NNPs over the past several years. The strained molecules studied in Wiggle150 might reasonably have been expected to serve as a "poison" set54 for machine-learning-based methods, given how few NNPs include structures like this in their training set�instead, NNPs like AIMNet2 and ANI-2x performed very well, approaching in some cases even exceeding the performance of dispersion-corrected DFT methods with quadruple-ζ basis sets. Given that improvement in NNPs continues to proceed at a rapid pace, and that considerable improvement is possible purely from scaling existing architectures to larger data sets,55 the present authors find it colorable that most quantum mechanical workflows will 1 day shift to be powered by NNPs.
```

**Metadata:**

```json
{
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "encoding": "utf-8",
  "chunk_id": 38,
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "file_type": "md"
}
```

---

### Document 2 (score: 6.0800)

```
e effect was inconsistent and small relative to the timing differences discussed in this study: calculations run in ORCA 6.0.0 completed in 91 ± 40% of the time that analogous calculations run in ORCA 5.0.4 took to complete. Given that the methods discussed in this study span approximately 17 orders of magnitude in speed, we do not anticipate that the difference between ORCA 5.0.4 and ORCA 6.0.0 will impact our conclusions.
NNP calculations and the Sage force field were run on a machine with 4 Intel Xeon E5-2666 v3 CPUs and 8 GB of memory. For NNPs, runtimes were quantified by recording the time to call get_potential_energy() in the Atomic Simulation Environment from an already initialized ase.Calculator object. For Sage, runtime was quantified by recording the time to (1) generate an openmm.State object from an already initialized openmm.Context object and (2) call getPotentialEnergy() from this object (The scripts employed have been provided in the Supporting Information). 
```

**Metadata:**

```json
{
  "encoding": "utf-8",
  "file_type": "md",
  "chunk_id": 14,
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md"
}
```

---

### Document 3 (score: 5.6660)

```
he structures these methods were optimized on. Future generations of xTB methods incorporating additional physics, like approximate nonlocal Fock exchange, may be able to address these shortcomings.
The 5 NNPs surveyed gave divergent performances. The models trained on materials data sets run with plane-wave PBE calculations, MACE-MP- and ORB-D3-V2 performed poorly. This is unsurprising: their training data contains few complex organic molecules like the ones shown here and few farfrom-equilibrium structures, vividly illustrating how current NNPs struggle to extrapolate beyond their training data with good quantitative accuracy. More surprising is the poor performance of SO3LR,42 which was trained on 3.5 M structures computed at the PBE0 + MBD level of theory with numerical atom-centered orbitals in FHI-aims. 
```

**Metadata:**

```json
{
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "encoding": "utf-8",
  "file_type": "md",
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "chunk_id": 29
}
```

---

### Document 4 (score: 5.6424)

```
ith only slightly increased error. (The systems investigated in this study are relatively small, and the speedup possible with pure functionals is likely to increase for larger or periodic systems.)
Among low-cost DFT methods, r2SCAN-3c stands out. The most commonly used strategy for reducing the cost of DFT simulations is to employ a double-ζ basis set, often 6-31G(d). Relative to r2SCAN-3c, both B3LYP-D3BJ/6-31G(d) and ωB97X/6-31G(d) give worse accuracy and worse performance and should be avoided for production use. We note that this study has not comprehensively surveyed many basis-set effects; we leave thissubstantial task to future work, with the observation that many commonly used basis sets may not be Paretoefficient.47,48
If faster methods than r2SCAN-3c are desired, AIMNet2 is the best choice by far. AIMNet2 offers comparable accuracy to B97- 3c while running approximately 8 orders of magnitude faster� faster than every semiempirical method, and even faster than GFN-FF. 
```

**Metadata:**

```json
{
  "file_type": "md",
  "encoding": "utf-8",
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "chunk_id": 34
}
```

---

### Document 5 (score: 5.5588)

```
 is r2SCAN-D4, the second revision of Sun, Ruzsinszky, and Perdew's fully constrained meta-GGA functional. r2SCAN-D4 gives an MAE of 1.16 vs 0.86 kcal/mol for ωB97M-V and runs almost 6 times faster.
Taken in aggregate, the results of this study support the commonly held idea that ascending the "Jacob's Ladder" of increasing DFT complexity will lead to improved performance. On average, hybrid density functionals performed better than non-hybrid/"pure" density functionals, and meta-GGA functionals performed better than GGA functionals among both pure and hybrid functionals. Nevertheless, the second-best nondouble-hybrid functional is r2SCAN-D4 and other pure meta-GGA functionals�M06-L and B97M-D4�performed about as well as common hybrid functionals like M06-2X, B3LYP, and PBE0. 
```

**Metadata:**

```json
{
  "chunk_id": 25,
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "file_type": "md",
  "encoding": "utf-8",
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md"
}
```

---


## [5] discussion of this study (top_k=5)

Retrieved 5 documents

### Document 1 (score: 4.7883)

```
f this article, our results highlight the reality that many research laboratories employ suboptimal methods, reducing the accuracy of the results they generate and the speed of their calculations.53
Finally, this benchmarking illustrates the remarkable progress made by NNPs over the past several years. The strained molecules studied in Wiggle150 might reasonably have been expected to serve as a "poison" set54 for machine-learning-based methods, given how few NNPs include structures like this in their training set�instead, NNPs like AIMNet2 and ANI-2x performed very well, approaching in some cases even exceeding the performance of dispersion-corrected DFT methods with quadruple-ζ basis sets. Given that improvement in NNPs continues to proceed at a rapid pace, and that considerable improvement is possible purely from scaling existing architectures to larger data sets,55 the present authors find it colorable that most quantum mechanical workflows will 1 day shift to be powered by NNPs.
```

**Metadata:**

```json
{
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "encoding": "utf-8",
  "chunk_id": 38,
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "file_type": "md"
}
```

---

### Document 2 (score: 4.6393)

```
he structures these methods were optimized on. Future generations of xTB methods incorporating additional physics, like approximate nonlocal Fock exchange, may be able to address these shortcomings.
The 5 NNPs surveyed gave divergent performances. The models trained on materials data sets run with plane-wave PBE calculations, MACE-MP- and ORB-D3-V2 performed poorly. This is unsurprising: their training data contains few complex organic molecules like the ones shown here and few farfrom-equilibrium structures, vividly illustrating how current NNPs struggle to extrapolate beyond their training data with good quantitative accuracy. More surprising is the poor performance of SO3LR,42 which was trained on 3.5 M structures computed at the PBE0 + MBD level of theory with numerical atom-centered orbitals in FHI-aims. 
```

**Metadata:**

```json
{
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "encoding": "utf-8",
  "file_type": "md",
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "chunk_id": 29
}
```

---

### Document 3 (score: 4.0857)

```
e effect was inconsistent and small relative to the timing differences discussed in this study: calculations run in ORCA 6.0.0 completed in 91 ± 40% of the time that analogous calculations run in ORCA 5.0.4 took to complete. Given that the methods discussed in this study span approximately 17 orders of magnitude in speed, we do not anticipate that the difference between ORCA 5.0.4 and ORCA 6.0.0 will impact our conclusions.
NNP calculations and the Sage force field were run on a machine with 4 Intel Xeon E5-2666 v3 CPUs and 8 GB of memory. For NNPs, runtimes were quantified by recording the time to call get_potential_energy() in the Atomic Simulation Environment from an already initialized ase.Calculator object. For Sage, runtime was quantified by recording the time to (1) generate an openmm.State object from an already initialized openmm.Context object and (2) call getPotentialEnergy() from this object (The scripts employed have been provided in the Supporting Information). 
```

**Metadata:**

```json
{
  "encoding": "utf-8",
  "file_type": "md",
  "chunk_id": 14,
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md"
}
```

---

### Document 4 (score: 4.0249)

```
ith only slightly increased error. (The systems investigated in this study are relatively small, and the speedup possible with pure functionals is likely to increase for larger or periodic systems.)
Among low-cost DFT methods, r2SCAN-3c stands out. The most commonly used strategy for reducing the cost of DFT simulations is to employ a double-ζ basis set, often 6-31G(d). Relative to r2SCAN-3c, both B3LYP-D3BJ/6-31G(d) and ωB97X/6-31G(d) give worse accuracy and worse performance and should be avoided for production use. We note that this study has not comprehensively surveyed many basis-set effects; we leave thissubstantial task to future work, with the observation that many commonly used basis sets may not be Paretoefficient.47,48
If faster methods than r2SCAN-3c are desired, AIMNet2 is the best choice by far. AIMNet2 offers comparable accuracy to B97- 3c while running approximately 8 orders of magnitude faster� faster than every semiempirical method, and even faster than GFN-FF. 
```

**Metadata:**

```json
{
  "file_type": "md",
  "encoding": "utf-8",
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "chunk_id": 34
}
```

---

### Document 5 (score: 3.9592)

```
es it a valuable addition to the computational chemistry canon, and we anticipate that this benchmark will prove useful in guiding the creation of future generations of density functionals and NNPs.
Our results also show the impact of modern density functionals. Many of the Pareto-optimal DFT methods are quite new: ωB97M-V50 was released in 2016, B97M-V51 &amp; r2SCAN52 in 2020, and r2SCAN-3c39 in 2021. As a result, many commonly used software packages do not contain these methods. While a broader discussion of the dynamics of the scientific software ecosystem is outside the scope of this article, our results highlight the reality that many research laboratories employ suboptimal methods, reducing the accuracy of the results they generate and the speed of their calculations.53
F
```

**Metadata:**

```json
{
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "chunk_id": 37,
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "encoding": "utf-8",
  "file_type": "md"
}
```

---


## [6] Research Field (top_k=2)

Retrieved 2 documents

### Document 1 (score: 5.9139)

```
f this article, our results highlight the reality that many research laboratories employ suboptimal methods, reducing the accuracy of the results they generate and the speed of their calculations.53
Finally, this benchmarking illustrates the remarkable progress made by NNPs over the past several years. The strained molecules studied in Wiggle150 might reasonably have been expected to serve as a "poison" set54 for machine-learning-based methods, given how few NNPs include structures like this in their training set�instead, NNPs like AIMNet2 and ANI-2x performed very well, approaching in some cases even exceeding the performance of dispersion-corrected DFT methods with quadruple-ζ basis sets. Given that improvement in NNPs continues to proceed at a rapid pace, and that considerable improvement is possible purely from scaling existing architectures to larger data sets,55 the present authors find it colorable that most quantum mechanical workflows will 1 day shift to be powered by NNPs.
```

**Metadata:**

```json
{
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "encoding": "utf-8",
  "chunk_id": 38,
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "file_type": "md"
}
```

---

### Document 2 (score: 4.9837)

```
es it a valuable addition to the computational chemistry canon, and we anticipate that this benchmark will prove useful in guiding the creation of future generations of density functionals and NNPs.
Our results also show the impact of modern density functionals. Many of the Pareto-optimal DFT methods are quite new: ωB97M-V50 was released in 2016, B97M-V51 &amp; r2SCAN52 in 2020, and r2SCAN-3c39 in 2021. As a result, many commonly used software packages do not contain these methods. While a broader discussion of the dynamics of the scientific software ecosystem is outside the scope of this article, our results highlight the reality that many research laboratories employ suboptimal methods, reducing the accuracy of the results they generate and the speed of their calculations.53
F
```

**Metadata:**

```json
{
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "chunk_id": 37,
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "encoding": "utf-8",
  "file_type": "md"
}
```

---


## [7] Received Revised Accepted (top_k=2)

Retrieved 2 documents

### Document 1 (score: 5.3597)

```
rid meta-GGA functional ωB97M-V, which uses the Vydrov−van Voorhis nonlocal dispersion correction.35,36 Matching results obtained by Santra and Martin,37 replacing the VV10 correction with the simpler D3BJ correction leads to a slight decrease in accuracy, although the resulting functional still has the third-lowest MAE of all non-double-hybrid functionals studied. Older hybrid functionals like ωB97X-D3, ωB97X-V, M06-2X, PBE0, and B3LYP all perform somewhat worse, with PBE0 giving the most consistent performance.
The second-best non-double-hybrid functional is r2SCAN-D4, the second revision of Sun, Ruzsinszky, and Perdew's fully constrained meta-GGA functional. r2SCAN-D4 gives an MAE of 1.16 vs 0.86 kcal/mol for ωB97M-V and runs almost 6 times faster.
T
```

**Metadata:**

```json
{
  "encoding": "utf-8",
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "file_type": "md",
  "chunk_id": 24
}
```

---

### Document 2 (score: 3.3990)

```
3               | 0.88              | 15,300   |
| DSD-PBEP86         | 0.90               | 0.72              | 2580     |
| B2PLYP             | 1.43               | 1.11              | 2510     |
| ωB97M-V            | 1.18               | 0.87              | 1990     |
| ωB97M-D3BJ         | 1.59               | 1.18              | 1970     |
| ωB97X-V            | 2.72               | 2.41              | 1930     |
| ωB97X-D3           | 3.00               | 2.49              | 1870     |
| ωB97X/6-31G(d)     | 5.54               | 5.24              | 180      |
| PBE0-D3BJ          | 1.51               | 1.19              | 1350     |
| B3LYP-D3BJ         | 1.84               | 1.41              | 1370     |
| M06                | 2.24               | 1.79              | 1450     |
| M06-2X             | 2.42               | 1.97              | 1460     |
| B3LYP-D3BJ/631G(d) | 4.01               | 3.46              | 105      |
|
```

**Metadata:**

```json
{
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "file_type": "md",
  "encoding": "utf-8",
  "chunk_id": 20
}
```

---


## [8] DOI (top_k=2)

Retrieved 2 documents

### Document 1 (score: 3.3963)

```
9               | 1.72              | 57.9     |
| B97-3c             | 2.96               | 2.32              | 43.3     |
| ωB97x-3c           | 4.63               | 4.12              | 377      |
| HF-3c              | 26.4               | 24.9              | 7.27     |
| PM3                | 12.2               | 9.48              | 1.22     |
| AM1                | 14.2               | 11.1              | 1.28     |
| GFN1-xTB           | 15.1               | 14.4              | 2.62     |
| GFN2-xTB           | 15.2               | 14.6              | 3.21     |
| AIMNet2            | 3.13               | 2.39              | 0.0170   |
| ANI-2X             | 5.41               | 4.41              | 0.0128   |
| SO3LR              | 10.6               | 9.39              | 4.73     |
| Orb-V2-D3          | 11.1               | 9.25              | 0.216    |
| MACE-MP-0          | 28.5               | 26.6              | 0.272    |
|
```

**Metadata:**

```json
{
  "chunk_id": 22,
  "encoding": "utf-8",
  "file_type": "md",
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform"
}
```

---

### Document 2 (score: 3.3573)

```
4               | 1.79              | 1450     |
| M06-2X             | 2.42               | 1.97              | 1460     |
| B3LYP-D3BJ/631G(d) | 4.01               | 3.46              | 105      |
| r2SCAN-D4          | 1.50               | 1.16              | 345      |
| M06-L              | 1.72               | 1.40              | 350      |
| B97M-D4            | 1.84               | 1.43              | 353      |
| B97-D              | 4.26               | 3.37              | 263      |
| BLYP-D3BJ          | 5.00               | 3.93              | 249      |
| BP86-D3BJ          | 5.44               | 4.57              | 256      |
| PBE-D3BJ           | 5.68               | 4.91              | 244      |
| r2SCAN-3c          | 2.19               | 1.72              | 57.9     |
| B97-3c             | 2.96               | 2.32              | 43.3     |
| ωB97x-3c           | 4.63               | 4.12              | 377      |
|
```

**Metadata:**

```json
{
  "title": "Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform",
  "file_type": "md",
  "source": "raw_data/jctc_recent/cleaned\\Brew \u7b49 - 2025 - Wiggle150 Benchmarking Density Functionals and Neural Network Potentials on Highly Strained Conform.md",
  "encoding": "utf-8",
  "chunk_id": 21
}
```

---

