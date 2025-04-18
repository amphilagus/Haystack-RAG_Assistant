# BATCH QUERY RESULTS FOR TITLE: Liang 等 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A

**Collection:** jctc_recent_0418
**Timestamp:** 2025-04-18 15:11:42

---


## [1] Abstract (top_k=3)

Retrieved 3 documents

### Document 1 (score: 9.7957)

```
hcal{G}_{\rm al} = \sum_{\slash b} \left( a \sharp f_{\rm xc} \vert \not b \right) \ X_{b\slash} = \sum_{\mu\nu} \mathcal{C}_{\nu a}^{\ast} \mathcal{C}_{\mu\ell} \mathcal{G}_{\nu\mu}^{\,} \tag{10}$$
2.2. Gauge Invariance Correction to mGGA. The kinetic energy density of mGGA functionals is usually defined as
$$\pi(r,t) = \frac{1}{2} \sum_{j} |-i\nabla \psi_{j}(r,t)|^{2} \tag{11}$$
which changes upon a gauge transformation (i.e.,  $\tau(r, t)$  is gauge-dependent), leading to the energy also being gaugedependent. This can be shown using the real gauge function  $\Lambda(r,t)$ .
$$
\mu_{\slash}^{!!!\/} \Lambda = \mu_{\slash}^{!!\/}(r, t) \mathbf{e}^{-i\Lambda(r, t)} \tag{12}
$$
$$
\pi\Lambda = \pi(r,t) - \nabla\Lambda(r,t) \cdot \mathfrak{j}_p(r,t) + \frac{1}{2}|\nabla\Lambda(r,t)|$$
$$
\mathfrak{l}^2 \rho(r,t) \tag{13}$$
Here  $j_p(r, t)$  is the paramagnetic orbital current density of the original system.
$
```

**Metadata:**

```json
{
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md",
  "chunk_id": 17,
  "file_type": "md",
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "encoding": "utf-8"
}
```

---

### Document 2 (score: 8.6885)

```
au^2}$   $\frac{\partial}{\partial \hat{\tau}}$   $\frac{\partial}{\partial \tau}$   $\frac{\partial^2 f}{\partial \hat{\tau}^2} = \frac{\partial^2 f}{\partial \tau^2}$  to employ to employ existing functionals.
3. COMPUTATIONAL DETAILS
We have tested the following density functionals:

Local Density Approximation (LDA, Rung 1): SPW9263,64
GGA (Rung 2): B97-D,65 MPW91,66,67 PBE,68 BLYP,69 N12,70 SOGGA11.71
mGGA (Rung 3): B97M-V,44 mBEEF,72 SCAN,73 MS2,52 M06-L,74 MVS,51 revM06-L,75 MN15-L,76 revTPSS,77 TPSS.78
hybrid GGA (Rung 4): ωB97X-D,79 CAM-B3LYP,80 ωB97X-V,43 SOGGA11-X,81 LRC-wPBE,82 LRCwPBEh,19 MPW1K,83 PBE0,84 HSEHJS,85,86 rcam-B3LYP,87 MPW1PW91,66 BHHLYP,88,89 PBE50,90 B3LYP,91,92 HFLYP.89
hybrid mGGA (Rung 4): BMK,93 M06-SX,53 M06-2X,94 ωB97M-V,45 wM05-D,95 MN15,96 PW6B95,97 SCAN0,98 MS2h,52 M11,99 revTPSSh,100 TPSSH,101 MVSh,51 MN12-SX.102

F
```

**Metadata:**

```json
{
  "file_type": "md",
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md",
  "encoding": "utf-8",
  "chunk_id": 21,
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A"
}
```

---

### Document 3 (score: 8.0494)

