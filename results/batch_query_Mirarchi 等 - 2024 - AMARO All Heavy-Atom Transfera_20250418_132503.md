# BATCH QUERY RESULTS FOR TITLE: Mirarchi 等 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics

**Collection:** jctc_recent_0417
**Timestamp:** 2025-04-18 13:25:03

---


## [1] Abstract (top_k=3)

Retrieved 3 documents

### Document 1 (score: 8.0807)

```
(20) Das, R.; Baker, D. Macromolecular modeling with rosetta.
Annu. Rev. Biochem. 2008, 77, 363−382.
(21) Foley, T. T.; Kidder, K. M.; Shell, M. S.; Noid, W. Exploring
the landscape of model representations. Proc. Natl. Acad. Sci. U. S. A.
2020, 117, 24061−24068.
(22) Boninsegna, L.; Banisch, R.; Clementi, C. A data-driven
perspective on the hierarchical assembly of molecular structures. J.
Chem. Theory Comput. 2018, 14, 453−460.
(23) Jin, J.; Pak, A. J.; Durumeric, A. E.; Loose, T. D.; Voth, G. A.
Bottom-up coarse-graining: Principles and perspectives. J. Chem.
Theory Comput. 2022, 18, 5759−5791.
(24) Navarro, C.; Majewski, M.; De Fabritiis, G. Top-down machine
learning of coarse-grained protein force-fields. arXiv, 2306.11375,
2023.
(25) Noé, F.; Tkatchenko, A.; Mu ̈ ller, K.-R.; Clementi, C. Machine
learning for molecular simulation. Annu. Rev. Phys. Chem. 2020, 71,
361−390.
(26) Behler, J.; Parrinello, M. Generalized neural-network
r
```

**Metadata:**

```json
{
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics",
  "chunk_id": 0,
  "file_type": "pdf",
  "source": "raw_data/jctc_recent\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.pdf",
  "page": 8
}
```

---

### Document 2 (score: 7.7450)

```
 via the loss function
$$L_{\rm FM}(\theta) = \frac{1}{\sum_{k=1}^{K} N_k} \sum_{k=1}^{K} \sum_{i=1}^{N_k} ||-\nabla_{\mathbf{R}_i^k} \mathcal{U}(\mathbf{R}^k; \theta) - \mathbf{F}_i^k||^2 \tag{2}$$
where  $N_k$  is the number of beads in conformation  $k$ , and  $K$  is the total number of conformations in a batch. Predicted forces are obtained as the negative gradient of the potential energy  $\tilde{U}$  with respect to the noh-bead coordinates R, and F represents the labeled coarse-grained forces.
2.4. Data Set. The mdCATH data set8 was the basis for applying the coarse-grained mapping approach. Specifically, the initial data were processed to retain only the heavy atoms' coordinates and forces, with a basic force aggregation map applied to the latter. Additionally, the z data set within each HDF5 file was modified to serve as the embedding for each system. 
```

**Metadata:**

```json
{
  "chunk_id": 14,
  "source": "raw_data/jctc_recent\\md\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.md",
  "file_type": "md",
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics",
  "encoding": "utf-8"
}
```

---

### Document 3 (score: 7.6159)

```
 Vanden-Eijnden, E.; Reich, L.; Weikl, T. R. Constructing the equilibrium ensemble of folding pathways from short off-equilibrium simulations. Proc. Natl. Acad. Sci. U. S. A. 2009, 106, 19011−19016.
(6) Muller, M. P.; Jiang, T.; Sun, C.; Lihan, M.; Pant, S.; Mahinthichaichan, P.; Trifan, A.; Tajkhorshid, E. Characterization of lipid-protein interactions and lipid-mediated modulation of membrane protein function through molecular simulation. Chem. Rev. 2019, 119, 6086−6161.
(7) McGeagh, J. D.; Ranaghan, K. E.; Mulholland, A. J. Protein dynamics and enzyme catalysis: insights from simulations. Biochimica et Biophysica Acta (BBA)-Proteins and Proteomics 2011, 1814, 1077− 1092.
(8) Mirarchi, A.; Giorgino, T.; Fabritiis, G. D. mdCATH: A Large-Scale MD Dataset for Data-Driven Computational Biophysics. arXiv, 2407.14794, 2024.
(
```

