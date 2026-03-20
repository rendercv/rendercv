// Import the rendercv function and all the refactored components
#import "@preview/rendercv:0.2.0": *

// Apply the rendercv template with custom configuration
#show: rendercv.with(
  name: "John Doe",
  footer: context { [#emph[John Doe -- #str(here().page())\/#str(counter(page).final().first())]] },
  top-note: [ #emph[Last updated in Dec 2025] ],
  locale-catalog-language: "en",
  page-size: "us-letter",
  page-top-margin: 0.7in,
  page-bottom-margin: 0.7in,
  page-left-margin: 0.7in,
  page-right-margin: 0.7in,
  page-show-footer: false,
  page-show-top-note: true,
  colors-body: rgb(0, 0, 0),
  colors-name: rgb(0, 0, 0),
  colors-headline: rgb(0, 0, 0),
  colors-connections: rgb(0, 0, 0),
  colors-section-titles: rgb(0, 0, 0),
  colors-links: rgb(0, 0, 0),
  colors-footer: rgb(128, 128, 128),
  colors-top-note: rgb(128, 128, 128),
  typography-line-spacing: 0.6em,
  typography-alignment: "justified",
  typography-date-and-location-column-alignment: right,
  typography-font-family-body: "XCharter",
  typography-font-family-name: "XCharter",
  typography-font-family-headline: "XCharter",
  typography-font-family-connections: "XCharter",
  typography-font-family-section-titles: "XCharter",
  typography-font-size-body: 10pt,
  typography-font-size-name: 25pt,
  typography-font-size-headline: 10pt,
  typography-font-size-connections: 10pt,
  typography-font-size-section-titles: 1.2em,
  typography-small-caps-name: false,
  typography-small-caps-headline: false,
  typography-small-caps-connections: false,
  typography-small-caps-section-titles: false,
  typography-bold-name: false,
  typography-bold-headline: false,
  typography-bold-connections: false,
  typography-bold-section-titles: true,
  links-underline: true,
  links-show-external-link-icon: false,
  header-alignment: center,
  header-photo-width: 3.5cm,
  header-space-below-name: 0.7cm,
  header-space-below-headline: 0.7cm,
  header-space-below-connections: 0.7cm,
  header-connections-hyperlink: true,
  header-connections-show-icons: false,
  header-connections-display-urls-instead-of-usernames: true,
  header-connections-separator: "|",
  header-connections-space-between-connections: 0.5cm,
  section-titles-type: "with_full_line",
  section-titles-line-thickness: 0.5pt,
  section-titles-space-above: 0.5cm,
  section-titles-space-below: 0.3cm,
  sections-allow-page-break: true,
  sections-space-between-text-based-entries: 0.15cm,
  sections-space-between-regular-entries: 0.42cm,
  entries-date-and-location-width: 4.15cm,
  entries-side-space: 0cm,
  entries-space-between-columns: 0.1cm,
  entries-allow-page-break: false,
  entries-short-second-row: false,
  entries-summary-space-left: 0cm,
  entries-summary-space-above: 0.08cm,
  entries-highlights-bullet:  text(13pt, [•], baseline: -0.6pt) ,
  entries-highlights-nested-bullet:  text(13pt, [•], baseline: -0.6pt) ,
  entries-highlights-space-left: 0cm,
  entries-highlights-space-above: 0.08cm,
  entries-highlights-space-between-items: 0.08cm,
  entries-highlights-space-between-bullet-and-text: 0.3em,
  date: datetime(
    year: 2025,
    month: 12,
    day: 5,
  ),
)


= John Doe

#connections(
  [San Francisco, CA],
  [#link("mailto:john.doe@email.com", icon: false, if-underline: false, if-color: false)[john.doe\@email.com]],
  [#link("https://rendercv.com/", icon: false, if-underline: false, if-color: false)[rendercv.com]],
  [#link("https://linkedin.com/in/rendercv", icon: false, if-underline: false, if-color: false)[linkedin.com\/in\/rendercv]],
  [#link("https://github.com/rendercv", icon: false, if-underline: false, if-color: false)[github.com\/rendercv]],
)


== Welcome to RenderCV

RenderCV reads a CV written in a YAML file, and generates a PDF with professional typography.

See the #link("https://docs.rendercv.com")[documentation] for more details.

== Education

#education-entry(
  [
    #strong[Princeton University], PhD in Computer Science -- Princeton, NJ
    
  ],
  [
    Sept 2018 – May 2023
    
  ],
  main-column-second-row: [
    - Thesis: Efficient Neural Architecture Search for Resource-Constrained Deployment
    
    - Advisor: Prof. Sanjeev Arora
    
    - NSF Graduate Research Fellowship, Siebel Scholar (Class of 2022)
    
  ],
)

#education-entry(
  [
    #strong[Boğaziçi University], BS in Computer Engineering -- Istanbul, Türkiye
    
  ],
  [
    Sept 2014 – June 2018
    
  ],
  main-column-second-row: [
    - GPA: 3.97\/4.00, Valedictorian
    
    - Fulbright Scholarship recipient for graduate studies
    
  ],
)

== Experience

#regular-entry(
  [
    #strong[Co-Founder & CTO], Nexus AI -- San Francisco, CA
    
  ],
  [
    June 2023 – present
    
  ],
  main-column-second-row: [
    - Built foundation model infrastructure serving 2M+ monthly API requests with 99.97\% uptime
    
    - Raised \$18M Series A led by Sequoia Capital, with participation from a16z and Founders Fund
    
    - Scaled engineering team from 3 to 28 across ML research, platform, and applied AI divisions
    
    - Developed proprietary inference optimization reducing latency by 73\% compared to baseline
    
  ],
)

#regular-entry(
  [
    #strong[Research Intern], NVIDIA Research -- Santa Clara, CA
    
  ],
  [
    May 2022 – Aug 2022
    
  ],
  main-column-second-row: [
    - Designed sparse attention mechanism reducing transformer memory footprint by 4.2x
    
    - Co-authored paper accepted at NeurIPS 2022 (spotlight presentation, top 5\% of submissions)
    
  ],
)

#regular-entry(
  [
    #strong[Research Intern], Google DeepMind -- London, UK
    
  ],
  [
    May 2021 – Aug 2021
    
  ],
  main-column-second-row: [
    - Developed reinforcement learning algorithms for multi-agent coordination
    
    - Published research at top-tier venues with significant academic impact
    
      - ICML 2022 main conference paper, cited 340+ times within two years
    
      - NeurIPS 2022 workshop paper on emergent communication protocols
    
      - Invited journal extension in JMLR (2023)
    
  ],
)