```
mathbf{0} &amp; -\mathbf{1} \end{bmatrix} \begin{bmatrix} \mathbf{X} \ \mathbf{Y} \end{bmatrix} \tag{1}
$$
Here, X and Y are the transition vectors. The elements of the matrices A and B are given as
$$A_{\rm ai,bj} = \delta_{\dot{\eta}} \delta_{ab} (\epsilon_u - \epsilon_i) + (ai|\dot{\eta}b) - c_{\rm HF}(ab|\dot{\eta})$$
$$+ \ (1 - c_{\rm HF}) (al ! f_{\rm xc} \vert \dot{\eta}b) \tag{2}$$
$$B_{\rm ai,bj} = \begin{pmatrix} ailbj \end{pmatrix} - c_{\rm HF}(bilaj) \ + \begin{pmatrix} 1 \ -c_{\rm HF} \end{pmatrix} \begin{pmatrix} ailf_{\rm xc} \| bj \end{pmatrix} \tag{3}$$
where the indices i, j and a, b label occupied and virtual orbitals respectively, which will also be written as  $\phi_i$ ,  $\phi_j$ ,  $\phi_a$ , and  $\phi_b$  later. We will use m and n to represent arbitrary molecular orbitals, while  $\epsilon_a$  and  $\epsilon_i$  are orbital energies of Kohn-Sham orbitals a and i. 
```

**Metadata:**

```json
{
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md",
  "chunk_id": 12,
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "encoding": "utf-8",
  "file_type": "md"
}
```

---


## [2] Introduction (top_k=3)

Retrieved 3 documents

### Document 1 (score: 5.8739)

```
-----|-----------|------------|------------|------------|------------|-------|-------|-------|
| LDA         | SPW92     | 0.314      | 0.970      | 0.641      | 0.802      | 0.377 | 0.602 | 1.203 |
| GGA         | B97-D     | 0.301      | 1.080      | 0.561      | 0.956      | 0.346 | 0.654 | 1.119 |
|             | PBE       | 0.337      | 1.137      | 0.616      | 0.968      | 0.403 | 0.594 | 1.163 |
|             | B97M-V    | 0.364      | 0.657      | 0.330      | 0.680      | 0.330 | 0.679 | 0.847 |
|             | SCAN      | 0.461      | 0.431      | 0.538      | 0.329      | 0.327 | 0.579 | 0.881 |
| mGGA        | M06-L     | 0.313      | 0.807      | 0.376      | 0.696      | 0.294 | 0.712 | 0.884 |
|             | revM06-L  | 0.605      | 0.639      | 0.376      | 0.481      | 0.530 | 0.866 | 0.688 |
|             | revTPSS   | 0.266      | 0.899      | 0.468      | 0.806      | 0.314 | 0.531 | 0.998 |
|
```

**Metadata:**

```json
{
  "chunk_id": 54,
  "file_type": "md",
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "encoding": "utf-8",
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md"
}
```

---

### Document 2 (score: 5.1898)

```
hcal{G}_{\rm al} = \sum_{\slash b} \left( a \sharp f_{\rm xc} \vert \not b \right) \ X_{b\slash} = \sum_{\mu\nu} \mathcal{C}_{\nu a}^{\ast} \mathcal{C}_{\mu\ell} \mathcal{G}_{\nu\mu}^{\,} \tag{10}$$
2.2. Gauge Invariance Correction to mGGA. The kinetic energy density of mGGA functionals is usually defined as
$$\pi(r,t) = \frac{1}{2} \sum_{j} |-i\nabla \psi_{j}(r,t)|^{2} \tag{11}$$
which changes upon a gauge transformation (i.e.,  $\tau(r, t)$  is gauge-dependent), leading to the energy also being gaugedependent. This can be shown using the real gauge function  $\Lambda(r,t)$ .
$$
\mu_{\slash}^{!!!\/} \Lambda = \mu_{\slash}^{!!\/}(r, t) \mathbf{e}^{-i\Lambda(r, t)} \tag{12}
$$
$$
\pi\Lambda = \pi(r,t) - \nabla\Lambda(r,t) \cdot \mathfrak{j}_p(r,t) + \frac{1}{2}|\nabla\Lambda(r,t)|$$
$$
\mathfrak{l}^2 \rho(r,t) \tag{13}$$
Here  $j_p(r, t)$  is the paramagnetic orbital current density of the original system.
$
```

**Metadata:**

```json
{
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md",
  "chunk_id": 17,
  "file_type": "md",
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "encoding": "utf-8"
}
```

---

### Document 3 (score: 4.4905)

