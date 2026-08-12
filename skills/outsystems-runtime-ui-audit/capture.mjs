// Capture a runtime URL for the UI Quality Assessment audit.
//
// Produces static screenshots (desktop + mobile), a shallow crawl of in-app
// surfaces, interaction-state captures (focus ring, hover before/after), a
// mechanical probe (tap-target sizes, motion/transition signals, reduced-motion
// support, focus outlines), and a session recording — enough to score the
// static, layout, content, accessibility, behaviour, and interaction criteria.
//
// Usage (run from a dir where `playwright` is installed — see SKILL.md):
//   node capture.mjs <url> <out-dir> [--max-screens=4] [--viewports=desktop,mobile] [--no-crawl]
//
// Uses the system Google Chrome (channel: 'chrome') — no Chromium download.
// Assumes the URL is publicly reachable (no auth). Writes into <out-dir>:
//   desktop.png, mobile.png            landing, full-page, per viewport
//   screen-NN-<slug>.png               crawled in-app surfaces (desktop)
//   focus.png                          first focused element (C6 focus ring)
//   hover-before.png / hover-after.png primary control resting vs hover (C12)
//   session.webm                       desktop session recording (C11 — human review)
//   probe.json                         mechanical signals (see keys below)
// and prints one JSON line per capture + a final {probe:...} summary line.

import { chromium } from 'playwright';
import { mkdirSync, writeFileSync, renameSync, readdirSync } from 'node:fs';

const [, , url, outDirRaw = '.', ...rest] = process.argv;
if (!url) {
  console.error('usage: node capture.mjs <url> <out-dir> [--max-screens=N] [--viewports=desktop,mobile] [--no-crawl]');
  process.exit(2);
}
const outDir = outDirRaw.replace(/\/$/, '');
const opt = (k, d) => {
  const a = rest.find((x) => x.startsWith(`--${k}=`));
  return a ? a.split('=')[1] : d;
};
const wantedViewports = opt('viewports', 'desktop,mobile').split(',').map((s) => s.trim());
const maxScreens = parseInt(opt('max-screens', '4'), 10);
const noCrawl = rest.includes('--no-crawl');

const VIEWPORTS = {
  desktop: { width: 1440, height: 900, deviceScaleFactor: 1 },
  mobile: { width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
};

mkdirSync(outDir, { recursive: true });

// Selector for "interactive" elements used for tap-target sizing + inventory.
const INTERACTIVE =
  'a[href], button, input:not([type=hidden]), select, textarea, [role=button], [role=link], [role=tab], [role=checkbox], [role=switch], [role=menuitem], [tabindex]:not([tabindex="-1"])';

// A rendered app has interactive elements or real text. An SPA whose entry URL
// client-side-redirects to its default screen can still be an empty shell when
// `networkidle` + a fixed wait expires — measured 2026-08-11, where the app's
// documented base URL produced a blank white capture and a probe of the
// pre-render shell. Polling for evidence of render is cheap and removes the
// race rather than lengthening the guess.
const RENDER_TIMEOUT_MS = 15000;

async function waitForRender(page, timeout = RENDER_TIMEOUT_MS) {
  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    const rendered = await page
      .evaluate(
        (sel) =>
          document.querySelectorAll(sel).length > 0 ||
          (document.body?.innerText || '').trim().length > 40,
        INTERACTIVE,
      )
      .catch(() => false);
    if (rendered) return true;
    await page.waitForTimeout(250);
  }
  return false;
}

async function loadPage(page, target) {
  try {
    await page.goto(target, { waitUntil: 'networkidle', timeout: 30000 });
  } catch {
    await page.goto(target, { waitUntil: 'load', timeout: 30000 });
  }
  await page.waitForTimeout(2500);
  return waitForRender(page);
}

