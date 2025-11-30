// Import the rendercv function and all the refactored components
#import "@preview/rendercv:0.1.0": *

// Apply the rendercv template with custom configuration
#show: rendercv.with(
  name: "John Doe",
  footer: context { [#emph[John Doe -- #str(here().page())\/#str(counter(page).final().first())]] },
  top-note: [ #emph[Last updated in Nov 2025] ],
  locale-catalog-language: "en",
  page-size: "us-letter",
  page-top-margin: 0.7in,
  page-bottom-margin: 0.7in,
  page-left-margin: 0.7in,
  page-right-margin: 0.7in,
  page-show-footer: true,
  page-show-top-note: true,
  colors-body: rgb(0, 0, 0),
  colors-name: rgb(0, 79, 144),
  colors-headline: rgb(0, 79, 144),
  colors-connections: rgb(0, 79, 144),
  colors-section-titles: rgb(0, 79, 144),
  colors-links: rgb(0, 79, 144),
  colors-footer: rgb(128, 128, 128),
  colors-top-note: rgb(128, 128, 128),
  typography-line-spacing: 0.6em,
  typography-alignment: "justified",
  typography-date-and-location-column-alignment: right,
  typography-font-family-body: "Source Sans 3",
  typography-font-family-name: "Source Sans 3",
  typography-font-family-headline: "Source Sans 3",
  typography-font-family-connections: "Source Sans 3",
  typography-font-family-section-titles: "Source Sans 3",
  typography-font-size-body: 10pt,
  typography-font-size-name: 30pt,
  typography-font-size-headline: 10pt,
  typography-font-size-connections: 10pt,
  typography-font-size-section-titles: 1.4em,
  typography-small-caps-name: false,
  typography-small-caps-headline: false,
  typography-small-caps-connections: false,
  typography-small-caps-section-titles: false,
  typography-bold-name: false,
  typography-bold-headline: false,
  typography-bold-connections: false,
  typography-bold-section-titles: false,
  links-underline: false,
  links-show-external-link-icon: false,
  header-alignment: left,
  header-photo-width: 3.5cm,
  header-space-below-name: 0.7cm,
  header-space-below-headline: 0.7cm,
  header-space-below-connections: 0.7cm,
  header-connections-hyperlink: true,
  header-connections-show-icons: false,
  header-connections-display-urls-instead-of-usernames: true,
  header-connections-separator: "",
  header-connections-space-between-connections: 0.5cm,
  section-titles-type: "with_partial_line",
  section-titles-line-thickness: 0.5pt,
  section-titles-space-above: 0.5cm,
  section-titles-space-below: 0.3cm,
  sections-allow-page-break: true,
  sections-space-between-text-based-entries: 0.3em,
  sections-space-between-regular-entries: 1.2em,
  entries-date-and-location-width: 4.15cm,
  entries-side-space: 0.2cm,
  entries-space-between-columns: 0.1cm,
  entries-allow-page-break: false,
  entries-short-second-row: true,
  entries-summary-space-left: 0cm,
  entries-summary-space-above: 0cm,
  entries-highlights-bullet:  "•" ,
  entries-highlights-nested-bullet:  "•" ,
  entries-highlights-space-left: 0.15cm,
  entries-highlights-space-above: 0cm,
  entries-highlights-space-between-items: 0cm,
  entries-highlights-space-between-bullet-and-text: 0.5em,
  date: datetime(
    year: 2025,
    month: 11,
    day: 29,
  ),
)


= John Doe

#connections(
  [San Francisco, CA],
  [#link("mailto:john.doe@email.com", icon: false, if-underline: false, if-color: false)[john.doe\@email.com]],
  [#link("https://johndoe.ai/", icon: false, if-underline: false, if-color: false)[johndoe.ai]],
  [#link("https://linkedin.com/in/johndoe", icon: false, if-underline: false, if-color: false)[linkedin.com\/in\/johndoe]],
  [#link("https://github.com/johndoe", icon: false, if-underline: false, if-color: false)[github.com\/johndoe]],
)


== Summary

AI researcher and entrepreneur with a track record of publishing at top venues (NeurIPS, ICML, ICLR) and translating research into products used by millions.

Currently building #link("https://nexusai.com")[Nexus AI], a VC-backed infrastructure company for efficient large model deployment.

== Education

#education-entry(
  [
    #strong[Princeton University], Computer Science
    
    - Thesis: Efficient Neural Architecture Search for Resource-Constrained Deployment
    
    - Advisor: Prof. Sanjeev Arora
    
    - NSF Graduate Research Fellowship, Siebel Scholar (Class of 2022)
    
  ],
  [
    Princeton, NJ
    
    Sept 2018 – May 2023
    
  ],
  degree-column: [
    #strong[PhD]
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], Computer Engineering
    
    - GPA: 3.97\/4.00, Valedictorian
    
    - Fulbright Scholarship recipient for graduate studies
    
  ],
  [
    Istanbul, Türkiye
    
    Sept 2014 – June 2018
    
  ],
  degree-column: [
    #strong[BS]
  ],
)

== Experience

#regular-entry(
  [
    #strong[Nexus AI], Co-Founder & CTO
    
    - Built foundation model infrastructure serving 2M+ monthly API requests with 99.97\% uptime
    
    - Raised \$18M Series A led by Sequoia Capital, with participation from a16z and Founders Fund
    
    - Scaled engineering team from 3 to 28 across ML research, platform, and applied AI divisions
    
    - Developed proprietary inference optimization reducing latency by 73\% compared to baseline
    
  ],
  [
    San Francisco, CA
    
    June 2023 – present
    
    2 years 7 months
    
  ],
)

#regular-entry(
  [
    #strong[NVIDIA Research], Research Intern
    
    - Designed sparse attention mechanism reducing transformer memory footprint by 4.2x
    
    - Co-authored paper accepted at NeurIPS 2022 (spotlight presentation, top 5\% of submissions)
    
  ],
  [
    Santa Clara, CA
    
    May 2022 – Aug 2022
    
    4 months
    
  ],
)

#regular-entry(
  [
    #strong[Google DeepMind], Research Intern
    
    - Developed reinforcement learning algorithms for multi-agent coordination
    
    - Published research at top-tier venues with significant academic impact
    
      - ICML 2022 main conference paper, cited 340+ times within two years
    
      - NeurIPS 2022 workshop paper on emergent communication protocols
    
      - Invited journal extension in JMLR (2023)
    
  ],
  [
    London, UK
    
    May 2021 – Aug 2021
    
    4 months
    
  ],
)

