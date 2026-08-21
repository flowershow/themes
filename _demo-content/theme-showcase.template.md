---
title: "Flowershow — {{name}} theme"
description: "{{description}}"
layout: plain
showToc: false
showEditLink: false
showComments: false
---

<div class="{{wrapperClass}} theme-showcase" data-theme-showcase="{{slug}}" data-theme-status="{{status}}">
  <main>
    <section class="ts-hero">
      <div class="ts-wrap ts-hero-grid">
        <div class="ts-hero-copy">
          <p class="ts-eyebrow"><span>{{status}}</span> Flowershow theme · {{name}}</p>
          <h1>{{headline}}</h1>
          <p class="ts-lede">{{description}}</p>
          <p class="ts-intro">Flowershow turns your Markdown into a live, hosted website—without a build pipeline or CMS to maintain. Keep writing in plain files while Flowershow handles the publishing.</p>
          <div class="ts-actions">
            <a class="ts-button ts-button-primary" href="/docs/kitchen-sink">Explore the kitchen sink <span aria-hidden="true">→</span></a>
            <a class="ts-button ts-button-secondary" href="https://flowershow.app/publish">Publish with Flowershow <span aria-hidden="true">→</span></a>
          </div>
        </div>
        <div class="ts-hero-art" aria-hidden="true">
          <div class="ts-orbit ts-orbit-wide"></div>
          <div class="ts-orbit ts-orbit-tight"></div>
          <div class="ts-node-mark">
            <span class="ts-node ts-node-center"></span>
            <span class="ts-node ts-node-nw"></span>
            <span class="ts-node ts-node-ne"></span>
            <span class="ts-node ts-node-sw"></span>
            <span class="ts-node ts-node-se"></span>
          </div>
          <span class="ts-art-label ts-art-label-top">MARKDOWN IN</span>
          <span class="ts-art-label ts-art-label-bottom">WEBSITE OUT</span>
        </div>
      </div>
    </section>

    <section class="ts-section ts-publish">
      <div class="ts-wrap">
        <p class="ts-eyebrow">One folder, many forms</p>
        <h2>Publish the site your content needs</h2>
        <p class="ts-section-intro">Use the same Markdown-first workflow for structured documentation, regular publishing, connected knowledge, or a growing collection of notes.</p>
        <div class="ts-card-grid ts-use-grid">
          <article class="ts-card"><span class="ts-card-index">01</span><h3>Documentation</h3><p>Clear navigation, readable code, tables, callouts, and long technical pages.</p></article>
          <article class="ts-card"><span class="ts-card-index">02</span><h3>Blogs</h3><p>Thoughtful article lists, metadata, images, and focused long-form reading.</p></article>
          <article class="ts-card"><span class="ts-card-index">03</span><h3>Knowledge bases</h3><p>Linked pages and durable structure for material that keeps evolving.</p></article>
          <article class="ts-card"><span class="ts-card-index">04</span><h3>Digital gardens</h3><p>Notes, ideas, and references that stay open to revision and discovery.</p></article>
        </div>
      </div>
    </section>

    <section class="ts-section ts-benefits">
      <div class="ts-wrap">
        <p class="ts-eyebrow">The Flowershow way</p>
        <h2>Your content stays simple</h2>
        <div class="ts-benefit-list">
          <article><span>MD</span><div><h3>Markdown-native</h3><p>Write in a format that is portable, readable, and easy to version.</p></div></article>
          <article><span>URL</span><div><h3>Hosted publishing</h3><p>Move from files to a shareable website without maintaining deployment machinery.</p></div></article>
          <article><span>OWN</span><div><h3>Your files remain yours</h3><p>Keep a durable source of truth in plain text instead of a closed content silo.</p></div></article>
          <article><span>CSS</span><div><h3>A visual system you can shape</h3><p>Start with a theme and refine ordinary CSS when the site needs its own voice.</p></div></article>
        </div>
      </div>
    </section>

    <section class="ts-section ts-process">
      <div class="ts-wrap">
        <p class="ts-eyebrow">A short path to published</p>
        <h2>Write. Publish. Keep moving.</h2>
        <ol class="ts-steps">
          <li><span>01</span><div><h3>Bring your Markdown</h3><p>Start with a folder, a repository, or the notes you already maintain.</p></div></li>
          <li><span>02</span><div><h3>Publish with Flowershow</h3><p>Use the web, command line, GitHub, or Obsidian workflow that fits your work.</p></div></li>
          <li><span>03</span><div><h3>Share a real website</h3><p>Get a hosted URL, then keep improving the same source files over time.</p></div></li>
        </ol>
      </div>
    </section>

    <section class="ts-section ts-theme-detail">
      <div class="ts-wrap ts-theme-grid">
        <div>
          <p class="ts-eyebrow">About this theme</p>
          <h2>{{name}}</h2>
          <p class="ts-theme-description">{{description}}</p>
          <p>This preview uses IBM Plex Mono, disciplined spacing, crisp rules, and first-class light and dark modes. It is designed to keep technical material dense without making it difficult to scan.</p>
          <div class="ts-text-links"><a href="/blog">Read the demo blog →</a><a href="/docs/kitchen-sink">Inspect every component →</a></div>
        </div>
        <div class="ts-theme-sample" aria-label="A small Monospace theme specimen">
          <p><span>THEME</span> {{name}}</p>
          <p><span>STATUS</span> {{status}}</p>
          <p><span>MODES</span> LIGHT / DARK</p>
          <pre><code># Publish clearly

Your words stay yours.
Your website stays useful.</code></pre>
        </div>
      </div>
    </section>

    <section class="ts-section ts-final-cta">
      <div class="ts-wrap ts-cta-grid">
        <div><p class="ts-eyebrow">Content in. Website out.</p><h2>Give your Markdown a place to live.</h2></div>
        <div class="ts-actions"><a class="ts-button ts-button-primary" href="https://flowershow.app/publish">Publish with Flowershow <span aria-hidden="true">→</span></a><a class="ts-button ts-button-secondary" href="{{sourceUrl}}">View theme source <span aria-hidden="true">→</span></a></div>
      </div>
      <div class="ts-wrap ts-preview-note"><span>{{name}} is currently a {{status}} theme.</span><a href="https://flowershow-themes-preview-rufuspollock.flowershow.me">Browse Flowershow themes</a></div>
    </section>
  </main>
</div>
