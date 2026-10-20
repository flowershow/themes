#!/usr/bin/env node
// Measure a website's design language from computed styles, in light and dark.
//
//     node scripts/measure-site.mjs <url> [<url> ...] [--out FILE] [--width N] [--shots DIR]
//
// --shots DIR also saves full-page reference screenshots of every URL in
// each mode the site has, at desktop (--width) and mobile (390px), named
// <page-slug>--<desktop|mobile>-<light|dark>.png like contact-sheet.py's.
//
// Phase A of the theme-from-website workflow (docs/plans/
// 2026-10-17-theme-from-website-handoff.md). Ranking colour literals by
// frequency across a site's stylesheets lets its dark palette win the light
// roles, and declared fonts aren't always the ones that render. This script
// is the source of truth for the values a theme copies. It loads each page with prefers-color-scheme emulated as
// light and then dark and reads getComputedStyle, so every value is what
// a visitor sees.
//
// Pass the homepage first, then an article or docs page: roles are taken
// from the first page where the element exists (an <h1> in an article
// beats a hero banner only if the article comes first), and the colour
// histograms are summed over all pages.
//
// Output (stdout, or --out FILE) is design-tokens.json:
//   source, pages, measuredAt, width
//   dark        "media"      the site follows prefers-color-scheme
//               "toggle:<x>" the site has a dark mode behind <x> (a class or
//                            attribute on <html>), applied by hand
//               "dark-only"  the site is dark in both schemes
//               "none"       no dark mode found; the theme derives one
//   modes.light / modes.dark  each {roles, type, shape, candidates} or null
//     roles     background, surface, foreground, muted, border, link,
//               linkHover (null: not measured), accent, codeBg, codeFg,
//               preBg, navBg, navFg, footerBg, buttonBg, buttonFg. Each
//               {value: "#rrggbb" (or #rrggbbaa), from: how it was found}
//               or null. Text roles prefer elements sitting straight on
//               the page background, so a paragraph in a dark feature
//               card doesn't become the foreground. Fixed cookie/consent
//               banners are hidden first.
//     type      body, h1, h2, h3, code, nav: family (the computed stack),
//               rendered (the font actually drawn, from CDP), size, weight,
//               lineHeight, letterSpacing, textTransform
//     shape     radius (button, input, card, code, image), borderWidth,
//               contentWidth (the main column's width)
//     candidates  the histograms behind roles: text, pageText (text on the
//               page background only), background, border, chromatic;
//               each [{color, share}] so a wrong pick is easy to overrule
//   fonts       one entry per rendered family (style words like "Light"
//               stripped; the raw face names are in faces): roles it
//               serves, weights seen, webfont (loaded via @font-face, as
//               opposed to a system font), googleFonts (true = in the
//               Google Fonts catalogue, so a theme can @import it; false =
//               find an open stand-in or check the licence; null = the
//               lookup failed)
//
// Uses the Playwright bundled with gstack (PLAYWRIGHT_DIR overrides where
// its node_modules is). This doesn't touch the gstack browse daemon, so it
// can run alongside hook-coverage.py and friends.