```
mathbf{0} &amp; -\mathbf{1} \end{bmatrix} \begin{bmatrix} \mathbf{X} \ \mathbf{Y} \end{bmatrix} \tag{1}
$$
Here, X and Y are the transition vectors. The elements of the matrices A and B are given as
$$A_{\rm ai,bj} = \delta_{\dot{\eta}} \delta_{ab} (\epsilon_u - \epsilon_i) + (ai|\dot{\eta}b) - c_{\rm HF}(ab|\dot{\eta})$$
$$+ \ (1 - c_{\rm HF}) (al ! f_{\rm xc} \vert \dot{\eta}b) \tag{2}$$
$$B_{\rm ai,bj} = \begin{pmatrix} ailbj \end{pmatrix} - c_{\rm HF}(bilaj) \ + \begin{pmatrix} 1 \ -c_{\rm HF} \end{pmatrix} \begin{pmatrix} ailf_{\rm xc} \| bj \end{pmatrix} \tag{3}$$
where the indices i, j and a, b label occupied and virtual orbitals respectively, which will also be written as  $\phi_i$ ,  $\phi_j$ ,  $\phi_a$ , and  $\phi_b$  later. We will use m and n to represent arbitrary molecular orbitals, while  $\epsilon_a$  and  $\epsilon_i$  are orbital energies of Kohn-Sham orbitals a and i. 
```

**Metadata:**

```json
{
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md",
  "chunk_id": 12,
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "encoding": "utf-8",
  "file_type": "md"
}
```

---


## [3] Background (top_k=3)

Retrieved 3 documents

### Document 1 (score: 3.9624)

```
-----|-----------|------------|------------|------------|------------|-------|-------|-------|
| LDA         | SPW92     | 0.314      | 0.970      | 0.641      | 0.802      | 0.377 | 0.602 | 1.203 |
| GGA         | B97-D     | 0.301      | 1.080      | 0.561      | 0.956      | 0.346 | 0.654 | 1.119 |
|             | PBE       | 0.337      | 1.137      | 0.616      | 0.968      | 0.403 | 0.594 | 1.163 |
|             | B97M-V    | 0.364      | 0.657      | 0.330      | 0.680      | 0.330 | 0.679 | 0.847 |
|             | SCAN      | 0.461      | 0.431      | 0.538      | 0.329      | 0.327 | 0.579 | 0.881 |
| mGGA        | M06-L     | 0.313      | 0.807      | 0.376      | 0.696      | 0.294 | 0.712 | 0.884 |
|             | revM06-L  | 0.605      | 0.639      | 0.376      | 0.481      | 0.530 | 0.866 | 0.688 |
|             | revTPSS   | 0.266      | 0.899      | 0.468      | 0.806      | 0.314 | 0.531 | 0.998 |
|
```

**Metadata:**

```json
{
  "chunk_id": 54,
  "file_type": "md",
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "encoding": "utf-8",
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md"
}
```

---

### Document 2 (score: 3.7392)

```
the basis set convergence of functionals from different rungs of Jacob's Ladder.119 Figures 3 and 4 display the RMSEs obtained with different basis sets for valence and Rydberg subsets against their average number of basis functions across the Q1 data set. We employ two kind of reference values here. One is calculated by the method itself in the complete basis set limit (CBS, here approximated with d-aug-cc-pV5Z basis set120), and the other is the set of TBE/CBS values from ref 37.
It is evident that ωB97X-V and ωB97M-V converge more rapidly than B97-D and B97M-V when the basis set size is increased, no matter which basis set family is used. This seems to imply that the hybrid functionals may converge more rapidly than the local functionals. But because of the limited number of tested functionals, we cannot rule out the possibility that the basis set convergence may be just influenced by characteristics of the individual functional. 
```

**Metadata:**

```json
{
  "chunk_id": 33,
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "file_type": "md",
  "encoding": "utf-8",
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md"
}
```

---

### Document 3 (score: 3.1379)

```
hcal{G}_{\rm al} = \sum_{\slash b} \left( a \sharp f_{\rm xc} \vert \not b \right) \ X_{b\slash} = \sum_{\mu\nu} \mathcal{C}_{\nu a}^{\ast} \mathcal{C}_{\mu\ell} \mathcal{G}_{\nu\mu}^{\,} \tag{10}$$
2.2. Gauge Invariance Correction to mGGA. The kinetic energy density of mGGA functionals is usually defined as
$$\pi(r,t) = \frac{1}{2} \sum_{j} |-i\nabla \psi_{j}(r,t)|^{2} \tag{11}$$
which changes upon a gauge transformation (i.e.,  $\tau(r, t)$  is gauge-dependent), leading to the energy also being gaugedependent. This can be shown using the real gauge function  $\Lambda(r,t)$ .
$$
\mu_{\slash}^{!!!\/} \Lambda = \mu_{\slash}^{!!\/}(r, t) \mathbf{e}^{-i\Lambda(r, t)} \tag{12}
$$
$$
\pi\Lambda = \pi(r,t) - \nabla\Lambda(r,t) \cdot \mathfrak{j}_p(r,t) + \frac{1}{2}|\nabla\Lambda(r,t)|$$
$$
\mathfrak{l}^2 \rho(r,t) \tag{13}$$
Here  $j_p(r, t)$  is the paramagnetic orbital current density of the original system.
$
```