// The guard for when the wait above still isn't enough.
//
// A blank capture does not read as an error — it reads as a clean app, and it
// fails OPTIMISTICALLY: zero tap targets, null focus, and `osDefaults.present:
// false` scores the identity criterion BETTER than the truth. So a probe from
// an unrendered page must never be written; a missing report is honest, an
// optimistic one is not.
// The guard must agree with waitForRender, which accepts EITHER interactive
// elements OR real visible text. Failing on zero interactive alone rejected
// legitimately text-only screens — an informational or read-only page would
// exit 3 with "nothing rendered" while its content sat in the screenshot.
// So: blank means BOTH signals absent, which is what "unrendered" actually is.
const BLANK_TEXT_THRESHOLD = 40; // same threshold waitForRender polls on

function blankCapture(probe) {
  const t = probe.tapTargets;
  if (!t || t.error) return null; // the probe itself failed; not this guard's call
  if (t.total > 0) return null;
  const textLength = typeof t.textLength === 'number' ? t.textLength : 0;
  if (textLength > BLANK_TEXT_THRESHOLD) return null; // text-only, but rendered
  return {
    reason: 'landing capture reported zero interactive elements and no meaningful text',
    tapTargets: t.total,
    textLength,
    title: probe.viewports?.desktop?.title ?? null,
    url: probe.viewports?.desktop?.url ?? probe.url,
    likelyCause:
      'the entry URL rendered nothing within the readiness window — commonly a '
      + 'client-side redirect to a default screen that outruns it',
    remedy:
      're-run against an explicit screen URL rather than the app base path, and '
      + 'confirm the screen renders in a browser first',
  };
}

// Platform-default design tokens. Their presence is the rubric's highest-signal
// mechanical tell for C1 / C14 / C16 — measured here rather than eyeballed.
const OS_DEFAULT_TOKENS = [
  { token: '#1068eb', value: 'rgb(16, 104, 235)', note: 'OutSystems default primary' },
  { token: '#f3f6f8', value: 'rgb(243, 246, 248)', note: 'OutSystems default body background' },
];
// Runaway guard for the identity scan, not a sampling cap — the probe reports
// `truncated: true` if it ever bites, because a silently missed default token
// reads as an authored palette.
const IDENTITY_MAX_SCAN = 20000;

const browser = await chromium.launch({ channel: 'chrome' });
const probe = { url, viewports: {}, tapTargets: null, motion: null, identity: null, focus: null, hover: null, crawled: [] };