**Metadata:**

```json
{
  "file_type": "md",
  "chunk_id": 43,
  "source": "raw_data/jctc_recent\\md\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.md",
  "encoding": "utf-8",
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics"
}
```

---


## [2] Introduction (top_k=3)

Retrieved 3 documents

### Document 1 (score: 5.4207)

```
(20) Das, R.; Baker, D. Macromolecular modeling with rosetta.
Annu. Rev. Biochem. 2008, 77, 363−382.
(21) Foley, T. T.; Kidder, K. M.; Shell, M. S.; Noid, W. Exploring
the landscape of model representations. Proc. Natl. Acad. Sci. U. S. A.
2020, 117, 24061−24068.
(22) Boninsegna, L.; Banisch, R.; Clementi, C. A data-driven
perspective on the hierarchical assembly of molecular structures. J.
Chem. Theory Comput. 2018, 14, 453−460.
(23) Jin, J.; Pak, A. J.; Durumeric, A. E.; Loose, T. D.; Voth, G. A.
Bottom-up coarse-graining: Principles and perspectives. J. Chem.
Theory Comput. 2022, 18, 5759−5791.
(24) Navarro, C.; Majewski, M.; De Fabritiis, G. Top-down machine
learning of coarse-grained protein force-fields. arXiv, 2306.11375,
2023.
(25) Noé, F.; Tkatchenko, A.; Mu ̈ ller, K.-R.; Clementi, C. Machine
learning for molecular simulation. Annu. Rev. Phys. Chem. 2020, 71,
361−390.
(26) Behler, J.; Parrinello, M. Generalized neural-network
r
```

**Metadata:**

```json
{
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics",
  "chunk_id": 0,
  "file_type": "pdf",
  "source": "raw_data/jctc_recent\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.pdf",
  "page": 8
}
```

---

### Document 2 (score: 5.0247)

```
 via the loss function
$$L_{\rm FM}(\theta) = \frac{1}{\sum_{k=1}^{K} N_k} \sum_{k=1}^{K} \sum_{i=1}^{N_k} ||-\nabla_{\mathbf{R}_i^k} \mathcal{U}(\mathbf{R}^k; \theta) - \mathbf{F}_i^k||^2 \tag{2}$$
where  $N_k$  is the number of beads in conformation  $k$ , and  $K$  is the total number of conformations in a batch. Predicted forces are obtained as the negative gradient of the potential energy  $\tilde{U}$  with respect to the noh-bead coordinates R, and F represents the labeled coarse-grained forces.
2.4. Data Set. The mdCATH data set8 was the basis for applying the coarse-grained mapping approach. Specifically, the initial data were processed to retain only the heavy atoms' coordinates and forces, with a basic force aggregation map applied to the latter. Additionally, the z data set within each HDF5 file was modified to serve as the embedding for each system. 
```

**Metadata:**

```json
{
  "chunk_id": 14,
  "source": "raw_data/jctc_recent\\md\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.md",
  "file_type": "md",
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics",
  "encoding": "utf-8"
}
```

---

### Document 3 (score: 4.9234)

```
F) is used to describe the free energy landscape of a system as a function of a collective coordinate or reaction coordinate, which is in other terms a configurational free energy in a reduced space. The term "many-body" in the context of a CG model refers to the fact that the potential energy landscape is considered in terms of interactions between groups of atoms rather than individual atoms, and network models offer a straightforward approximation in this context.13 Our machine learning model of choice in this work is TensorNet,9 a new neural network architecture that integrates O(3)-equivariance in message-passing and utilizes rank-2 Cartesian tensor representations. O(3)-equivariant NNPs35−37 ensuring that tensor outputs transform correctly under rotations and reflections. In practice, in this work, we only predict the scalar energy, therefore invariance would have been enough. 
```

