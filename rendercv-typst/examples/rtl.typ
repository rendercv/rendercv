// RTL (Right-to-Left) example with Persian content.
// Requires a Persian font such as "Vazirmatn" to be installed.
#import "@preview/rendercv:0.2.0": *

#show: rendercv.with(
  name: "علی احمدی",
  title: "رزومه علی احمدی",
  footer: context { [صفحه #str(here().page()) از #str(counter(page).final().first())] },
  top-note: [ آخرین بروزرسانی: بهمن ۱۴۰۴ ],
  locale-catalog-language: "fa",
  text-direction: rtl,
  page-size: "a4",
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
  typography-date-and-location-column-alignment: left,
  typography-font-family-body: "Vazirmatn",
  typography-font-family-name: "Vazirmatn",
  typography-font-family-headline: "Vazirmatn",
  typography-font-family-connections: "Vazirmatn",
  typography-font-family-section-titles: "Vazirmatn",
  typography-font-size-body: 10pt,
  typography-font-size-name: 30pt,
  typography-font-size-headline: 10pt,
  typography-font-size-connections: 10pt,
  typography-font-size-section-titles: 1.4em,
  typography-small-caps-name: false,
  typography-small-caps-headline: false,
  typography-small-caps-connections: false,
  typography-small-caps-section-titles: false,
  typography-bold-name: true,
  typography-bold-headline: false,
  typography-bold-connections: false,
  typography-bold-section-titles: true,
  links-underline: false,
  links-show-external-link-icon: false,
  header-alignment: right,
  header-photo-width: 3.5cm,
  header-space-below-name: 0.7cm,
  header-space-below-headline: 0.7cm,
  header-space-below-connections: 0.7cm,
  header-connections-hyperlink: true,
  header-connections-show-icons: true,
  header-connections-display-urls-instead-of-usernames: false,
  header-connections-separator: "",
  header-connections-space-between-connections: 0.5cm,
  section-titles-type: "with_full_line",
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
  entries-short-second-row: false,
  entries-summary-space-left: 0cm,
  entries-summary-space-above: 0.12cm,
  entries-highlights-bullet: "•",
  entries-highlights-nested-bullet: "•",
  entries-highlights-space-left: 0cm,
  entries-highlights-space-above: 0.12cm,
  entries-highlights-space-between-items: 0.12cm,
  entries-highlights-space-between-bullet-and-text: 0.5em,
  date: datetime(
    year: 2026,
    month: 2,
    day: 16,
  ),
)

= علی احمدی

#headline([مهندس نرم‌افزار])

#connections(
  [#connection-with-icon("location-dot")[تهران، ایران]],
  [#link("mailto:ali@example.com", icon: false, if-underline: false, if-color: false)[#connection-with-icon("envelope")[ali\@example.com]]],
  [#link("https://github.com/aliahmadi", icon: false, if-underline: false, if-color: false)[#connection-with-icon("github")[aliahmadi]]],
  [#link("https://linkedin.com/in/aliahmadi", icon: false, if-underline: false, if-color: false)[#connection-with-icon("linkedin")[aliahmadi]]],
)

== تحصیلات

#education-entry(
  [
    #strong[دانشگاه صنعتی شریف]، مهندسی کامپیوتر

    - معدل: ۱۸.۵ از ۲۰

    - رتبه اول دانشکده مهندسی کامپیوتر

  ],
  [
    تهران، ایران

    مهر ۱۳۹۴ – شهریور ۱۳۹۸

  ],
  degree-column: [
    #strong[کارشناسی]
  ],
)

#education-entry(
  [
    #strong[دانشگاه تهران]، مهندسی نرم‌افزار

    - پایان‌نامه: بهینه‌سازی سیستم‌های توزیع‌شده با یادگیری ماشین

  ],
  [
    تهران، ایران

    مهر ۱۳۹۸ – شهریور ۱۴۰۰

  ],
  degree-column: [
    #strong[کارشناسی ارشد]
  ],
)

== سوابق کاری

#regular-entry(
  [
    #strong[شرکت فناوری اطلاعات]، مهندس ارشد نرم‌افزار

    - طراحی و پیاده‌سازی معماری میکروسرویس برای سیستم پرداخت آنلاین

    - مدیریت تیم ۸ نفره توسعه‌دهندگان

    - بهبود ۴۰ درصدی عملکرد سیستم با بهینه‌سازی پایگاه داده

  ],
  [
    تهران، ایران

    مهر ۱۴۰۰ – اکنون

  ],
)

#regular-entry(
  [
    #strong[استارتاپ هوش مصنوعی]، توسعه‌دهنده بک‌اند

    - پیاده‌سازی API‌های RESTful با Python و FastAPI

    - طراحی سیستم صف پیام با RabbitMQ برای پردازش ناهمزمان

  ],
  [
    تهران، ایران

    مهر ۱۳۹۸ – شهریور ۱۴۰۰

  ],
)

== پروژه‌ها

#regular-entry(
  [
    #strong[#link("https://github.com/")[سامانه مدیریت محتوا]]

    #summary[سیستم مدیریت محتوای متن‌باز با قابلیت چندزبانه]

    - پشتیبانی کامل از زبان‌های راست‌به‌چپ

    - بیش از ۲۰۰۰ ستاره در گیت‌هاب

  ],
  [
    فروردین ۱۴۰۲ – اکنون

  ],
)

== مهارت‌ها

#strong[زبان‌های برنامه‌نویسی:] Python، JavaScript، TypeScript، Go، Rust

#strong[فریم‌ورک‌ها:] FastAPI، Django، React، Next.js

#strong[ابزارها:] Docker، Kubernetes، PostgreSQL، Redis، Git