#regular-entry(
  [
    #strong[Research Intern], Apple ML Research -- Cupertino, CA
    
  ],
  [
    May 2020 – Aug 2020
    
  ],
  main-column-second-row: [
    - Created on-device neural network compression pipeline deployed across 50M+ devices
    
    - Filed 2 patents on efficient model quantization techniques for edge inference
    
  ],
)

#regular-entry(
  [
    #strong[Research Intern], Microsoft Research -- Redmond, WA
    
  ],
  [
    May 2019 – Aug 2019
    
  ],
  main-column-second-row: [
    - Implemented novel self-supervised learning framework for low-resource language modeling
    
    - Research integrated into Azure Cognitive Services, reducing training data requirements by 60\%
    
  ],
)

== Projects

#regular-entry(
  [
    #strong[#link("https://github.com/")[FlashInfer]]
    
  ],
  [
    Jan 2023 – present
    
  ],
  main-column-second-row: [
    #summary[Open-source library for high-performance LLM inference kernels]
    
    - Achieved 2.8x speedup over baseline attention implementations on A100 GPUs
    
    - Adopted by 3 major AI labs, 8,500+ GitHub stars, 200+ contributors
    
  ],
)

#regular-entry(
  [
    #strong[#link("https://github.com/")[NeuralPrune]]
    
  ],
  [
    Jan 2021
    
  ],
  main-column-second-row: [
    #summary[Automated neural network pruning toolkit with differentiable masks]
    
    - Reduced model size by 90\% with less than 1\% accuracy degradation on ImageNet
    
    - Featured in PyTorch ecosystem tools, 4,200+ GitHub stars
    
  ],
)

== Publications

#regular-entry(
  [
    #strong[Sparse Mixture-of-Experts at Scale: Efficient Routing for Trillion-Parameter Models]
    
  ],
  [
    July 2023
    
  ],
  main-column-second-row: [
    #emph[John Doe], Sarah Williams, David Park
    
    #link("https://doi.org/10.1234/neurips.2023.1234")[10.1234\/neurips.2023.1234] (NeurIPS 2023)
    
  ],
)

#regular-entry(
  [
    #strong[Neural Architecture Search via Differentiable Pruning]
    
  ],
  [
    Dec 2022
    
  ],
  main-column-second-row: [
    James Liu, #emph[John Doe]
    
    #link("https://doi.org/10.1234/neurips.2022.5678")[10.1234\/neurips.2022.5678] (NeurIPS 2022, Spotlight)
    
  ],
)

#regular-entry(
  [
    #strong[Multi-Agent Reinforcement Learning with Emergent Communication]
    
  ],
  [
    July 2022
    
  ],
  main-column-second-row: [
    Maria Garcia, #emph[John Doe], Tom Anderson
    
    #link("https://doi.org/10.1234/icml.2022.9012")[10.1234\/icml.2022.9012] (ICML 2022)
    
  ],
)

#regular-entry(
  [
    #strong[On-Device Model Compression via Learned Quantization]
    
  ],
  [
    May 2021
    
  ],
  main-column-second-row: [
    #emph[John Doe], Kevin Wu
    
    #link("https://doi.org/10.1234/iclr.2021.3456")[10.1234\/iclr.2021.3456] (ICLR 2021, Best Paper Award)
    
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

== Any Section Title

You can use any section title you want.

You can choose any entry type for the section: `TextEntry`, `ExperienceEntry`, `EducationEntry`, `PublicationEntry`, `BulletEntry`, `NumberedEntry`, or `ReversedNumberedEntry`.

Markdown syntax is supported everywhere.

The `design` field in YAML gives you control over almost any aspect of your CV design.

See the #link("https://docs.rendercv.com")[documentation] for more details.