import { createRequire } from "node:module";
import { mkdirSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const PLAYWRIGHT_DIR =
  process.env.PLAYWRIGHT_DIR || join(homedir(), ".claude/skills/gstack/node_modules/");

// Classes/attributes sites put on <html> (or <body>) for a manual dark mode.
const TOGGLES = [
  ["class", "dark"],
  ["data-theme", "dark"],
  ["data-mode", "dark"],
  ["data-color-scheme", "dark"],
  ["data-bs-theme", "dark"],
  ["class", "theme-dark"],
  ["class", "dark-mode"],
];

function usage(msg) {
  if (msg) console.error(msg);
  console.error("usage: node scripts/measure-site.mjs <url> [<url> ...] [--out FILE] [--width N] [--shots DIR]");
  process.exit(2);
}

function parseArgs(argv) {
  const opts = { urls: [], out: null, width: 1280, shots: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--out") opts.out = argv[++i] ?? usage("--out needs a file");
    else if (a === "--shots") opts.shots = argv[++i] ?? usage("--shots needs a directory");
    else if (a === "--width") opts.width = Number(argv[++i]) || usage("--width needs a number");
    else if (a === "-h" || a === "--help") usage();
    else if (a.startsWith("--")) usage(`unknown option ${a}`);
    else opts.urls.push(a);
  }
  if (!opts.urls.length) usage("give at least one URL");
  return opts;
}

// Runs in the page. Tags the probe elements with data-measure-role (so the
// CDP font lookup can find them) and returns raw computed values plus the
// colour histograms. Colours come back as the browser's rgb()/rgba() text;
// normalising happens in Node.
function probePage() {
  const visible = (el) => {
    if (!el) return false;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return false;
    const s = getComputedStyle(el);
    return s.visibility !== "hidden" && s.display !== "none" && Number(s.opacity) > 0.05;
  };
  const first = (root, sel, test = () => true) =>
    [...root.querySelectorAll(sel)].find((el) => visible(el) && test(el)) || null;
  const transparent = (c) => !c || c === "transparent" || /rgba\(.*,\s*0\)$/.test(c);
  // the colour actually behind an element: walk up to the first opaque-ish bg
  const effectiveBg = (el) => {
    for (let e = el; e; e = e.parentElement) {
      const c = getComputedStyle(e).backgroundColor;
      if (!transparent(c)) return c;
    }
    return getComputedStyle(document.documentElement).backgroundColor;
  };

  // cookie/consent overlays sit on top of everything and skew every pick
  for (const el of document.querySelectorAll("body *")) {
    const s = getComputedStyle(el);
    if ((s.position === "fixed" || s.position === "sticky") &&
        /cookie|consent|gdpr|privacy-banner/i.test(`${el.id} ${el.className}`))
      el.style.setProperty("display", "none", "important");
  }

  const root =
    first(document, "main, [role=main], article, #content, .content, #main") || document.body;
  const pageBg = effectiveBg(document.body);
  // text sitting straight on the page, not in a coloured card or banner
  const onPage = (el) => effectiveBg(el) === pageBg;
  const prose = (el) => el.textContent.trim().length > 40;
  const pick = {
    body:
      first(root, "p", (el) => prose(el) && onPage(el)) ||
      first(root, "p", prose) ||
      first(root, "p"),
    h1: first(root, "h1") || first(document, "h1"),
    h2: first(root, "h2") || first(document, "h2"),
    h3: first(root, "h3") || first(document, "h3"),
    link:
      first(root, "p a[href], li a[href]", (el) => el.textContent.trim().length > 1 && onPage(el)) ||
      first(root, "p a[href], li a[href]", (el) => el.textContent.trim().length > 1) ||
      first(root, "a[href]"),
    nav: first(document, "header, nav, [role=banner], [role=navigation]"),
    navLink: first(document, "header a[href], nav a[href]"),
    footer: first(document, "footer, [role=contentinfo]"),
    button: first(
      document,
      "button, [role=button], input[type=submit], a[class*=button i], a[class*=btn i], a[class*=cta i]",
      (el) => !transparent(getComputedStyle(el).backgroundColor),
    ),
    input: first(document, "input[type=text], input[type=search], input[type=email], input:not([type])"),
    code: first(document, ":not(pre) > code"),
    pre: first(document, "pre"),
    blockquote: first(document, "blockquote"),
    hr: first(document, "hr"),
    card: first(
      document,
      "[class*=card i], article",
      (el) => {
        const s = getComputedStyle(el);
        return parseFloat(s.borderTopLeftRadius) > 0 || s.boxShadow !== "none" || parseFloat(s.borderTopWidth) > 0;
      },
    ),
    image: first(root, "img", (el) => el.getBoundingClientRect().width > 120),
  };

  const out = { roles: {}, histograms: { text: {}, pageText: {}, background: {}, border: {} } };
  for (const [role, el] of Object.entries(pick)) {
    if (!el) {
      out.roles[role] = null;
      continue;
    }
    el.setAttribute("data-measure-role", role);
    const s = getComputedStyle(el);
    out.roles[role] = {
      tag: el.tagName.toLowerCase() + (el.className && typeof el.className === "string"
        ? "." + el.className.trim().split(/\s+/).slice(0, 2).join(".")
        : ""),
      color: s.color,
      background: s.backgroundColor,
      effectiveBg: effectiveBg(el),
      borderColor: s.borderTopColor,
      borderWidth: s.borderTopWidth,
      borderLeftColor: s.borderLeftColor,
      borderLeftWidth: s.borderLeftWidth,
      radius: s.borderTopLeftRadius,
      shadow: s.boxShadow,
      fontFamily: s.fontFamily,
      fontSize: s.fontSize,
      fontWeight: s.fontWeight,
      lineHeight: s.lineHeight,
      letterSpacing: s.letterSpacing,
      textTransform: s.textTransform,
      textDecoration: s.textDecorationLine,
      width: Math.round(el.getBoundingClientRect().width),
    };
  }
  out.roles.page = {
    background: effectiveBg(document.body),
    color: getComputedStyle(document.body).color,
  };
  out.contentWidth = Math.round(
    (pick.body?.parentElement || root).getBoundingClientRect().width,
  );

  // Histograms: text colour weighted by the element's own text, background
  // by painted area, border by length. Capped so huge pages stay quick.
  const add = (h, c, w) => {
    if (!transparent(c) && w > 0) h[c] = (h[c] || 0) + w;
  };
  const all = [...document.body.querySelectorAll("*")].slice(0, 6000);
  for (const el of all) {
    if (!visible(el)) continue;
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    let own = 0;
    for (const n of el.childNodes) if (n.nodeType === 3) own += n.textContent.trim().length;
    add(out.histograms.text, s.color, own);
    if (own && onPage(el)) add(out.histograms.pageText, s.color, own);
    add(out.histograms.background, s.backgroundColor, Math.min(r.width * r.height, 2e6));
    // inline borders are mostly link underlines drawn as border-bottom
    if (s.display === "inline") continue;
    if (parseFloat(s.borderTopWidth) > 0) add(out.histograms.border, s.borderTopColor, r.width);
    if (parseFloat(s.borderBottomWidth) > 0) add(out.histograms.border, s.borderBottomColor, r.width);
    if (parseFloat(s.borderLeftWidth) > 0) add(out.histograms.border, s.borderLeftColor, r.height);
  }
  out.webfonts = [...document.fonts]
    .filter((f) => f.status === "loaded")
    .map((f) => f.family.replace(/^["']|["']$/g, "").toLowerCase());
  return out;
}

// --- colour helpers (Node side) ---------------------------------------------

function parseColor(text) {
  if (!text) return null;
  const h = text.match(/^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})?$/i);
  if (h) {
    const [r, g, b] = [h[1], h[2], h[3]].map((v) => parseInt(v, 16));
    return { r, g, b, a: h[4] ? parseInt(h[4], 16) / 255 : 1 };
  }
  // modern Chromium may report color(srgb r g b / a) for some inputs
  let m = text.match(/rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+%?))?\s*\)/);
  let r, g, b, a = 1;
  if (m) {
    [r, g, b] = [m[1], m[2], m[3]].map(Number);
    if (m[4] !== undefined) a = m[4].endsWith("%") ? parseFloat(m[4]) / 100 : Number(m[4]);
  } else if ((m = text.match(/color\(srgb\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)(?:\s*\/\s*([\d.]+))?\)/))) {
    [r, g, b] = [m[1], m[2], m[3]].map((v) => Number(v) * 255);
    if (m[4] !== undefined) a = Number(m[4]);
  } else return null;
  return { r: Math.round(r), g: Math.round(g), b: Math.round(b), a };
}

