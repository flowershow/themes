---
title: "Flowershow — {{yaml:name}} theme"
description: "{{yaml:description}}"
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
          <p>Flowershow turns Markdown files into a live website. Keep writing in plain text while Flowershow handles the hosted publishing.</p>
          <p class="ts-links"><a href="/docs/kitchen-sink">Explore the kitchen sink →</a><a href="https://flowershow.app/publish">Publish with Flowershow →</a></p>
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
    <div class="ts-wrap ts-document">
      <section class="ts-section">
        <h2>Sites you can publish</h2>
        <p>The same Markdown-first workflow works for a focused publication or a body of knowledge that grows for years.</p>
        <ul>
          <li><a href="/docs/kitchen-sink">Documentation</a> with navigation, code, tables, callouts, and long technical pages</li>
          <li><a href="/blog">Blogs</a> with article lists, metadata, images, and focused reading</li>
          <li>Knowledge bases with linked pages and durable structure</li>
          <li>Digital gardens made from notes, ideas, and references</li>
        </ul>
      </section>
      <section class="ts-section">
        <h2>Why Flowershow</h2>
        <p>Your source stays ordinary and portable. Flowershow supplies the website without putting a CMS or custom build pipeline between you and your writing.</p>
        <ul>
          <li>Write and version plain Markdown files</li>
          <li>Publish a shareable hosted website</li>
          <li>Keep your files as the durable source of truth</li>
          <li>Choose a theme and refine it with ordinary CSS</li>
        </ul>
      </section>
      <section class="ts-section">
        <h2>From files to website</h2>
        <ol>
          <li>Bring a folder, repository, or the notes you already maintain.</li>
          <li>Publish through the web, command line, GitHub, or Obsidian workflow.</li>
          <li>Share the hosted URL and keep improving the same source files.</li>
        </ol>
      </section>
      <section class="ts-section">
        <h2>About {{name}}</h2>
        <p>{{description}}</p>
        <p>This preview keeps technical material compact and easy to scan. Use the <a href="/docs/kitchen-sink">component page</a> and <a href="/blog/first-post">demo post</a> to see how the same theme handles denser content.</p>
        <pre aria-label="A small {{name}} theme specimen"><code># Publish clearly
Your words stay yours.
Your website stays useful.</code></pre>
      </section>
      <section class="ts-section ts-closing">
        <h2>Start publishing</h2>
        <p>Try Flowershow with your own Markdown, inspect this theme's source, or compare the other available themes.</p>
        <p class="ts-links"><a href="https://flowershow.app/publish">Publish with Flowershow →</a><a href="{{sourceUrl}}">View theme source →</a><a href="https://flowershow-themes-preview-rufuspollock.flowershow.me">Browse themes →</a></p>
        <p class="ts-status">{{name}} is currently a {{status}} theme.</p>
      </section>
    </div>
  </main>
</div>
