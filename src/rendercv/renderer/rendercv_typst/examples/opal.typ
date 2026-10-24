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
  page-top-margin: 0.65in,
  page-bottom-margin: 0.65in,
  page-left-margin: 0.65in,
  page-right-margin: 0.65in,
  page-show-footer: false,
  page-show-top-note: false,
  colors-body: rgb(0, 0, 0),
  colors-name: rgb(0, 100, 90),
  colors-headline: rgb(0, 80, 72),
  colors-connections: rgb(0, 80, 72),
  colors-section-titles: rgb(0, 100, 90),
  colors-links: rgb(0, 100, 90),
  colors-footer: rgb(100, 140, 135),
  colors-top-note: rgb(100, 140, 135),
  typography-line-spacing: 0.6em,
  typography-alignment: "left",
  typography-date-and-location-column-alignment: right,
  typography-font-family-body: "Lato",
  typography-font-family-name: "Lato",
  typography-font-family-headline: "Lato",
  typography-font-family-connections: "Lato",
  typography-font-family-section-titles: "Lato",
  typography-font-size-body: 10pt,
  typography-font-size-name: 26pt,
  typography-font-size-headline: 10pt,
  typography-font-size-connections: 9pt,
  typography-font-size-section-titles: 1.2em,
  typography-small-caps-name: false,
  typography-small-caps-headline: true,
  typography-small-caps-connections: false,
  typography-small-caps-section-titles: true,
  typography-bold-name: true,
  typography-bold-headline: false,
  typography-bold-connections: false,
  typography-bold-section-titles: false,
  links-underline: false,
  links-show-external-link-icon: false,
  header-alignment: center,
  header-photo-width: 3.5cm,
  header-space-below-name: 0.3cm,
  header-space-below-headline: 0.3cm,
  header-space-below-connections: 0.6cm,
  header-connections-hyperlink: true,
  header-connections-show-icons: true,
  header-connections-display-urls-instead-of-usernames: false,
  header-connections-separator: "•",
  header-connections-space-between-connections: 0.5cm,
  section-titles-type: "centered_without_line",
  section-titles-line-thickness: 0.4pt,
  section-titles-space-above: 0.55cm,
  section-titles-space-below: 0.25cm,
  sections-allow-page-break: true,
  sections-space-between-text-based-entries: 0.3em,
  sections-space-between-regular-entries: 1.1em,
  entries-date-and-location-width: 4.15cm,
  entries-side-space: 0.15cm,
  entries-space-between-columns: 0.1cm,
  entries-allow-page-break: false,
  entries-short-second-row: true,
  entries-degree-width: 1cm,
  entries-summary-space-left: 0cm,
  entries-summary-space-above: 0.04cm,
  entries-highlights-bullet:  "◦" ,
  entries-highlights-nested-bullet:  "◦" ,
  entries-highlights-space-left: 0.15cm,
  entries-highlights-space-above: 0.04cm,
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
  [#connection-with-icon("location-dot")[San Francisco, CA]],
  [#link("mailto:john.doe@email.com", icon: false, if-underline: false, if-color: false)[#connection-with-icon("envelope")[john.doe\@email.com]]],
  [#link("https://rendercv.com/", icon: false, if-underline: false, if-color: false)[#connection-with-icon("link")[rendercv.com]]],
  [#link("https://linkedin.com/in/rendercv", icon: false, if-underline: false, if-color: false)[#connection-with-icon("linkedin")[rendercv]]],
  [#link("https://github.com/rendercv", icon: false, if-underline: false, if-color: false)[#connection-with-icon("github")[rendercv]]],
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

    PhD in Computer Science

    - Thesis: Efficient Neural Architecture Search for Resource-Constrained Deployment

    - Advisor: Prof. Sanjeev Arora

    - NSF Graduate Research Fellowship, Siebel Scholar (Class of 2022)

  ],
  [
    Sept 2018 – May 2023

  ],
)

#education-entry(
  [
    #strong[Boğaziçi University] -- Istanbul, Türkiye

    BS in Computer Engineering

    - GPA: 3.97\/4.00, Valedictorian

    - Fulbright Scholarship recipient for Graduate Studies

  ],
  [
    Sept 2014 – June 2018

  ],
)

== Experience

#regular-entry(
  [
    #strong[Nexus AI], #emph[Co-Founder & CTO] -- San Francisco, CA

    - Built foundation model infrastructure serving 2M+ monthly API requests with 99.97\% uptime

    - Raised \$18M Series A led by Sequoia Capital, with participation from a16z and Founders Fund

    - Scaled engineering team from 3 to 28 across ML research, platform, and applied AI divisions

    - Developed proprietary inference optimization reducing latency by 73\% compared to baseline

  ],
  [
    June 2023 – present

  ],
)

#regular-entry(
  [
    #strong[NVIDIA Research], #emph[Research Intern] -- Santa Clara, CA

    - Designed sparse attention mechanism reducing transformer memory footprint by 4.2x

    - Co-authored paper accepted at NeurIPS 2022 (spotlight presentation, top 5\% of submissions)

  ],
  [
    May 2022 – Aug 2022

  ],
)

#regular-entry(
  [
    #strong[Google DeepMind], #emph[Research Intern] -- London, UK

    - Developed reinforcement learning algorithms for multi-agent coordination

    - Published research at top-tier venues with significant academic impact

    - ICML 2022 main conference paper, cited 340+ times within two years

    - NeurIPS 2022 workshop paper on emergent communication protocols

    - Invited journal extension in JMLR (2023)

  ],
  [
    May 2021 – Aug 2021

  ],
)

#regular-entry(
  [
    #strong[Apple ML Research], #emph[Research Intern] -- Cupertino, CA

    - Created on-device neural network compression pipeline deployed across 50M+ devices

    - Filed 2 patents on efficient model quantization techniques for edge inference

  ],
  [
    May 2020 – Aug 2020

  ],
)

#regular-entry(
  [
    #strong[Microsoft Research], #emph[Research Intern] -- Redmond, WA

    - Implemented novel self-supervised learning framework for low-resource language modeling

    - Research integrated into Azure Cognitive Services, reducing training data requirements by 60\%

  ],
  [
    May 2019 – Aug 2019

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