**Metadata:**

```json
{
  "file_type": "md",
  "source": "raw_data/jctc_recent\\md\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.md",
  "encoding": "utf-8",
  "chunk_id": 8,
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics"
}
```

---


## [3] Background (top_k=3)

Retrieved 3 documents

### Document 1 (score: 4.7720)

```
ompared the areas of
the TICA landscapes recovered by both models, see Figure 6.
The starting point (blue dot), the same for both cases, was
selected randomly and resulted in a conformation near the
global minimum, while the red star represents the crystal
structure (PDB ID: 2A3D).
The all-atom simulation (left panel) explores a more
localized region of the TICA space, with the trajectory
(black arrows) predominantly staying within a single basin.
This indicates limited sampling within the time frame due to
the high dimensionality and energy barriers typical of fully
atomistic representations. The final conformation is marked by
a yellow dot, indicating that the simulation does not move
significantly away from the initial state.
In contrast, the CG-NNP simulation (right panel), despite
the shorter trajectory length, explores a broader region of the
conformational space (red arrows), as seen by the wider spread
of sampled conformations. The trajectory covers a larger
p
```

**Metadata:**

```json
{
  "chunk_id": 1,
  "page": 6,
  "source": "raw_data/jctc_recent\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.pdf",
  "file_type": "pdf",
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics"
}
```

---

### Document 2 (score: 4.4535)

```
3.3. Recovering the Energetic Landscape. For three of
the four fast-folding proteins the TICA landscape has been
successfully recovered, see Figure 4. In contrast, for α3D, the
recovery is only partial, with most microstates populating a
middle region between the global minimum on the right and a
local minimum on the left. This behavior could be attributed to
the particular secondary structure of α3D, which is
characterized by a high proportion of α-helices. Additionally,
the relative shape anisotropy (RSA) of the system, 0.3, may not
be well-represented in the training data set, which has an
average RSA of 0.17 ± 0.16. This discrepancy, coupled with
the larger system size and the presence of NH
3
+
groups in the
unstructured region between the first and second helices of the
folded state, could contribute to the observed differences.
While Figure 4 displays the two TICA dimensions as the
principal axes and uses free energy as the third dimension,
F
```

**Metadata:**

```json
{
  "chunk_id": 0,
  "source": "raw_data/jctc_recent\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.pdf",
  "file_type": "pdf",
  "page": 5,
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics"
}
```

---

### Document 3 (score: 4.1281)

```
d second helices of the
folded state, could contribute to the observed differences.
While Figure 4 displays the two TICA dimensions as the
principal axes and uses free energy as the third dimension,
Figure S3 presents the free energy on the y-axis, providing a
quantitative analysis. For the simplest target, Chignolin, the
absolute minimum is perfectly captured by AMARO. For more
complex structures like Trp-Cage and Villin, the overall shape
of the profile is well approximated. Conversely, for α3D,
extensive sampling in the central region results in a shift,
leading to the identification of an absolute minimum between
the two minima.
3.4. Sampling the Native Structures of Unseen
Training Proteins. Analysis of the CG simulations using
MSMs, detailed in Section 2.6 and Table S7, revealed that the
model successfully reproduced the experimental structure of
the corresponding fast-folding proteins, as illustrated in Figure
5a. Sampling originated from the native macrostate, defined as
t
```

**Metadata:**

```json
{
  "page": 5,
  "chunk_id": 1,
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics",
  "file_type": "pdf",
  "source": "raw_data/jctc_recent\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.pdf"
}
```

---


## [4] Method (top_k=3)

Retrieved 3 documents

### Document 1 (score: 7.1197)