**Metadata:**

```json
{
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md",
  "chunk_id": 17,
  "file_type": "md",
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "encoding": "utf-8"
}
```

---


## [4] Method (top_k=3)

Retrieved 3 documents

### Document 1 (score: 6.9702)

```
-----|-----------|------------|------------|------------|------------|-------|-------|-------|
| LDA         | SPW92     | 0.314      | 0.970      | 0.641      | 0.802      | 0.377 | 0.602 | 1.203 |
| GGA         | B97-D     | 0.301      | 1.080      | 0.561      | 0.956      | 0.346 | 0.654 | 1.119 |
|             | PBE       | 0.337      | 1.137      | 0.616      | 0.968      | 0.403 | 0.594 | 1.163 |
|             | B97M-V    | 0.364      | 0.657      | 0.330      | 0.680      | 0.330 | 0.679 | 0.847 |
|             | SCAN      | 0.461      | 0.431      | 0.538      | 0.329      | 0.327 | 0.579 | 0.881 |
| mGGA        | M06-L     | 0.313      | 0.807      | 0.376      | 0.696      | 0.294 | 0.712 | 0.884 |
|             | revM06-L  | 0.605      | 0.639      | 0.376      | 0.481      | 0.530 | 0.866 | 0.688 |
|             | revTPSS   | 0.266      | 0.899      | 0.468      | 0.806      | 0.314 | 0.531 | 0.998 |
|
```

**Metadata:**

```json
{
  "chunk_id": 54,
  "file_type": "md",
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "encoding": "utf-8",
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md"
}
```

---

### Document 2 (score: 6.8238)

```
hcal{G}_{\rm al} = \sum_{\slash b} \left( a \sharp f_{\rm xc} \vert \not b \right) \ X_{b\slash} = \sum_{\mu\nu} \mathcal{C}_{\nu a}^{\ast} \mathcal{C}_{\mu\ell} \mathcal{G}_{\nu\mu}^{\,} \tag{10}$$
2.2. Gauge Invariance Correction to mGGA. The kinetic energy density of mGGA functionals is usually defined as
$$\pi(r,t) = \frac{1}{2} \sum_{j} |-i\nabla \psi_{j}(r,t)|^{2} \tag{11}$$
which changes upon a gauge transformation (i.e.,  $\tau(r, t)$  is gauge-dependent), leading to the energy also being gaugedependent. This can be shown using the real gauge function  $\Lambda(r,t)$ .
$$
\mu_{\slash}^{!!!\/} \Lambda = \mu_{\slash}^{!!\/}(r, t) \mathbf{e}^{-i\Lambda(r, t)} \tag{12}
$$
$$
\pi\Lambda = \pi(r,t) - \nabla\Lambda(r,t) \cdot \mathfrak{j}_p(r,t) + \frac{1}{2}|\nabla\Lambda(r,t)|$$
$$
\mathfrak{l}^2 \rho(r,t) \tag{13}$$
Here  $j_p(r, t)$  is the paramagnetic orbital current density of the original system.
$
```

**Metadata:**

```json
{
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md",
  "chunk_id": 17,
  "file_type": "md",
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "encoding": "utf-8"
}
```

---

### Document 3 (score: 6.6027)

```
l |
|---------|-----|-----|----|--------------|--------------|-----|
| singlet | 55  | 154 | 19 | all singlets | all doublets | 254 |
| triplet | 45  | 111 | 11 |              |              | 167 |
| valence | 60  | 201 | 28 |              |              | 289 |
| Rydberg | 39  | 64  | 2  |              |              | 105 |
| total   | 100 | 265 | 30 | 27           | 42           | 463 |
4. PRELIMINARY BENCHMARK OF METHODS AND BASIS SETS
4.1. Effect of TDA Approximation and meta-GGA Gauge Invariance Correction. We first explore the effect of TDA and GINV correction on the mGGA and hybrid mGGA functionals separately. The GINV correction is only suitable for use with TDDFT because TDA itself breaks gauge invariance.118 Figure 1 shows graphical representations of the root-mean square error (RMSE) of six representative functionals for different excitation types via TDDFT, TDDFT with GINV correction and TDA on the Q1 subset. 
```