#regular-entry(
  [
    #strong[Apple ML Research], Research Intern
    
    - Created on-device neural network compression pipeline deployed across 50M+ devices
    
    - Filed 2 patents on efficient model quantization techniques for edge inference
    
  ],
  [
    Cupertino, CA
    
    May 2020 – Aug 2020
    
    4 months
    
  ],
)

#regular-entry(
  [
    #strong[Microsoft Research], Research Intern
    
    - Implemented novel self-supervised learning framework for low-resource language modeling
    
    - Research integrated into Azure Cognitive Services, reducing training data requirements by 60\%
    
  ],
  [
    Redmond, WA
    
    May 2019 – Aug 2019
    
    4 months
    
  ],
)

== Projects

#regular-entry(
  [
    #strong[#link("https://github.com/")[FlashInfer]]
    
    #summary[Open-source library for high-performance LLM inference kernels]
    
    - Achieved 2.8x speedup over baseline attention implementations on A100 GPUs
    
    - Adopted by 3 major AI labs, 8,500+ GitHub stars, 200+ contributors
    
  ],
  [
    Jan 2023 – present
    
  ],
)

#regular-entry(
  [
    #strong[#link("https://github.com/")[NeuralPrune]]
    
    #summary[Automated neural network pruning toolkit with differentiable masks]
    
    - Reduced model size by 90\% with less than 1\% accuracy degradation on ImageNet
    
    - Featured in PyTorch ecosystem tools, 4,200+ GitHub stars
    
  ],
  [
    Jan 2021
    
  ],
)

== Publications

#regular-entry(
  [
    #strong[Sparse Mixture-of-Experts at Scale: Efficient Routing for Trillion-Parameter Models]
    
    #emph[John Doe], Sarah Williams, David Park
    
    #link("https://doi.org/10.1234/neurips.2023.1234")[10.1234\/neurips.2023.1234] (NeurIPS 2023)
    
  ],
  [
    July 2023
    
  ],
)

#regular-entry(
  [
    #strong[Neural Architecture Search via Differentiable Pruning]
    
    James Liu, #emph[John Doe]
    
    #link("https://doi.org/10.1234/neurips.2022.5678")[10.1234\/neurips.2022.5678] (NeurIPS 2022, Spotlight)
    
  ],
  [
    Dec 2022
    
  ],
)

#regular-entry(
  [
    #strong[Multi-Agent Reinforcement Learning with Emergent Communication]
    
    Maria Garcia, #emph[John Doe], Tom Anderson
    
    #link("https://doi.org/10.1234/icml.2022.9012")[10.1234\/icml.2022.9012] (ICML 2022)
    
  ],
  [
    July 2022
    
  ],
)

#regular-entry(
  [
    #strong[On-Device Model Compression via Learned Quantization]
    
    #emph[John Doe], Kevin Wu
    
    #link("https://doi.org/10.1234/iclr.2021.3456")[10.1234\/iclr.2021.3456] (ICLR 2021, Best Paper Award)
    
  ],
  [
    May 2021
    
  ],
)

== Selected Honors

- MIT Technology Review 35 Under 35 Innovators (2024)

- Forbes 30 Under 30 in Enterprise Technology (2024)

- ACM Doctoral Dissertation Award Honorable Mention (2023)

- Google PhD Fellowship in Machine Learning (2020 – 2023)

- Fulbright Scholarship for Graduate Studies (2018)

== Skills

#strong[Languages:] Python, C++, CUDA, Rust, Julia

#strong[ML Frameworks:] PyTorch, JAX, TensorFlow, Triton, ONNX

#strong[Infrastructure:] Kubernetes, Ray, distributed training, AWS, GCP

#strong[Research Areas:] Neural architecture search, model compression, efficient inference, multi-agent RL

== Patents

+ Adaptive Quantization for Neural Network Inference on Edge Devices (US Patent 11,234,567)

+ Dynamic Sparsity Patterns for Efficient Transformer Attention (US Patent 11,345,678)

+ Hardware-Aware Neural Architecture Search Method (US Patent 11,456,789)

== Invited Talks

#reversed-numbered-entries(
  [

+ Scaling Laws for Efficient Inference — Stanford HAI Symposium (2024)

+ Building AI Infrastructure for the Next Decade — TechCrunch Disrupt (2024)

+ From Research to Production: Lessons in ML Systems — NeurIPS Workshop (2023)

+ Efficient Deep Learning: A Practitioner's Perspective — Google Tech Talk (2022)
  ],
)
