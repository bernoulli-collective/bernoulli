# Research Canon: Tom Dupré la Tour

**PI:** Tom Dupré la Tour — OpenAI (formerly UC Berkeley / Gallant Lab; Télécom ParisTech)
**Source:** https://tomdlt.github.io/
**Date:** 2026-04-29

## In one sentence
This canon is organized by a recurring methodological stance: replace fragile hand-tuned summaries of complex signals with explicit, testable models that can compare competing representational hypotheses in brains and language models alike.

## Topic trajectories

### 1. Cross-frequency coupling needs generative models, not just sharper summary statistics.
The earliest core problem in this canon is methodological: phase–amplitude coupling (PAC) in neural time series is easy to over-claim because traditional pipelines depend on filter choices, Hilbert transforms, and post hoc summary metrics that can all manufacture apparent structure. Earlier work in neuroscience had already established PAC as biologically interesting — for example Canolty et al. (2006) and Tort et al. (2010) made PAC measurable and cognitively legible — but that literature also left the field with a tooling problem: how do you compare parameterizations on real data without simply optimizing the effect you hoped to see? The 2017 PLOS Computational Biology paper on driven auto-regressive models reframed the issue by making PAC estimation a probabilistic signal-modeling problem rather than a metric-selection problem, using likelihood as a principled criterion for model comparison and parameter selection instead of choosing the pipeline that yields the sharpest comodulogram [1][2][3].

What distinguishes this stance from adjacent work is not hostility to PAC, but skepticism about how PAC had been operationalized. The model treats slow oscillations as exogenous drivers of time-varying spectra, which lets the analysis ask harder questions than “is there coupling?” — for example whether the driver should be wide-band rather than nearly sinusoidal, whether amplitude fluctuations of the driver matter, and whether there is a measurable delay structure in the coupling [1]. This pushes the field away from handcrafted oscillation summaries and toward inference over explicit generative assumptions. Even when later work on waveform shape and spurious coupling kept the field honest, the contribution here remained distinctive: it did not merely warn about artifacts, it supplied a computational alternative and open-source implementation (`pactools`) that let researchers test competing hypotheses on the same data [1][4].

### 2. Brain rhythms are sparse, multichannel motifs rather than stationary Fourier atoms.
A second trajectory extends the same skepticism about sinusoidal assumptions into representation learning for electrophysiology. Classical spectral analysis treats neural recordings as if the relevant structure is well captured by sustained oscillations and fixed basis functions. But by the late 2010s there was growing evidence that many brain signals are transient, waveform-specific, and spatially distributed. The convolutional sparse coding line of work enters here by asking whether one can learn reusable waveform atoms directly from MEG/EEG data instead of imposing Fourier or wavelet dictionaries in advance. The 2017 NeurIPS paper on alpha-stable convolutional sparse coding introduced heavier-tailed noise modeling to make learned atoms more robust to the bursty morphology of neural signals, while the 2018 NeurIPS paper generalized the approach to multivariate electromagnetic recordings so that temporal motifs and spatial topographies are learned jointly [5][6].

The relation to prior art is important. Sparse coding itself was not new, nor was convolutional factorization; what changes in this body of work is the insistence that electromagnetic brain data are not just one-dimensional time series but spatiotemporal fields whose meaningful units are localized motifs with anatomical signatures. Relative to standard CSC, the multivariate formulation gives the model a chance to separate source-like spatial patterns rather than only denoise single channels; relative to ordinary spectral methods, it gives up closed-form interpretability in exchange for waveform realism [6]. The result is a trajectory from “estimate frequency content” toward “learn recurring physiological events.” This same sensibility explains why the papers often emphasize non-sinusoidal mu-like patterns and biological artifacts: the aim is not to purify data into ideal oscillators, but to discover what shapes the brain actually uses and where they live.

### 3. Voxelwise encoding became a feature-selection problem, not just a regression problem.
After moving to UC Berkeley’s Gallant Lab, the canon shifts from invasive and electromagnetic signals toward high-dimensional fMRI encoding models, but the methodological fingerprint stays recognizable: the central concern is still how to compare rich feature spaces without fooling yourself. Earlier voxelwise encoding work in the Gallant tradition had already shown that naturalistic stimuli and large semantic feature spaces can predict cortical responses, yet multi-feature models created a new bottleneck. If feature spaces are correlated, winner-take-all comparisons between representations or model layers become unstable, and ordinary ridge regression blurs together complementary and redundant features. The 2022 NeuroImage paper on banded ridge regression makes that issue explicit by treating each feature space as deserving its own regularization strength, turning regularization into a form of feature-space selection rather than mere shrinkage [7].

That move matters because it changes what a fitted encoding model can mean. Instead of only asking whether a pooled design matrix predicts voxels, the framework asks which representation families contribute uniquely enough to survive joint fitting. This is why the method supports both scientific interpretation and computational scale: it decomposes explained variance across feature spaces while remaining feasible for many voxels and many candidate representations, with the `himalaya` package released as infrastructure [7]. Later papers build directly on that logic. The 2021 workshop paper on mapping CNN layers to visual cortex uses joint fitting to avoid brittle layer-by-layer winner-take-all maps [8], and the 2024 Communications Biology paper on language timescales uses voxelwise models plus filtered language-model embeddings to ask where cortical timescale organization is shared across reading and listening [9]. The stance is consistent across these projects: better neuroscience comes from models that adjudicate among correlated representational hypotheses instead of reporting whichever single feature family looks best in isolation.