**Metadata:**

```json
{
  "encoding": "utf-8",
  "file_type": "md",
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md",
  "chunk_id": 28,
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A"
}
```

---


## [5] Results (top_k=5)

Retrieved 5 documents

### Document 1 (score: 8.0488)

```
-----|-----------|------------|------------|------------|------------|-------|-------|-------|
| LDA         | SPW92     | 0.314      | 0.970      | 0.641      | 0.802      | 0.377 | 0.602 | 1.203 |
| GGA         | B97-D     | 0.301      | 1.080      | 0.561      | 0.956      | 0.346 | 0.654 | 1.119 |
|             | PBE       | 0.337      | 1.137      | 0.616      | 0.968      | 0.403 | 0.594 | 1.163 |
|             | B97M-V    | 0.364      | 0.657      | 0.330      | 0.680      | 0.330 | 0.679 | 0.847 |
|             | SCAN      | 0.461      | 0.431      | 0.538      | 0.329      | 0.327 | 0.579 | 0.881 |
| mGGA        | M06-L     | 0.313      | 0.807      | 0.376      | 0.696      | 0.294 | 0.712 | 0.884 |
|             | revM06-L  | 0.605      | 0.639      | 0.376      | 0.481      | 0.530 | 0.866 | 0.688 |
|             | revTPSS   | 0.266      | 0.899      | 0.468      | 0.806      | 0.314 | 0.531 | 0.998 |
|
```

**Metadata:**

```json
{
  "chunk_id": 54,
  "file_type": "md",
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "encoding": "utf-8",
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md"
}
```

---

### Document 2 (score: 7.5503)

```
\omega$ B97M-V) on the Q2 and QCT
subsets, and their result are still very close (shown in SI), further validating this conclusion.
5. COMPREHENSIVE BENCHMARK OF 43 DENSITY FUNCTIONAL APPROXIMATIONS
5.1. Overall Performance. Figure 5 and Figure S1 summarize the RMSE of 43 functionals on the whole benchmark data set. N12, SOGGA11, and HFLYP are not considered here due to their very poor performance in the preliminary test on Q1. It turns out that Jacob's ladder119 is Table 2. Comparison of RMSEs and MSEs (both in eV) of B97M-V, ωB97X-V and ωB97M-V with or without VV10's Contribution across Q1 Subset
|         | RMSE  | MSE    |
|---------|-------|--------|
| B97M    | 0.502 | -0.150 |
| B97M-V  | 0.498 | -0.148 |
| ωB97Xa  | 0.279 | -0.119 |
| ωB97X-V | 0.284 | -0.109 |
| ωB97M   | 0.465 | -0.329 |
| ωB97M-V | 0.464 | -0.329 |
a $\omega$ B97X in this table refers to  $\omega$ B97X-V without the VV10 contribution, not the stand-alone functional developed by Chai et al. in 2008.125
p
```

**Metadata:**

```json
{
  "chunk_id": 40,
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md",
  "file_type": "md",
  "encoding": "utf-8"
}
```

---

### Document 3 (score: 7.3278)

```
 0.005   | -0.168  | 0.279   | 0.238   | -0.069  | -0.066  | 0.552        |
|             | @B97X-V   | 0.338   | 0.198   | 0.126   | -0.075  | 0.299   | 0.252   | 0.016   | 0.110   | 0.585        |
|             | CAM-B3LYP | 0.303   | 0.291   | -0.049  | -0.246  | 0.311   | 0.261   | -0.112  | -0.186  | 0.580        |
|             | MPW1K     | 0.348   | 0.316   | 0.114   | -0.230  | 0.372   | 0.199   | -0.063  | 0.055   | 0.618        |
|             | B3LYP     | 0.467   | 0.399   | -0.293  | -0.355  | 0.358   | 0.609   | -0.226  | -0.576  | 0.517        |
| hybrid mGGA | M06-SX    | 0.324   | 0.171   | 0.117   | -0.007  | 0.277   | 0.251   | 0.016   | 0.198   | 0.516        |
|             | BMK       | 0.323   | 0.200   | 0.063   | -0.082  | 0.304   | 0.192   | -0.023  | 0.069   | 0.612        |
|             | M06-2X    | 0.359   | 0.248   | -0.078  | -0.095  | 0.341   | 0.237   | -0.058  | -0.158  | 0.743        |
|
```