function hex(text) {
  const c = typeof text === "string" ? parseColor(text) : text;
  if (!c) return null;
  const h = (n) => n.toString(16).padStart(2, "0");
  const base = `#${h(c.r)}${h(c.g)}${h(c.b)}`;
  return c.a < 0.999 ? base + h(Math.round(c.a * 255)) : base;
}

function luminance(c) {
  const ch = (v) => {
    v /= 255;
    return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * ch(c.r) + 0.7152 * ch(c.g) + 0.0722 * ch(c.b);
}

function saturation(c) {
  const max = Math.max(c.r, c.g, c.b) / 255;
  const min = Math.min(c.r, c.g, c.b) / 255;
  const l = (max + min) / 2;
  if (max === min) return 0;
  return (max - min) / (1 - Math.abs(2 * l - 1));
}

const chromatic = (c) => c && c.a > 0.5 && saturation(c) > 0.25 && luminance(c) > 0.02 && luminance(c) < 0.8;
const sameColor = (a, b) => a && b && Math.abs(a.r - b.r) + Math.abs(a.g - b.g) + Math.abs(a.b - b.b) <= 6;

// merge raw-text keyed histograms into hex-keyed shares, largest first
function ranked(histos) {
  const sum = {};
  for (const h of histos)
    for (const [text, w] of Object.entries(h)) {
      const k = hex(text);
      if (k) sum[k] = (sum[k] || 0) + w;
    }
  const total = Object.values(sum).reduce((a, b) => a + b, 0) || 1;
  return Object.entries(sum)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 12)
    .map(([color, w]) => ({ color, share: Math.round((w / total) * 1000) / 1000 }));
}