```
 via the loss function
$$L_{\rm FM}(\theta) = \frac{1}{\sum_{k=1}^{K} N_k} \sum_{k=1}^{K} \sum_{i=1}^{N_k} ||-\nabla_{\mathbf{R}_i^k} \mathcal{U}(\mathbf{R}^k; \theta) - \mathbf{F}_i^k||^2 \tag{2}$$
where  $N_k$  is the number of beads in conformation  $k$ , and  $K$  is the total number of conformations in a batch. Predicted forces are obtained as the negative gradient of the potential energy  $\tilde{U}$  with respect to the noh-bead coordinates R, and F represents the labeled coarse-grained forces.
2.4. Data Set. The mdCATH data set8 was the basis for applying the coarse-grained mapping approach. Specifically, the initial data were processed to retain only the heavy atoms' coordinates and forces, with a basic force aggregation map applied to the latter. Additionally, the z data set within each HDF5 file was modified to serve as the embedding for each system. 
```

**Metadata:**

```json
{
  "chunk_id": 14,
  "source": "raw_data/jctc_recent\\md\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.md",
  "file_type": "md",
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics",
  "encoding": "utf-8"
}
```

---

### Document 2 (score: 7.0727)

```
0) Izvekov, S.; Voth, G. A. A multiscale coarse-graining method for
biomolecular systems. J. Phys. Chem. B 2005, 109, 2469−2473.
(41) Noid, W. G.; Chu, J.-W.; Ayton, G. S.; Krishna, V.; Izvekov, S.;
Voth, G. A.; Das, A.; Andersen, H. C. The multiscale coarse-graining
method. I. A rigorous bridge between atomistic and coarse-grained
models. J. Chem. Phys. 2008, 128, 244114.
(42) Noé, F.; Fischer, S. Transition networks for modeling the
kinetics of conformational change in macromolecules. Curr. Opin.
Struct. Biol. 2008, 18, 154−162.
(43) Husic, B. E.; Pande, V. S. Markov state models: From an art to
a science. J. Am. Chem. Soc. 2018, 140, 2386−2396.
(44) Pan, A. C.; Roux, B. Building Markov state models along
pathways to determine free energies and rates of transitions. J. Chem.
Phys. 2008, 129, 064107.
(45) Doerr, S.; Harvey, M.; Noé, F.; De Fabritiis, G. HTMD: high-
throughput molecular dynamics for molecular discovery. J. Chem.
Theory Comput. 2016, 12, 1845−1852.
(
```

**Metadata:**

```json
{
  "source": "raw_data/jctc_recent\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.pdf",
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics",
  "file_type": "pdf",
  "chunk_id": 5,
  "page": 8
}
```

---

### Document 3 (score: 6.2208)

```
e Fabritiis, G. An implementation of the smooth
particle mesh Ewald method on GPU hardware. J. Chem. Theory
Comput. 2009, 5, 2371−2377.
(56) Ryckaert, J.-P.; Ciccotti, G.; Berendsen, H. J. Numerical
integration of the cartesian equations of motion of a system with
constraints: molecular dynamics of n-alkanes. J. Comput. Phys. 1977,
23, 327−341.
Journal of Chemical Theory and Computation pubs.acs.org/JCTC Article
https://doi.org/10.1021/acs.jctc.4c01239
J. Chem. Theory Comput. XXXX, XXX, XXX−XXX
H

```

**Metadata:**

```json
{
  "file_type": "pdf",
  "source": "raw_data/jctc_recent\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.pdf",
  "page": 8,
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics",
  "chunk_id": 9
}
```

---


## [5] Results (top_k=5)

Retrieved 5 documents

### Document 1 (score: 8.4007)