**Metadata:**

```json
{
  "file_type": "md",
  "chunk_id": 48,
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md",
  "encoding": "utf-8",
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A"
}
```

---

### Document 4 (score: 7.2525)

```
 -0.537  | -0.480  | 0.500   | 0.995   | -0.359  | -0.934  | 0.387        |
|             | PBE       | 0.767   | 0.622   | -0.570  | -0.515  | 0.551   | 1.026   | -0.398  | -0.954  | 0.352        |
| mGGA        | B97M-V    | 0.517   | 0.334   | -0.198  | -0.165  | 0.337   | 0.666   | -0.032  | -0.604  | 0.413        |
|             | MVS       | 0.508   | 0.377   | 0.220   | 0.028   | 0.455   | 0.459   | 0.099   | 0.243   | 0.294        |
|             | SCAN      | 0.402   | 0.554   | -0.101  | -0.442  | 0.506   | 0.370   | -0.256  | -0.221  | 0.321        |
|             | M06-L     | 0.543   | 0.396   | -0.252  | -0.225  | 0.357   | 0.734   | -0.096  | -0.638  | 0.362        |
| hybrid GGA  | @B97X-D   | 0.295   | 0.228   | 0.005   | -0.168  | 0.279   | 0.238   | -0.069  | -0.066  | 0.552        |
|             | @B97X-V   | 0.338   | 0.198   | 0.126   | -0.075  | 0.299   | 0.252   | 0.016   | 0.110   | 0.585        |
|
```

**Metadata:**

```json
{
  "file_type": "md",
  "chunk_id": 47,
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md",
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "encoding": "utf-8"
}
```

---

### Document 5 (score: 7.1912)

```
     | revM06-L  | 0.605      | 0.639      | 0.376      | 0.481      | 0.530 | 0.866 | 0.688 |
|             | revTPSS   | 0.266      | 0.899      | 0.468      | 0.806      | 0.314 | 0.531 | 0.998 |
|             | ωB97X-D   | 0.308      | 0.351      | 0.279      | 0.131      | 0.205 | 0.314 | 0.247 |
|             | ωB97X-V   | 0.314      | 0.213      | 0.306      | 0.274      | 0.202 | 0.275 | 0.426 |
| hybrid GGA  | CAM-B3LYP | 0.368      | 0.377      | 0.297      | 0.158      | 0.262 | 0.313 | 0.234 |
|             | MPW1K     | 0.416      | 0.190      | 0.368      | 0.204      | 0.292 | 0.426 | 0.297 |
|             | B3LYP     | 0.353      | 0.658      | 0.368      | 0.587      | 0.280 | 0.366 | 0.636 |
|             | BMK       | 0.334      | 0.211      | 0.304      | 0.180      | 0.217 | 0.315 | 0.292 |
| hybrid mGGA | M06-SX    | 0.276      | 0.285      | 0.291      | 0.229      | 0.156 | 0.366 | 0.381 |
|
```

**Metadata:**

```json
{
  "chunk_id": 55,
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "encoding": "utf-8",
  "file_type": "md",
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md"
}
```

---


## [6] Discussion (top_k=3)

Retrieved 3 documents

### Document 1 (score: 5.3936)

```
improvement over TDDFT, but more extensive studies are needed before any firm conclusions can be reached.
```

**Metadata:**

```json
{
  "chunk_id": 68,
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md",
  "encoding": "utf-8",
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "file_type": "md"
}
```

---

### Document 2 (score: 4.1639)

```
Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations: Assessment of 43 Popular and Recently Developed Functionals from Rungs One to Four
Jiashu Liang, Xintian Feng, Diptarka Hait, and Martin Head-Gordon\*
|        | Cite This: J. Chem. Theory Comput. 2022, 18, 3460–3473 | Read Online             |                          |
|--------|--------------------------------------------------------|-------------------------|--------------------------|
| ACCESS | Metrics &amp; More                                         | Article Recommendations | Supporting InformationSI |
ABSTRACT: In this paper, the performance of more than 40 popular or recently developed density functionals is assessed for the calculation of 463 vertical excitation energies against the large and accurate QuestDB benchmark set. For this purpose, the Tamm−Dancoff approximation offers a good balance between computational efficiency and accuracy. 
```