### 4. Mechanistic interpretability is treated as another representation-learning problem, but now inside language models.
The most recent phase at OpenAI carries the older methodological agenda into mechanistic interpretability. Sparse autoencoders (SAEs) had already become a popular tool for extracting putatively interpretable features from large language model activations, but the field faced familiar problems: tuning trade-offs between reconstruction and sparsity, dead latents, and weak evaluation criteria. The 2024/2025 work on scaling and evaluating sparse autoencoders treats these as first-class modeling problems, proposing k-sparse autoencoders to control sparsity directly, documenting scaling behavior across model sizes, and introducing evaluation metrics based on feature recovery, explainability of activation patterns, and sparsity of downstream effects [10]. In spirit this resembles the earlier PAC and voxelwise work: don’t trust a representation-learning method just because it yields interesting pictures; make its assumptions explicit and compare models with systematic diagnostics.

The 2025 paper on emergent misalignment then uses sparse autoencoders as part of a model-diffing workflow to trace how fine-tuning changes internal representations, arguing that generalized misalignment is associated with a small set of “persona” features in activation space [11]. The contrast with much of mechanistic interpretability is subtle but real. Rather than treating interpretability as one-off neuron archeology, this work treats it as a scalable latent-variable problem: learn a dictionary over activations, characterize how that dictionary behaves as scale increases, and then use the learned features as probes into behavioral shifts [10][11]. This makes the OpenAI phase feel less like a discontinuity than a transfer of method. The domain changes from brains to language models, but the recurring commitment is the same: if complex signals hide structure, the right response is not prettier heuristics but better models of the latent structure itself.

## Papers ranked by originality

### 1. Non-linear auto-regressive models for cross-frequency coupling in neural time series (2017)
**Source:** https://doi.org/10.1371/journal.pcbi.1005893
This is the clearest early statement of the canon’s style: a neuroscience measurement problem is turned into a probabilistic model-selection problem. Its contrastive difference is that, unlike standard PAC estimators that score coupling after fixed filtering choices, it evaluates explicit generative models by likelihood and uses that fit criterion to compare parameterizations instead of optimizing the visual sharpness of the coupling map [1].

### 2. Feature-space selection with banded ridge regression (2022)
**Source:** https://doi.org/10.1016/j.neuroimage.2022.119728
This paper matters because it upgrades voxelwise encoding from “fit a big ridge model” to “decide which representation families deserve explanatory credit under joint competition.” Its contrastive difference is that it assigns regularization by feature space rather than globally, letting the model suppress redundant representations instead of blending them together by default [7].

### 3. Scaling and evaluating sparse autoencoders (2024)
**Source:** https://openreview.net/forum?id=tcsZt9ZNKD
This paper is significant because it brings scaling-law and evaluation discipline into mechanistic interpretability, a field that often advanced through vivid case studies more than standardized measurement. Its contrastive difference is that it studies SAEs as scalable objects with explicit sparsity control and feature-quality metrics, not merely as ad hoc tools for showcasing interpretable neurons or latents [10].

### 4. Multivariate convolutional sparse coding for electromagnetic brain signals (2018)
**Source:** https://arxiv.org/abs/1805.09654v2
This work is the key bridge from signal-processing skepticism to learned representations of neural data. Its contrastive difference is that it learns temporal motifs and spatial topographies jointly, so the basic unit of explanation becomes a multichannel physiological pattern rather than a single-channel spectral component or denoised waveform [6].

## Coverage gaps
- No separate institutional lab website was found; the canon is reconstructed from the PI homepage (`https://tomdlt.github.io/`) plus public indices.
- Google Scholar exposed some extra software/data outputs not cleanly mirrored on the homepage; these were not merged into the main canon without cleaner primary records.
- `researcher` and `verifier` subagents both returned empty output files in this runtime, so trajectory synthesis and verification were completed by the lead agent.

## Sources

[1] https://doi.org/10.1371/journal.pcbi.1005893
[2] https://doi.org/10.1126/science.1128115
[3] https://doi.org/10.1152/jn.00106.2010
[4] https://doi.org/10.1016/j.tics.2016.12.008
[5] https://papers.nips.cc/paper/6710-learning-the-morphology-of-brain-signals-using-alpha-stable-convolutional-sparse-coding
[6] https://arxiv.org/abs/1805.09654v2
[7] https://doi.org/10.1016/j.neuroimage.2022.119728
[8] https://openreview.net/forum?id=EcoKpq43Ul8
[9] https://doi.org/10.1038/s42003-024-05909-z
[10] https://openreview.net/forum?id=tcsZt9ZNKD
[11] https://arxiv.org/abs/2506.19823