```
 via the loss function
$$L_{\rm FM}(\theta) = \frac{1}{\sum_{k=1}^{K} N_k} \sum_{k=1}^{K} \sum_{i=1}^{N_k} ||-\nabla_{\mathbf{R}_i^k} \mathcal{U}(\mathbf{R}^k; \theta) - \mathbf{F}_i^k||^2 \tag{2}$$
where  $N_k$  is the number of beads in conformation  $k$ , and  $K$  is the total number of conformations in a batch. Predicted forces are obtained as the negative gradient of the potential energy  $\tilde{U}$  with respect to the noh-bead coordinates R, and F represents the labeled coarse-grained forces.
2.4. Data Set. The mdCATH data set8 was the basis for applying the coarse-grained mapping approach. Specifically, the initial data were processed to retain only the heavy atoms' coordinates and forces, with a basic force aggregation map applied to the latter. Additionally, the z data set within each HDF5 file was modified to serve as the embedding for each system. 
```

**Metadata:**

```json
{
  "chunk_id": 14,
  "source": "raw_data/jctc_recent\\md\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.md",
  "file_type": "md",
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics",
  "encoding": "utf-8"
}
```

---

### Document 2 (score: 6.2074)

```
n times considered.
3. RESULTS
TensorNet was trained on the filtered mdCATH data set, as
described in Section 2.4, using TorchMD-Net
48
for 100
epochs. Detailed information on model architecture and
training hyper-parameters can be found in the Supporting
Information (see Tables S3 and S4).
The final L1 test loss for the model is reported as 5.07 kcal/
mol/Å, while MSE loss for training and validation are reported
in Figure 2.
3.1. Generalization to Larger Domains. We explore the
ability of the AMARO to scale up when larger protein domains
than those considered in the training set. To achieve this, we
selected a subset of 5,000 conformations from the mdCATH
data set, specifically targeting domains with between 150 and
250 residues and a combined helix and sheet fraction >50%.
This selection criteria ensured that the domains were
representative of complex protein structures while still
maintaining a manageable size for computational analysis.
T
```

**Metadata:**

```json
{
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics",
  "chunk_id": 6,
  "page": 3,
  "file_type": "pdf",
  "source": "raw_data/jctc_recent\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.pdf"
}
```

---

### Document 3 (score: 5.5938)

```
mol/Å, while MSE loss for training and validation are reported in Figure 2.

Figure 2. Training- and validation- MSE loss, in blue and orange respectively, for AMARO as a function of training epoch.
3.1. Generalization to Larger Domains. We explore the ability of the AMARO to scale up when larger protein domains than those considered in the training set. To achieve this, we selected a subset of 5,000 conformations from the mdCATH data set, specifically targeting domains with between 150 and 250 residues and a combined helix and sheet fraction &gt;50%. This selection criteria ensured that the domains were representative of complex protein structures while still maintaining a manageable size for computational analysis. The forces acting on the noh-bead within these larger domains were evaluated using the CG-NNP. AMARO exhibited a mean absolute error (MAE) of 4.98 kcal/mol/Å, assessed for each force component (x, y, z). 
```

**Metadata:**

```json
{
  "source": "raw_data/jctc_recent\\md\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.md",
  "encoding": "utf-8",
  "chunk_id": 21,
  "file_type": "md",
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics"
}
```

---

### Document 4 (score: 5.2359)

```
er minimum RMSD of 4.38 Å.
Moreover, the average RMSD values of 13.31 ± 4.82 Å for
CG-NNP and 6.41 ± 0.5 Å for CHARMM22* suggest that the
coarse-grained model explores a larger conformational space,
as expected.
The CG-NNP’s efficiency was further quantified relative to
system size, measured in CG beads (Figure 7, providing a
quantitative benchmark of AMARO’s performance. Both
millions of simulation steps (left y-axis) and ns/day (right y-
axis) are considered variables. The term “simulation step”
refers to a forward and backward step of the model. The
efficiency demonstrated by the CG-NNP in small-to-medium
systems (up to 1000 CG beads) makes it a valuable tool for
exploring larger conformational landscapes or long-time scale
events.
4. CONCLUSIONS
This paper introduces the first version of AMARO a new fully
machine-learning coarse-grained force field offering a new
framework for molecular dynamics simulations. AMARO uses
an all-heavy-atoms coarse-graining strategy paired with varia-
t
```