try {
  // ---- Desktop context (records video, does crawl + probes + interaction states) ----
  if (wantedViewports.includes('desktop')) {
    const context = await browser.newContext({
      viewport: { width: 1440, height: 900 },
      deviceScaleFactor: 1,
      recordVideo: { dir: outDir, size: { width: 1440, height: 900 } },
    });
    const page = await context.newPage();
    await loadPage(page, url);

    await page.screenshot({ path: `${outDir}/desktop.png`, fullPage: true });
    const meta = { title: await page.title(), url: page.url() };
    probe.viewports.desktop = meta;
    console.log(JSON.stringify({ viewport: 'desktop', path: `${outDir}/desktop.png`, ...meta }));

    // --- Tap-target inventory (C5) + interactive count (C2/C13 context) ---
    try {
      probe.tapTargets = await page.evaluate((sel) => {
        const els = [...document.querySelectorAll(sel)];
        const items = [];
        for (const el of els) {
          const r = el.getBoundingClientRect();
          if (r.width === 0 || r.height === 0) continue;
          const cs = getComputedStyle(el);
          if (cs.visibility === 'hidden' || cs.display === 'none') continue;
          items.push({
            tag: el.tagName.toLowerCase(),
            role: el.getAttribute('role') || null,
            text: (el.innerText || el.value || el.getAttribute('aria-label') || '').trim().slice(0, 40),
            w: Math.round(r.width),
            h: Math.round(r.height),
          });
        }
        const total = items.length;
        const under44 = items.filter((i) => i.w < 44 || i.h < 44).length;
        const under32 = items.filter((i) => i.w < 32 || i.h < 32).length;
        // Visible text length is recorded for the blank guard, which must not
        // treat a legitimate text-only screen as an unrendered one.
        const textLength = (document.body?.innerText || '').trim().length;
        return { total, under44, under32, textLength, pctGte44: total ? Math.round(((total - under44) / total) * 100) : null, sample: items.slice(0, 40) };
      }, INTERACTIVE);
    } catch (e) { probe.tapTargets = { error: e.message }; }

    // --- Motion / transition signals (C11, C12) ---
    try {
      probe.motion = await page.evaluate((sel) => {
        const els = [...document.querySelectorAll(sel)].slice(0, 60);
        const durations = new Set();
        let withTransition = 0, withAnimation = 0;
        for (const el of els) {
          const cs = getComputedStyle(el);
          if (cs.transitionDuration && cs.transitionDuration !== '0s') { withTransition++; cs.transitionDuration.split(',').forEach((d) => durations.add(d.trim())); }
          if (cs.animationName && cs.animationName !== 'none') withAnimation++;
        }
        let reducedMotion = false;
        for (const sheet of document.styleSheets) {
          try {
            for (const rule of sheet.cssRules) {
              if (rule.cssText && rule.cssText.includes('prefers-reduced-motion')) { reducedMotion = true; break; }
            }
          } catch { /* cross-origin sheet */ }
          if (reducedMotion) break;
        }
        return { sampled: els.length, withTransition, withAnimation, durations: [...durations].slice(0, 8), prefersReducedMotionHandled: reducedMotion };
      }, INTERACTIVE);
    } catch (e) { probe.motion = { error: e.message }; }

    // --- Design-token identity (C16; cross-checks C1/C14) ---
    // Which tokens are actually authored for this product, and whether the
    // platform's default tokens are still on screen. Measured on the resting
    // page, before the Tab press below changes any state.
    try {
      probe.identity = await page.evaluate(([sel, defaults, maxScan]) => {
        const bump = (m, k) => { if (k) m.set(k, (m.get(k) || 0) + 1); };
        const top = (m, n) => [...m.entries()].sort((a, b) => b[1] - a[1]).slice(0, n)
          .map(([value, count]) => ({ value, count }));

        // A default-token hit has to be actionable, so record where it is:
        // a CSS path an auditor can quote, plus the control's own label.
        const cssPath = (el) => {
          const part = (n) => {
            const tag = n.tagName.toLowerCase();
            if (n.id) return `${tag}#${n.id}`;
            const cls = [...n.classList].slice(0, 2).map((c) => `.${c}`).join('');
            return tag + cls;
          };
          const chain = [];
          for (let n = el; n && n.nodeType === 1 && chain.length < 3; n = n.parentElement) {
            chain.unshift(part(n));
            if (n.id || n.tagName.toLowerCase() === 'body') break;
          }
          return chain.join(' > ');
        };
        const labelOf = (el) => (el.children.length && !el.matches(sel))
          ? ''
          : (el.innerText || el.getAttribute('aria-label') || el.value || '').trim().slice(0, 40);

        const fonts = new Map(), text = new Map(), background = new Map();
        const accent = new Map(), radii = new Map(), shadows = new Map();
        const hits = new Map();
        const noteHit = (value, el, property) => {
          const d = defaults.find((x) => x.value === value);
          if (!d) return;
          let h = hits.get(value);
          if (!h) { h = { token: d.token, value, note: d.note, where: [], count: 0 }; hits.set(value, h); }
          h.count++;
          const selector = cssPath(el);
          // `where` is a bounded sample; `count` carries the true total.
          if (h.where.length < 4 && !h.where.some((w) => w.selector === selector && w.property === property)) {
            h.where.push({ selector, text: labelOf(el), property });
          }
        };
        const isOpaque = (c) => c && c !== 'transparent' && !/rgba\(.*,\s*0\)$/.test(c);

        // No pre-filter cap: a default token missed because it sat past a slice
        // boundary reads as an authored palette and scores C16 too high. The
        // bound below is a runaway guard only, and it reports when it bites.
        const all = [document.body, ...document.querySelectorAll('body *')];
        const els = all.slice(0, maxScan);
        let backgroundImages = 0;
        for (const el of els) {
          const cs = getComputedStyle(el);
          if (cs.visibility === 'hidden' || cs.display === 'none') continue;
          const rect = el.getBoundingClientRect();
          const area = rect.width * rect.height;

          const ownsText = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
          if (ownsText) {
            bump(fonts, cs.fontFamily);
            bump(text, cs.color);
            noteHit(cs.color, el, 'color');
          }
          if (isOpaque(cs.backgroundColor) && area > 400) {
            bump(background, cs.backgroundColor);
            noteHit(cs.backgroundColor, el, 'background-color');
          }
          if (el.matches(sel)) {
            if (isOpaque(cs.backgroundColor)) { bump(accent, cs.backgroundColor); noteHit(cs.backgroundColor, el, 'background-color'); }
            bump(accent, cs.color);
            noteHit(cs.color, el, 'color');
          }
          if (cs.borderRadius && cs.borderRadius !== '0px' && area > 400) bump(radii, cs.borderRadius);
          if (cs.boxShadow && cs.boxShadow !== 'none') bump(shadows, cs.boxShadow);
          if (cs.backgroundImage !== 'none') backgroundImages++;
        }

        return {
          screen: { url: location.href, title: document.title },
          sampled: els.length,
          truncated: all.length > els.length,
          fonts: top(fonts, 6),
          colors: { text: top(text, 6), background: top(background, 6), accent: top(accent, 6) },
          radii: top(radii, 6),
          shadows: top(shadows, 4),
          imagery: {
            img: document.querySelectorAll('img').length,
            svg: document.querySelectorAll('svg').length,
            backgroundImages,
          },
          osDefaults: { present: hits.size > 0, hits: [...hits.values()] },
        };
      }, [INTERACTIVE, OS_DEFAULT_TOKENS, IDENTITY_MAX_SCAN]);
    } catch (e) { probe.identity = { error: e.message }; }

    // --- Focus ring (C6) ---
    try {
      await page.keyboard.press('Tab');
      await page.waitForTimeout(150);
      probe.focus = await page.evaluate(() => {
        const el = document.activeElement;
        if (!el || el === document.body) return { focused: null };
        const cs = getComputedStyle(el);
        return {
          tag: el.tagName.toLowerCase(),
          text: (el.innerText || el.getAttribute('aria-label') || '').trim().slice(0, 40),
          outlineStyle: cs.outlineStyle,
          outlineWidth: cs.outlineWidth,
          outlineColor: cs.outlineColor,
          boxShadow: cs.boxShadow && cs.boxShadow !== 'none' ? 'present' : 'none',
        };
      });
      await page.screenshot({ path: `${outDir}/focus.png` }); // viewport only, shows the ring in context
      console.log(JSON.stringify({ capture: 'focus', path: `${outDir}/focus.png`, ...probe.focus }));
    } catch (e) { probe.focus = { error: e.message }; }

    // --- Hover before/after on the first VISIBLE prominent control (C12) ---
    // Selector matches can be invisible (collapsed navs, visibility:hidden);
    // scrolling one times out and kills the probe, so scan for visibility first.
    try {
      const candidates = page.locator('button, [role=button], a[href]').filter({ hasText: /\S/ });
      const count = await candidates.count();
      let btn = null;
      for (let i = 0; i < count; i++) {
        if (await candidates.nth(i).isVisible()) { btn = candidates.nth(i); break; }
      }
      if (!btn) {
        probe.hover = { skipped: `no visible hoverable control among ${count} candidates` };
      } else {
        await btn.scrollIntoViewIfNeeded({ timeout: 5000 });
        await page.waitForTimeout(200);
        await btn.screenshot({ path: `${outDir}/hover-before.png` });
        const before = await btn.evaluate((el) => { const c = getComputedStyle(el); return { bg: c.backgroundColor, boxShadow: c.boxShadow, transform: c.transform, transition: c.transitionProperty }; });
        await btn.hover();
        await page.waitForTimeout(350);
        await btn.screenshot({ path: `${outDir}/hover-after.png` });
        const after = await btn.evaluate((el) => { const c = getComputedStyle(el); return { bg: c.backgroundColor, boxShadow: c.boxShadow, transform: c.transform }; });
        probe.hover = { label: (await btn.innerText().catch(() => '')).trim().slice(0, 40), before, after, changed: JSON.stringify(before) !== JSON.stringify({ ...after, transition: before.transition }) };
        console.log(JSON.stringify({ capture: 'hover', before: `${outDir}/hover-before.png`, after: `${outDir}/hover-after.png`, label: probe.hover.label }));
      }
    } catch (e) { probe.hover = { error: e.message }; }

    // --- Shallow crawl of in-app surfaces (C9, C10) ---
    if (!noCrawl && maxScreens > 0) {
      try {
        const origin = new URL(url);
        const base = '/' + origin.pathname.split('/').filter(Boolean)[0]; // e.g. /Smith_Enterprise
        const links = await page.evaluate((baseArg) => {
          const seen = new Set();
          const out = [];
          for (const a of document.querySelectorAll('a[href]')) {
            let u;
            try { u = new URL(a.href, location.href); } catch { continue; }
            if (u.origin !== location.origin) continue;
            if (!u.pathname.startsWith(baseArg)) continue;
            if (u.pathname === location.pathname) continue;
            if (seen.has(u.pathname)) continue;
            seen.add(u.pathname);
            out.push({ href: u.href, label: (a.innerText || '').trim().slice(0, 30), path: u.pathname });
          }
          return out;
        }, base);
        let n = 0;
        for (const link of links.slice(0, maxScreens)) {
          n++;
          const slug = (link.path.split('/').filter(Boolean).pop() || `screen${n}`).replace(/[^a-z0-9]+/gi, '-').toLowerCase();
          const path = `${outDir}/screen-${String(n).padStart(2, '0')}-${slug}.png`;
          try {
            await loadPage(page, link.href);
            await page.screenshot({ path, fullPage: true });
            const info = { path, label: link.label, url: page.url(), title: await page.title() };
            probe.crawled.push(info);
            console.log(JSON.stringify({ capture: 'crawl', ...info }));
          } catch (e) {
            probe.crawled.push({ path, href: link.href, error: e.message });
          }
        }
      } catch (e) { probe.crawlError = e.message; }
    }

    await page.close();
    await context.close();
    // Rename the auto-named video to session.webm
    try {
      const vids = readdirSync(outDir).filter((f) => f.endsWith('.webm'));
      if (vids.length) renameSync(`${outDir}/${vids[0]}`, `${outDir}/session.webm`);
    } catch { /* ignore */ }
  }

  // ---- Mobile context (landing only) ----
  if (wantedViewports.includes('mobile')) {
    const vp = VIEWPORTS.mobile;
    const context = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
      deviceScaleFactor: vp.deviceScaleFactor,
      isMobile: vp.isMobile,
      hasTouch: vp.hasTouch,
    });
    const page = await context.newPage();
    await loadPage(page, url);
    await page.screenshot({ path: `${outDir}/mobile.png`, fullPage: true });
    const meta = { title: await page.title(), url: page.url() };
    probe.viewports.mobile = meta;
    console.log(JSON.stringify({ viewport: 'mobile', path: `${outDir}/mobile.png`, ...meta }));
    await context.close();
  }

  const blank = blankCapture(probe);
  if (blank) {
    writeFileSync(`${outDir}/CAPTURE-FAILED.json`, JSON.stringify(blank, null, 2));
    console.error(JSON.stringify({
      captureFailed: `${outDir}/CAPTURE-FAILED.json`,
      ...blank,
      note: 'probe.json deliberately NOT written — scoring this capture would '
        + 'read an unrendered page as a clean app',
    }, null, 2));
    process.exitCode = 3;
  } else {
  writeFileSync(`${outDir}/probe.json`, JSON.stringify(probe, null, 2));
  console.log(JSON.stringify({
    probe: `${outDir}/probe.json`,
    tapTargets: probe.tapTargets && { total: probe.tapTargets.total, pctGte44: probe.tapTargets.pctGte44 },
    motion: probe.motion,
    identity: probe.identity && !probe.identity.error && {
      fonts: probe.identity.fonts.length,
      accents: probe.identity.colors.accent.length,
      radii: probe.identity.radii.length,
      osDefaults: probe.identity.osDefaults,
    },
    focus: probe.focus,
    crawled: probe.crawled.length,
  }));
  }
} finally {
  await browser.close();
}