**Metadata:**

```json
{
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md",
  "encoding": "utf-8",
  "file_type": "md",
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "chunk_id": 0
}
```

---

### Document 3 (score: 3.7719)

```
-----|-----------|------------|------------|------------|------------|-------|-------|-------|
| LDA         | SPW92     | 0.314      | 0.970      | 0.641      | 0.802      | 0.377 | 0.602 | 1.203 |
| GGA         | B97-D     | 0.301      | 1.080      | 0.561      | 0.956      | 0.346 | 0.654 | 1.119 |
|             | PBE       | 0.337      | 1.137      | 0.616      | 0.968      | 0.403 | 0.594 | 1.163 |
|             | B97M-V    | 0.364      | 0.657      | 0.330      | 0.680      | 0.330 | 0.679 | 0.847 |
|             | SCAN      | 0.461      | 0.431      | 0.538      | 0.329      | 0.327 | 0.579 | 0.881 |
| mGGA        | M06-L     | 0.313      | 0.807      | 0.376      | 0.696      | 0.294 | 0.712 | 0.884 |
|             | revM06-L  | 0.605      | 0.639      | 0.376      | 0.481      | 0.530 | 0.866 | 0.688 |
|             | revTPSS   | 0.266      | 0.899      | 0.468      | 0.806      | 0.314 | 0.531 | 0.998 |
|
```

**Metadata:**

```json
{
  "chunk_id": 54,
  "file_type": "md",
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "encoding": "utf-8",
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md"
}
```

---


## [7] Research Field (top_k=2)

Retrieved 2 documents

### Document 1 (score: 8.2484)

```
improvement over TDDFT, but more extensive studies are needed before any firm conclusions can be reached.
```

**Metadata:**

```json
{
  "chunk_id": 68,
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md",
  "encoding": "utf-8",
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "file_type": "md"
}
```

---

### Document 2 (score: 4.9033)

```
lance. Among local functionals, LDAs and GGAs yield strong underestimation (MSE around −0.5 eV) while meta-GGAs can reduce the systematic error roughly by half. The addition of exact exchange (EXX)

can further reduce systematic error and good RSH functionals (RSHs) or global hybrid functionals (GHs) with high EXXs, like ωB97X-D and BMK, can almost resolve this problem (the absolute values of their MSE are only near 0.05 eV).

Taking the precision of the benchmark data (±0.05 eV) into consideration, the overall RMSEs of good functionals on each rung are so close that we cannot give a definite answer about which functional is best for predicting excitation energies. ωB97X-D offers the lowest overall RMSE (0.272 eV) among all functionals, and BMK, M06-SX, ωB97X-V, CAM-B3LYP and SOGGA11-X also provide similarly accurate predictions (RMSE &lt; 0.30 eV). If semilocal functionals are required, we recommend mGGAs like mBEEF and B97M-V. 
```

**Metadata:**

```json
{
  "chunk_id": 43,
  "encoding": "utf-8",
  "file_type": "md",
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md",
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A"
}
```

---


## [8] Received Revised Accepted (top_k=2)

Retrieved 2 documents

### Document 1 (score: 5.7438)

```
     | revM06-L  | 0.605      | 0.639      | 0.376      | 0.481      | 0.530 | 0.866 | 0.688 |
|             | revTPSS   | 0.266      | 0.899      | 0.468      | 0.806      | 0.314 | 0.531 | 0.998 |
|             | ωB97X-D   | 0.308      | 0.351      | 0.279      | 0.131      | 0.205 | 0.314 | 0.247 |
|             | ωB97X-V   | 0.314      | 0.213      | 0.306      | 0.274      | 0.202 | 0.275 | 0.426 |
| hybrid GGA  | CAM-B3LYP | 0.368      | 0.377      | 0.297      | 0.158      | 0.262 | 0.313 | 0.234 |
|             | MPW1K     | 0.416      | 0.190      | 0.368      | 0.204      | 0.292 | 0.426 | 0.297 |
|             | B3LYP     | 0.353      | 0.658      | 0.368      | 0.587      | 0.280 | 0.366 | 0.636 |
|             | BMK       | 0.334      | 0.211      | 0.304      | 0.180      | 0.217 | 0.315 | 0.292 |
| hybrid mGGA | M06-SX    | 0.276      | 0.285      | 0.291      | 0.229      | 0.156 | 0.366 | 0.381 |
|
```