// --- turning probes into a mode ---------------------------------------------

function role(value, from) {
  const h = hex(value);
  return h ? { value: h, from } : null;
}

function firstRole(probes, name) {
  for (const p of probes) if (p.roles[name]) return { ...p.roles[name], page: p.url };
  return null;
}

function typeOf(el) {
  if (!el) return null;
  return {
    from: `${el.tag} on ${el.page}`,
    family: el.fontFamily,
    rendered: el.rendered ?? null,
    size: el.fontSize,
    weight: el.fontWeight,
    lineHeight: el.lineHeight,
    letterSpacing: el.letterSpacing,
    textTransform: el.textTransform,
  };
}

function buildMode(probes) {
  const page = probes[0].roles.page;
  const bg = parseColor(page.background);
  const fg = parseColor(page.color);
  const text = ranked(probes.map((p) => p.histograms.text));
  const pageText = ranked(probes.map((p) => p.histograms.pageText));
  const background = ranked(probes.map((p) => p.histograms.background));
  const border = ranked(probes.map((p) => p.histograms.border));
  const chroma = ranked(
    probes.flatMap((p) => [p.histograms.text, p.histograms.background]).map((h) =>
      Object.fromEntries(Object.entries(h).filter(([c]) => chromatic(parseColor(c)))),
    ),
  );

  const el = Object.fromEntries(
    ["body", "h1", "h2", "h3", "link", "nav", "navLink", "footer", "button", "input", "code", "pre",
      "blockquote", "hr", "card", "image"].map((k) => [k, firstRole(probes, k)]),
  );

  // foreground: of the neutral text colours straight on the page (the probed
  // paragraph may sit in a card) with a real share, the one with the most
  // contrast; sites often set more words in a muted grey than in the body
  // colour. muted: the commonest neutral one that sits closer to the page.
  const contrast = (c) => Math.abs(luminance(c) - luminance(bg));
  const neutral = pageText.filter(({ color }) => !chromatic(parseColor(color)));
  const fgPick = neutral
    .filter(({ share }) => share >= 0.1)
    .sort((a, b) => contrast(parseColor(b.color)) - contrast(parseColor(a.color)))[0];
  const fgBody = (fgPick && parseColor(fgPick.color)) || parseColor(el.body?.color) || fg;
  const muted = neutral.find(({ color }) => {
    const c = parseColor(color);
    return !sameColor(c, fgBody) && contrast(c) < contrast(fgBody);
  });
  // surface: the most common background other than the page's that stays
  // close to it (a card or sidebar tint, not a dark footer band)
  const surface = background.find(({ color }) => {
    const c = parseColor(color);
    return c.a > 0.5 && !sameColor(c, bg) && Math.abs(luminance(c) - luminance(bg)) < 0.12;
  });
  const linkColor = parseColor(el.link?.color);
  const buttonBg = parseColor(el.button?.background);
  let accent = null;
  if (chromatic(buttonBg)) accent = role(el.button.background, `button background (${el.button.tag})`);
  else if (chromatic(linkColor)) accent = role(el.link.color, `link colour (${el.link.tag})`);
  else if (chroma[0]) accent = { value: chroma[0].color, from: "most common chromatic colour" };

  const radius = (e) => (e ? e.radius : null);
  return {
    roles: {
      background: role(page.background, "body's effective background"),
      surface: surface ? { value: surface.color, from: "most common near-page background" } : null,
      foreground: fgPick
        ? { value: fgPick.color, from: "strongest common neutral text colour on the page background" }
        : role(el.body?.color || page.color, el.body ? `paragraph text (${el.body.tag})` : "body colour"),
      muted: muted ? { value: muted.color, from: "most common quieter text colour" } : null,
      border: border[0] ? { value: border[0].color, from: "most common border colour" } : null,
      link: el.link ? role(el.link.color, `link in content (${el.link.tag})`) : null,
      linkHover: null,
      accent,
      codeBg: el.code ? role(el.code.effectiveBg, `inline code (${el.code.tag})`) : null,
      codeFg: el.code ? role(el.code.color, `inline code (${el.code.tag})`) : null,
      preBg: el.pre ? role(el.pre.effectiveBg, `code block (${el.pre.tag})`) : null,
      navBg: el.nav ? role(el.nav.effectiveBg, `header/nav (${el.nav.tag})`) : null,
      navFg: el.navLink ? role(el.navLink.color, `nav link (${el.navLink.tag})`) : null,
      footerBg: el.footer ? role(el.footer.effectiveBg, `footer (${el.footer.tag})`) : null,
      buttonBg: el.button ? role(el.button.background, `button (${el.button.tag})`) : null,
      buttonFg: el.button ? role(el.button.color, `button (${el.button.tag})`) : null,
    },
    type: {
      body: typeOf(el.body),
      h1: typeOf(el.h1),
      h2: typeOf(el.h2),
      h3: typeOf(el.h3),
      code: typeOf(el.code || el.pre),
      nav: typeOf(el.navLink),
    },
    shape: {
      radius: {
        button: radius(el.button),
        input: radius(el.input),
        card: radius(el.card),
        code: radius(el.code),
        image: radius(el.image),
      },
      borderWidth: el.hr?.borderWidth ?? el.card?.borderWidth ?? null,
      contentWidth: probes[0].contentWidth,
      blockquote: el.blockquote
        ? { borderLeft: `${el.blockquote.borderLeftWidth} ${hex(el.blockquote.borderLeftColor)}`, color: hex(el.blockquote.color) }
        : null,
      cardShadow: el.card && el.card.shadow !== "none" ? el.card.shadow : null,
    },
    candidates: { text, pageText, background, border, chromatic: chroma },
  };
}

