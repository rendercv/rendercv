// Import the rendercv function and all the refactored components
#import "@preview/rendercv:0.3.0": *

// Apply the rendercv template with custom configuration
#show: rendercv.with(
  name: "John Doe",
  title: "John Doe - CV",
  footer: context { [#emph[John Doe -- #str(here().page())\/#str(counter(page).final().first())]] },
  top-note: [ #emph[Last updated in Apr 2026] ],
  locale-catalog-language: "en",
  text-direction: ltr,
  page-size: "us-letter",
  page-top-margin: 0.6in,
  page-bottom-margin: 0.6in,
  page-left-margin: 0.6in,
  page-right-margin: 0.6in,
  page-show-footer: true,
  page-show-top-note: true,
  colors-body: rgb(35, 31, 32),
  colors-name: rgb(155, 35, 25),
  colors-headline: rgb(90, 60, 55),
  colors-connections: rgb(100, 75, 68),
  colors-section-titles: rgb(155, 35, 25),
  colors-links: rgb(155, 35, 25),
  colors-footer: rgb(140, 125, 118),
  colors-top-note: rgb(140, 125, 118),
  typography-line-spacing: 0.6em,
  typography-alignment: "justified-with-no-hyphenation",
  typography-date-and-location-column-alignment: right,
  typography-font-family-body: "Ubuntu",
  typography-font-family-name: "Gentium Book Plus",
  typography-font-family-headline: "Gentium Book Plus",
  typography-font-family-connections: "Ubuntu",
  typography-font-family-section-titles: "Ubuntu",
  typography-font-size-body: 10pt,
  typography-font-size-name: 30pt,
  typography-font-size-headline: 10.5pt,
  typography-font-size-connections: 9pt,
  typography-font-size-section-titles: 1.25em,
  typography-small-caps-name: false,
  typography-small-caps-headline: true,
  typography-small-caps-connections: false,
  typography-small-caps-section-titles: true,
  typography-bold-name: true,
  typography-bold-headline: false,
  typography-bold-connections: false,
  typography-bold-section-titles: false,
  links-underline: true,
  links-show-external-link-icon: false,
  header-alignment: center,
  header-photo-width: 3.5cm,
  header-space-below-name: 0.5cm,
  header-space-below-headline: 0.4cm,
  header-space-below-connections: 0.6cm,
  header-connections-hyperlink: true,
  header-connections-show-icons: false,
  header-connections-display-urls-instead-of-usernames: false,
  header-connections-separator: "·",
  header-connections-space-between-connections: 0.5cm,
  section-titles-type: "centered_without_line",
  section-titles-line-thickness: 0.5pt,
  section-titles-space-above: 0.55cm,
  section-titles-space-below: 0.25cm,
  sections-allow-page-break: true,
  sections-space-between-text-based-entries: 0.3em,
  sections-space-between-regular-entries: 1.1em,
  entries-date-and-location-width: 4.15cm,
  entries-side-space: 0.1cm,
  entries-space-between-columns: 0.15cm,
  entries-allow-page-break: false,
  entries-short-second-row: false,
  entries-degree-width: 1cm,
  entries-summary-space-left: 0cm,
  entries-summary-space-above: 0.05cm,
  entries-highlights-bullet:  "◆" ,
  entries-highlights-nested-bullet:  "◦" ,
  entries-highlights-space-left: 0.15cm,
  entries-highlights-space-above: 0.05cm,
  entries-highlights-space-between-items: 0.04cm,
  entries-highlights-space-between-bullet-and-text: 0.5em,
  date: datetime(
    year: 2026,
    month: 4,
    day: 17,
  ),
)


= John Doe

#connections(
  [San Francisco, CA],
  [#link("mailto:john.doe@email.com", icon: false, if-underline: false, if-color: false)[john.doe\@email.com]],
  [#link("https://rendercv.com/", icon: false, if-underline: false, if-color: false)[rendercv.com]],
  [#link("https://linkedin.com/in/rendercv", icon: false, if-underline: false, if-color: false)[rendercv]],
  [#link("https://github.com/rendercv", icon: false, if-underline: false, if-color: false)[rendercv]],
)


== Welcome to RenderCV

RenderCV reads a CV written in a YAML file, and generates a PDF with professional typography.

Each section title is arbitrary.

You can choose any of the 9 entry types for each section.

Markdown syntax is supported everywhere. This is #strong[bold], #emph[italic], and #link("https://example.com")[link].

== Education

#education-entry(
  [
    #strong[Princeton University] -- Princeton, NJ

  ],
  [
    Sept 2018 – May 2023

  ],
  main-column-second-row: [
    #emph[PhD in Computer Science]

    - Thesis: Efficient Neural Architecture Search for Resource-Constrained Deployment

    - Advisor: Prof. Sanjeev Arora

    - NSF Graduate Research Fellowship, Siebel Scholar (Class of 2022)

  ],
)

#education-entry(
  [
    #strong[Boğaziçi University] -- Istanbul, Türkiye

  ],
  [
    Sept 2014 – June 2018

  ],
  main-column-second-row: [
    #emph[BS in Computer Engineering]

    - GPA: 3.97\/4.00, Valedictorian

    - Fulbright Scholarship recipient for Graduate Studies

  ],
)

== Experience

#regular-entry(
  [
    #strong[Nexus AI] -- San Francisco, CA

  ],
  [
    June 2023 – present

  ],
  main-column-second-row: [
    #emph[Co-Founder & CTO]

    - Built foundation model infrastructure serving 2M+ monthly API requests with 99.97\% uptime

    - Raised \$18M Series A led by Sequoia Capital, with participation from a16z and Founders Fund

    - Scaled engineering team from 3 to 28 across ML research, platform, and applied AI divisions

    - Developed proprietary inference optimization reducing latency by 73\% compared to baseline

  ],
)

#regular-entry(
  [
    #strong[NVIDIA Research] -- Santa Clara, CA

  ],
  [
    May 2022 – Aug 2022

  ],
  main-column-second-row: [
    #emph[Research Intern]

    - Designed sparse attention mechanism reducing transformer memory footprint by 4.2x

    - Co-authored paper accepted at NeurIPS 2022 (spotlight presentation, top 5\% of submissions)

  ],
)

#regular-entry(
  [
    #strong[Google DeepMind] -- London, UK

  ],
  [
    May 2021 – Aug 2021

  ],
  main-column-second-row: [
    #emph[Research Intern]

    - Developed reinforcement learning algorithms for multi-agent coordination

    - Published research at top-tier venues with significant academic impact

    - ICML 2022 main conference paper, cited 340+ times within two years

    - NeurIPS 2022 workshop paper on emergent communication protocols

    - Invited journal extension in JMLR (2023)

  ],
)

#regular-entry(
  [
    #strong[Apple ML Research] -- Cupertino, CA

  ],
  [
    May 2020 – Aug 2020

  ],
  main-column-second-row: [
    #emph[Research Intern]

    - Created on-device neural network compression pipeline deployed across 50M+ devices

    - Filed 2 patents on efficient model quantization techniques for edge inference

  ],
)

#regular-entry(
  [
    #strong[Microsoft Research] -- Redmond, WA

  ],
  [
    May 2019 – Aug 2019

  ],
  main-column-second-row: [
    #emph[Research Intern]

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