**Metadata:**

```json
{
  "chunk_id": 55,
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "encoding": "utf-8",
  "file_type": "md",
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md"
}
```

---

### Document 2 (score: 5.5658)

```
s preferable, and all results beyond that point utilize it.
We select reference transitions from QUEST database according to the following three criteria. (i) The transition should be labeled "safe". (The deviation with FCI is expected to be smaller than 0.05 eV.) (ii) The transition should have dominant single-excitation character (%T1 &gt; 85%, as computed at the CC3 level) except for the data in the QR data set. This is because we do not have the exact time-dependent (i.e., frequency-dependent) functional and double (or higher) excitation character can not be captured by LR-TDDFT with adiabatic approximation.113 (iii) The electronic state associated with the transition should be assignable using the attribution procedure described below.
All the calculations employ the aug-cc-pVTZ basis set114−116 except for the basis set tests described in Section 4.2. The large aug-cc-pVTZ basis set contains many diffuse basis functions and thus yields significant orbital mixing in the excitation
w
```

**Metadata:**

```json
{
  "encoding": "utf-8",
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md",
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "chunk_id": 24,
  "file_type": "md"
}
```

---


## [9] DOI (top_k=2)

Retrieved 2 documents

### Document 1 (score: 5.2800)

```
-----|-----------|------------|------------|------------|------------|-------|-------|-------|
| LDA         | SPW92     | 0.314      | 0.970      | 0.641      | 0.802      | 0.377 | 0.602 | 1.203 |
| GGA         | B97-D     | 0.301      | 1.080      | 0.561      | 0.956      | 0.346 | 0.654 | 1.119 |
|             | PBE       | 0.337      | 1.137      | 0.616      | 0.968      | 0.403 | 0.594 | 1.163 |
|             | B97M-V    | 0.364      | 0.657      | 0.330      | 0.680      | 0.330 | 0.679 | 0.847 |
|             | SCAN      | 0.461      | 0.431      | 0.538      | 0.329      | 0.327 | 0.579 | 0.881 |
| mGGA        | M06-L     | 0.313      | 0.807      | 0.376      | 0.696      | 0.294 | 0.712 | 0.884 |
|             | revM06-L  | 0.605      | 0.639      | 0.376      | 0.481      | 0.530 | 0.866 | 0.688 |
|             | revTPSS   | 0.266      | 0.899      | 0.468      | 0.806      | 0.314 | 0.531 | 0.998 |
|
```

**Metadata:**

```json
{
  "chunk_id": 54,
  "file_type": "md",
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A",
  "encoding": "utf-8",
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md"
}
```

---

### Document 2 (score: 4.2109)

```
l |
|---------|-----|-----|----|--------------|--------------|-----|
| singlet | 55  | 154 | 19 | all singlets | all doublets | 254 |
| triplet | 45  | 111 | 11 |              |              | 167 |
| valence | 60  | 201 | 28 |              |              | 289 |
| Rydberg | 39  | 64  | 2  |              |              | 105 |
| total   | 100 | 265 | 30 | 27           | 42           | 463 |
4. PRELIMINARY BENCHMARK OF METHODS AND BASIS SETS
4.1. Effect of TDA Approximation and meta-GGA Gauge Invariance Correction. We first explore the effect of TDA and GINV correction on the mGGA and hybrid mGGA functionals separately. The GINV correction is only suitable for use with TDDFT because TDA itself breaks gauge invariance.118 Figure 1 shows graphical representations of the root-mean square error (RMSE) of six representative functionals for different excitation types via TDDFT, TDDFT with GINV correction and TDA on the Q1 subset. 
```

**Metadata:**

```json
{
  "encoding": "utf-8",
  "file_type": "md",
  "source": "raw_data/jctc_recent/cleaned\\Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A.md",
  "chunk_id": 28,
  "title": "Liang \u7b49 - 2022 - Revisiting the Performance of Time-Dependent Density Functional Theory for Electronic Excitations A"
}
```

---