// --- browser side ------------------------------------------------------------

async function renderedFonts(page) {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("DOM.enable");
  await cdp.send("CSS.enable");
  const { root } = await cdp.send("DOM.getDocument", { depth: 0 });
  const { nodeIds } = await cdp.send("DOM.querySelectorAll", { nodeId: root.nodeId, selector: "[data-measure-role]" });
  const out = {};
  for (const nodeId of nodeIds) {
    const { attributes } = await cdp.send("DOM.getAttributes", { nodeId });
    const r = attributes[attributes.indexOf("data-measure-role") + 1];
    try {
      const { fonts } = await cdp.send("CSS.getPlatformFontsForNode", { nodeId });
      fonts.sort((a, b) => b.glyphCount - a.glyphCount);
      out[r] = fonts[0]?.familyName ?? null;
    } catch {
      // nodes with no text of their own (an <hr>) have no platform fonts
    }
  }
  await cdp.detach();
  return out;
}

// Opens url in a new page with the colour scheme emulated and, if given, a
// dark-mode toggle applied. The caller closes the page.
async function openPage(browser, url, scheme, width, toggle) {
  const page = await browser.newPage({ colorScheme: scheme, viewport: { width, height: 900 } });
  try {
    const resp = await page.goto(url, { waitUntil: "networkidle", timeout: 45000 }).catch(async (e) => {
      // some sites never go network-idle (analytics beacons); settle for load
      if (!/Timeout/.test(String(e))) throw e;
      return null;
    });
    if (resp && resp.status() >= 400) throw new Error(`${url} answered HTTP ${resp.status()}`);
    if (toggle) {
      await page.evaluate(([attr, value]) => {
        for (const el of [document.documentElement, document.body]) {
          if (attr === "class") el.classList.add(value);
          else el.setAttribute(attr, value);
        }
      }, toggle);
    }
    await page.evaluate(() => document.fonts.ready);
    return page;
  } catch (e) {
    await page.close();
    throw e;
  }
}