**Metadata:**

```json
{
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics",
  "source": "raw_data/jctc_recent\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.pdf",
  "file_type": "pdf",
  "chunk_id": 3,
  "page": 6
}
```

---

### Document 5 (score: 5.1851)

```
proves that the learned potential can scale up without loss in
accuracy. Moreover, Figure 3 presents a direct comparison
between the expected and observed force values, with each dot
color-coded by CG atom type, illustrating the model’s
precision. The results underscore the robustness of the CG-
NNP model and its potential applicability to larger biological
systems, confirming its feature to maintain performance across
an expanded range of system sizes and complexities.
Detailed errors per atom type are reported in Table S5, with
NH
3
+
exhibiting the highest error, a mean absolute error
(MAE) of 8.10 kcal/mol/Å. However, this is not due to NH3
bead-type being underrepresented in the training data sets, as
shown in Figure S1, but rather due to the physical and
chemical properties of this group. Five domains with the
highest number of NH
3
+
groups (i.e., ≥ 20) were selected for
further investigation: 1kvnA00, 1nu7D01, 1w9rA00, 2c5zA00,
2
```

**Metadata:**

```json
{
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics",
  "page": 4,
  "file_type": "pdf",
  "chunk_id": 0,
  "source": "raw_data/jctc_recent\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.pdf"
}
```

---


## [6] Discussion (top_k=3)

Retrieved 3 documents

### Document 1 (score: 5.2347)

```
loaded via UNIV OF CHINESE ACADEMY OF SCIENCES on November 12, 2024 at 06:08:41 (UTC).
See https://pubs.acs.org/sharingguidelines for options on how to legitimately share published articles.

```

**Metadata:**

```json
{
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics",
  "file_type": "pdf",
  "chunk_id": 6,
  "page": 1,
  "source": "raw_data/jctc_recent\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.pdf"
}
```

---

### Document 2 (score: 4.9881)

```
F) is used to describe the free energy landscape of a system as a function of a collective coordinate or reaction coordinate, which is in other terms a configurational free energy in a reduced space. The term "many-body" in the context of a CG model refers to the fact that the potential energy landscape is considered in terms of interactions between groups of atoms rather than individual atoms, and network models offer a straightforward approximation in this context.13 Our machine learning model of choice in this work is TensorNet,9 a new neural network architecture that integrates O(3)-equivariance in message-passing and utilizes rank-2 Cartesian tensor representations. O(3)-equivariant NNPs35−37 ensuring that tensor outputs transform correctly under rotations and reflections. In practice, in this work, we only predict the scalar energy, therefore invariance would have been enough. 
```

**Metadata:**

```json
{
  "file_type": "md",
  "source": "raw_data/jctc_recent\\md\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.md",
  "encoding": "utf-8",
  "chunk_id": 8,
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics"
}
```

---

### Document 3 (score: 4.4491)

```
al resources required for larger systems and extended time scales; furthermore, postprocess and data analysis demands considerable effort, particularly in terms of human expertise and time.10,11 To investigate larger systems over an extended time scale, a leading approach involves reducing computational demands via coarse-grained (CG) simulations, where molecular systems are simulated using fewer degrees of freedom than those associated with the atomic positions.12,13
Several CG models have been developed, each tailored to optimize molecular simulations and capture critical biophysical features. The MARTINI model,14,15 for instance, excels due to its adaptability across a range of biomolecular systems, including membrane structure formation and protein interactions. Models such as AWSEM16 and UNRES17 have been successful in simulating intramolecular protein dynamics, though they occasionally struggle to capture alternative metastable states. 
```

**Metadata:**

```json
{
  "file_type": "md",
  "chunk_id": 2,
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics",
  "source": "raw_data/jctc_recent\\md\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.md",
  "encoding": "utf-8"
}
```

---


## [7] Research Field (top_k=2)

Retrieved 2 documents