async function probe(browser, url, scheme, width, toggle) {
  const page = await openPage(browser, url, scheme, width, toggle);
  try {
    const result = await page.evaluate(probePage);
    const fonts = await renderedFonts(page);
    for (const [r, family] of Object.entries(fonts)) if (result.roles[r]) result.roles[r].rendered = family;
    result.url = url;
    return result;
  } finally {
    await page.close();
  }
}

function pageSlug(url) {
  const path = new URL(url).pathname.replace(/^\/+|\/+$/g, "");
  return path ? path.replace(/[^a-z0-9]+/gi, "-").toLowerCase() : "home";
}

// render: {light|dark: [scheme, toggle]} for the modes the site has.
async function screenshots(browser, urls, width, render, dir) {
  mkdirSync(dir, { recursive: true });
  const written = [];
  for (const url of urls) {
    for (const [viewport, w] of [["desktop", width], ["mobile", 390]]) {
      for (const [mode, [scheme, toggle]] of Object.entries(render)) {
        const page = await openPage(browser, url, scheme, w, toggle);
        try {
          const file = join(dir, `${pageSlug(url)}--${viewport}-${mode}.png`);
          await page.screenshot({ path: file, fullPage: true });
          written.push(file);
        } finally {
          await page.close();
        }
      }
    }
  }
  return written;
}

// The css2 API is no use for this: it answers 200 with a stand-in for
// families it doesn't host (Helvetica Neue, Georgia). The metadata list is
// the real catalogue.
async function googleFontFamilies() {
  try {
    const r = await fetch("https://fonts.google.com/metadata/fonts");
    const text = (await r.text()).replace(/^\)\]\}'\s*/, "");
    return new Set(JSON.parse(text).familyMetadataList.map((f) => f.family.toLowerCase()));
  } catch {
    return null;
  }
}

// CDP reports a face's full name for static fonts ("JetBrains Mono Light",
// "Die Grotesk C Medium"); the family is what's left without the style words
const STYLE_WORDS =
  /\s+(thin|hairline|extra ?light|ultra ?light|light|book|regular|normal|medium|semi ?bold|demi ?bold|bold|extra ?bold|ultra ?bold|black|heavy|italic|oblique)$/i;
function baseFamily(name) {
  let prev;
  do {
    prev = name;
    name = name.replace(STYLE_WORDS, "");
  } while (name !== prev);
  return name;
}