### Document 1 (score: 7.0606)

```
Science Laboratory, Universitat Pompeu Fabra, Barcelona 08003, Spain; orcid.org/0000-0003-3225-1632

Complete contact information is available at: https://pubs.acs.org/10.1021/acs.jctc.4c01239
Notes
The authors declare no competing financial interest.
■ ACKNOWLEDGMENTS
AM is financially supported by Generalitat de Catalunya's Agency for Management of University and Research Grants (AGAUR) PhD grant 2024 FI-1-00278; the project PID2023- 151620OB-I00 has been funded by MCIN/AEI/10.13039/ 501100011033. Research reported in this publication was partially supported by the National Institute of General Medical Sciences (NIGMS) of the National Institutes of Health under award number R01GM140090. The content is solely the responsibility of the authors and does not necessarily represent the official views of the National Institutes of Health.
■ REFERENCES
(1) Williamson, J. R. Cooperativity in macromolecular assembly. Nat. Chem. Biol. 2008, 4, 458−465.
(
```

**Metadata:**

```json
{
  "file_type": "md",
  "encoding": "utf-8",
  "chunk_id": 41,
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics",
  "source": "raw_data/jctc_recent\\md\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.md"
}
```

---

### Document 2 (score: 6.4710)

```
or training, model, and fast-folding protein MSMs, details of the values used to achieve the main text results, and additional analyses and statistics (PDF)
■ AUTHOR INFORMATION
Corresponding Author
Gianni De Fabritiis − Computational Science Laboratory, Universitat Pompeu Fabra, Barcelona 08003, Spain; Acellera Labs, Barcelona 08005, Spain; Institucío Catalana de Recerca i Estudis Avançats (ICREA), Barcelona 08010, Spain; orcid.org/0000-0003-3913-4877; Email: g.defabritiis@gmail.com
Authors

Antonio Mirarchi − Computational Science Laboratory, Universitat Pompeu Fabra, Barcelona 08003, Spain; orcid.org/0000-0001-7798-0519
Raúl P. Peláez − Computational Science Laboratory, Universitat Pompeu Fabra, Barcelona 08003, Spain; orcid.org/0000-0003-3393-7329
Guillem Simeon − Computational Science Laboratory, Universitat Pompeu Fabra, Barcelona 08003, Spain; orcid.org/0000-0003-3225-1632

Complete contact information is available at: https://pubs.acs.org/10.1021/acs.jctc.4c01239
Notes
T
```

**Metadata:**

```json
{
  "chunk_id": 40,
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics",
  "source": "raw_data/jctc_recent\\md\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.md",
  "file_type": "md",
  "encoding": "utf-8"
}
```

---


## [8] Received Revised Accepted (top_k=2)

Retrieved 2 documents

### Document 1 (score: 4.2875)

```
reported in this publication was
partially supported by the National Institute of General
Medical Sciences (NIGMS) of the National Institutes of
Health under award number R01GM140090. The content is
solely the responsibility of the authors and does not necessarily
represent the official views of the National Institutes of Health.
■
REFERENCES
(1) Williamson, J. R. Cooperativity in macromolecular assembly.
Nat. Chem. Biol. 2008, 4, 458−465.
(2) McCammon, J. A.; Gelin, B. R.; Karplus, M. Dynamics of folded
proteins. nature 1977, 267, 585−590.
(3) Hollingsworth, S. A.; Dror, R. O. Molecular dynamics simulation
for all. Neuron 2018, 99, 1129−1143.
(4) Baxa, M. C.; Haddadian, E. J.; Jumper, J. M.; Freed, K. F.;
Sosnick, T. R. Loss of conformational entropy in protein folding
calculated using realistic ensembles and its implications for NMR-
based calculations. Proc. Natl. Acad. Sci. U. S. A. 2014, 111, 15396−
15401.
(5) Noé, F.; Schu ̈ tte, C.; Vanden-Eijnden, E.; Reich, L.; Weikl, T. R.
C
```

**Metadata:**

```json
{
  "source": "raw_data/jctc_recent\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.pdf",
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics",
  "file_type": "pdf",
  "chunk_id": 3,
  "page": 7
}
```

---

### Document 2 (score: 4.0755)

```
mol/Å, while MSE loss for training and validation are reported in Figure 2.

Figure 2. Training- and validation- MSE loss, in blue and orange respectively, for AMARO as a function of training epoch.
3.1. Generalization to Larger Domains. We explore the ability of the AMARO to scale up when larger protein domains than those considered in the training set. To achieve this, we selected a subset of 5,000 conformations from the mdCATH data set, specifically targeting domains with between 150 and 250 residues and a combined helix and sheet fraction &gt;50%. This selection criteria ensured that the domains were representative of complex protein structures while still maintaining a manageable size for computational analysis. The forces acting on the noh-bead within these larger domains were evaluated using the CG-NNP. AMARO exhibited a mean absolute error (MAE) of 4.98 kcal/mol/Å, assessed for each force component (x, y, z). 
```

**Metadata:**

```json
{
  "source": "raw_data/jctc_recent\\md\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.md",
  "encoding": "utf-8",
  "chunk_id": 21,
  "file_type": "md",
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics"
}
```

---


## [9] DOI (top_k=2)

Retrieved 2 documents

### Document 1 (score: 4.4116)

```
 via the loss function
$$L_{\rm FM}(\theta) = \frac{1}{\sum_{k=1}^{K} N_k} \sum_{k=1}^{K} \sum_{i=1}^{N_k} ||-\nabla_{\mathbf{R}_i^k} \mathcal{U}(\mathbf{R}^k; \theta) - \mathbf{F}_i^k||^2 \tag{2}$$
where  $N_k$  is the number of beads in conformation  $k$ , and  $K$  is the total number of conformations in a batch. Predicted forces are obtained as the negative gradient of the potential energy  $\tilde{U}$  with respect to the noh-bead coordinates R, and F represents the labeled coarse-grained forces.
2.4. Data Set. The mdCATH data set8 was the basis for applying the coarse-grained mapping approach. Specifically, the initial data were processed to retain only the heavy atoms' coordinates and forces, with a basic force aggregation map applied to the latter. Additionally, the z data set within each HDF5 file was modified to serve as the embedding for each system. 
```

**Metadata:**

```json
{
  "chunk_id": 14,
  "source": "raw_data/jctc_recent\\md\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.md",
  "file_type": "md",
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics",
  "encoding": "utf-8"
}
```

---

### Document 2 (score: 3.4955)

```
Science Laboratory, Universitat Pompeu Fabra, Barcelona 08003, Spain; orcid.org/0000-0003-3225-1632

Complete contact information is available at: https://pubs.acs.org/10.1021/acs.jctc.4c01239
Notes
The authors declare no competing financial interest.
■ ACKNOWLEDGMENTS
AM is financially supported by Generalitat de Catalunya's Agency for Management of University and Research Grants (AGAUR) PhD grant 2024 FI-1-00278; the project PID2023- 151620OB-I00 has been funded by MCIN/AEI/10.13039/ 501100011033. Research reported in this publication was partially supported by the National Institute of General Medical Sciences (NIGMS) of the National Institutes of Health under award number R01GM140090. The content is solely the responsibility of the authors and does not necessarily represent the official views of the National Institutes of Health.
■ REFERENCES
(1) Williamson, J. R. Cooperativity in macromolecular assembly. Nat. Chem. Biol. 2008, 4, 458−465.
(
```

**Metadata:**

```json
{
  "file_type": "md",
  "encoding": "utf-8",
  "chunk_id": 41,
  "title": "Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics",
  "source": "raw_data/jctc_recent\\md\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics\\Mirarchi \u7b49 - 2024 - AMARO All Heavy-Atom Transferable Neural Network Potentials of Protein Thermodynamics.md"
}
```

---