function weightsByFamily(modes) {
  const fams = {};
  for (const mode of Object.values(modes)) {
    if (!mode) continue;
    for (const [r, t] of Object.entries(mode.type)) {
      if (!t?.rendered) continue;
      const name = baseFamily(t.rendered);
      const f = (fams[name] ??= { family: name, faces: new Set(), roles: new Set(), weights: new Set() });
      f.faces.add(t.rendered);
      f.roles.add(r);
      f.weights.add(Number(t.weight));
    }
  }
  return Object.values(fams);
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  const require = createRequire(PLAYWRIGHT_DIR);
  let chromium;
  try {
    ({ chromium } = require("playwright"));
  } catch {
    console.error(`playwright not found under ${PLAYWRIGHT_DIR} (set PLAYWRIGHT_DIR)`);
    process.exit(2);
  }
  const browser = await chromium.launch();
  try {
    const light = [];
    const dark = [];
    for (const url of opts.urls) {
      light.push(await probe(browser, url, "light", opts.width, null));
      dark.push(await probe(browser, url, "dark", opts.width, null));
    }

    const bgOf = (p) => parseColor(p.roles.page.background);
    let darkMode = "none";
    let darkToggle = null;
    let darkProbes = null;
    let lightProbes = light;
    if (!sameColor(bgOf(light[0]), bgOf(dark[0]))) {
      darkMode = "media";
      darkProbes = dark;
    } else if (luminance(bgOf(light[0])) < 0.05) {
      // dark in both schemes: there is no light palette to copy
      darkMode = "dark-only";
      darkProbes = light;
      lightProbes = null;
    } else {
      for (const t of TOGGLES) {
        const p = await probe(browser, opts.urls[0], "light", opts.width, t);
        if (!sameColor(bgOf(p), bgOf(light[0]))) {
          darkToggle = t;
          darkMode = `toggle:${t[0] === "class" ? "." + t[1] : `[${t[0]}=${t[1]}]`}`;
          darkProbes = [p];
          for (const url of opts.urls.slice(1)) darkProbes.push(await probe(browser, url, "light", opts.width, t));
          break;
        }
      }
    }

    const modes = {
      light: lightProbes ? buildMode(lightProbes) : null,
      dark: darkProbes ? buildMode(darkProbes) : null,
    };
    const google = await googleFontFamilies();
    const faces = new Set([...light, ...dark].flatMap((p) => p.webfonts));
    const fonts = weightsByFamily(modes).map((f) => ({
      family: f.family,
      faces: [...f.faces].sort(),
      roles: [...f.roles].sort(),
      weights: [...f.weights].sort((a, b) => a - b),
      // CDP names the face from the font file, which can differ slightly
      // from the @font-face name ("Inter Variable" vs "Inter")
      webfont: [...faces].some((n) => {
        const fam = f.family.toLowerCase();
        return n.startsWith(fam) || fam.startsWith(n);
      }),
      googleFonts: google ? google.has(f.family.toLowerCase()) : null,
    }));

    const result = {
      source: opts.urls[0],
      pages: opts.urls,
      measuredAt: new Date().toISOString(),
      width: opts.width,
      dark: darkMode,
      modes,
      fonts,
    };
    if (opts.shots) {
      const render = {};
      if (lightProbes) render.light = ["light", null];
      if (darkMode === "media" || darkMode === "dark-only") render.dark = ["dark", null];
      else if (darkToggle) render.dark = ["light", darkToggle];
      const files = await screenshots(browser, opts.urls, opts.width, render, opts.shots);
      console.error(`saved ${files.length} reference shots to ${opts.shots}`);
    }
    const json = JSON.stringify(result, null, 2) + "\n";
    if (opts.out) {
      writeFileSync(opts.out, json);
      console.error(`wrote ${opts.out} (dark: ${darkMode}; fonts: ${fonts.map((f) => f.family).join(", ") || "none"})`);
    } else process.stdout.write(json);
  } finally {
    await browser.close();
  }
}

main().catch((e) => {
  console.error(e.stack || String(e));
  process.exit(1);
});
