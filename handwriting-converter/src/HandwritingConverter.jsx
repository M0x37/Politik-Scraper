import React, { useState, useEffect, useRef, useCallback } from 'react';
import './HandwritingConverter.css';
import { Shuffle, Download, Tornado, RotateCw, PenLine } from 'lucide-react';

const FONTS = [
  { l: 'Caveat', v: 'Caveat' },
  { l: 'Reenie', v: 'Reenie Beanie' },
  { l: 'Shadows', v: 'Shadows Into Light' },
  { l: 'Rock Salt', v: 'Rock Salt' },
  { l: 'Homemade', v: 'Homemade Apple' },
];

const COLORS = [
  { h: '#000000', n: 'Schwarz' },
];

const PAPERS = [
  { l: 'Liniert', v: 'lined' },
  { l: 'Blanko', v: 'blank' },
  { l: 'Kariert', v: 'grid' },
];

const HandwritingConverter = () => {
  // Read text from URL parameter or use default
  const getInitialText = () => {
    const params = new URLSearchParams(window.location.search);
    const urlText = params.get('text');
    return urlText || '';
  };
  
  const [text, setText] = useState(getInitialText());
  const [selectedFont, setSelectedFont] = useState('Caveat');
  const [selectedColor, setSelectedColor] = useState('#000000');
  const [selectedPaper, setSelectedPaper] = useState('lined');
  const [fontSize, setFontSize] = useState(30);
  const [chaos, setChaos] = useState(7);
  const canvasRef = useRef(null);
  const renderTimeoutRef = useRef(null);

  // PRNG (seeded LCG so render is deterministic per seed)
  const sr = useCallback(() => {
    sr._seed = (sr._seed * 1664525 + 1013904223) >>> 0;
    return sr._seed / 0x100000000;
  }, []);

  const srN = useCallback((a, b) => {
    return a + sr() * (b - a);
  }, [sr]);

  const srG = useCallback(() => {
    let s = 0;
    for (let i = 0; i < 6; i++) s += sr();
    return (s - 3) / 1.73;
  }, [sr]);

  // Catmull-Rom smooth noise
  const makeNoise = useCallback((N) => {
    const p = new Float32Array(N + 8);
    for (let i = 0; i < p.length; i++) p[i] = srG();
    return (t) => {
      t = Math.max(0, t);
      const i = Math.floor(t), f = t - i;
      const p0 = p[Math.max(0, i - 1)], p1 = p[i] ?? 0, p2 = p[i + 1] ?? 0, p3 = p[i + 2] ?? 0;
      const f2 = f * f, f3 = f2 * f;
      return 0.5 * ((2 * p1) + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f2 + (-p0 + 3 * p1 - 3 * p2 + p3) * f3);
    };
  }, [srG]);

  const drawPaper = useCallback((ctx, W, H, type, LH, topY) => {
    // Always white background
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, W, H);

    // Grain (very subtle on blank/white)
    const id = ctx.getImageData(0, 0, W, H), d = id.data;
    const grainStr = type === 'blank' ? 5 : 14;
    for (let i = 0; i < d.length; i += 12) {
      const n = (Math.random() - 0.5) * grainStr;
      d[i] = clamp(d[i] + n);
      d[i + 1] = clamp(d[i + 1] + n * 0.8);
      d[i + 2] = clamp(d[i + 2] + n * 0.55);
    }
    ctx.putImageData(id, 0, 0);

    if (type === 'blank') return;

    ctx.strokeStyle = 'rgba(100,140,200,.25)'; // More transparent so text shows through
    ctx.lineWidth = 0.9;
    const y0 = Math.round(topY + LH * 0.55) + 0.5;
    for (let y = y0; y < H - 8; y += LH) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(W, y);
      ctx.stroke();
    }
    if (type === 'grid') {
      for (let x = LH; x < W; x += LH) {
        ctx.beginPath();
        ctx.moveTo(Math.round(x) + 0.5, 0);
        ctx.lineTo(Math.round(x) + 0.5, H);
        ctx.stroke();
      }
    }
  }, []);

  const wrapText = useCallback((ctx, text, maxW) => {
    const res = [];
    text.split('\n').forEach(raw => {
      if (!raw.trim()) {
        res.push('');
        return;
      }
      let line = '';
      raw.split(' ').forEach(w => {
        const t = line ? line + ' ' + w : w;
        ctx.measureText(t).width <= maxW ? line = t : (res.push(line), line = w);
      });
      if (line) res.push(line);
    });
    return res;
  }, []);

  const hexToRgb = useCallback((h) => {
    return [
      parseInt(h.slice(1, 3), 16),
      parseInt(h.slice(3, 5), 16),
      parseInt(h.slice(5, 7), 16)
    ];
  }, []);

  const clamp = useCallback((v) => {
    return Math.min(255, Math.max(0, Math.round(v)));
  }, []);

  const clamp01 = useCallback((v) => {
    return Math.min(1, Math.max(0, v));
  }, []);

  const render = useCallback(() => {
    // New seed each call
    sr._seed = ((Date.now() ^ (Math.random() * 0xfffffff | 0)) >>> 0) || 1;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const dpr = window.devicePixelRatio || 1;
    const W = 680, H = 940;
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    canvas.style.width = '100%';
    canvas.style.height = 'auto';
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    ctx.scale(dpr, dpr);
    
    // Enable high-quality rendering
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    ctx.textBaseline = 'alphabetic';
    ctx.textRendering = 'optimizeLegibility';

    // Auto-adjust font size to fit text on page
    let adjustedFontSize = fontSize;
    let maxLines;
    
    // Calculate how many lines can fit
    const calculateMaxLines = (size) => {
      const lineHeight = size * 2.4; // Increased line height
      const topMargin = size * 1.8; // Increased top margin
      const bottomMargin = 20; // Leave some space at bottom
      return Math.floor((H - topMargin - bottomMargin) / lineHeight);
    };
    
    // Calculate how many lines the text needs
    const calculateTextLines = (size) => {
      ctx.font = `${size}px '${selectedFont}', cursive`;
      const lineHeight = size * 2.4; // Increased line height
      const topMargin = size * 1.8; // Increased top margin
      const hasMargin = selectedPaper !== 'grid' && selectedPaper !== 'blank';
      const marginX = 54;
      const startX = hasMargin ? marginX + 10 : 24;
      const maxW = W - startX - 45; // Increased right margin
      const lines = wrapText(ctx, text, maxW);
      return lines.length;
    };
    
    // Iteratively adjust font size until text fits
    let attempts = 0;
    const maxAttempts = 10;
    const minFontSize = 12; // Minimum readable size
    let wasAdjusted = false;
    
    while (attempts < maxAttempts) {
      maxLines = calculateMaxLines(adjustedFontSize);
      const textLines = calculateTextLines(adjustedFontSize);
      
      if (textLines <= maxLines || adjustedFontSize <= minFontSize) {
        break; // Text fits or reached minimum size
      }
      
      // Reduce font size and try again
      adjustedFontSize = Math.max(minFontSize, adjustedFontSize - 2);
      attempts++;
      wasAdjusted = true;
    }
    
    // Show notification if font size was adjusted
    if (wasAdjusted && adjustedFontSize < fontSize) {
      console.log(`Schriftgröße automatisch von ${fontSize}px auf ${adjustedFontSize}px angepasst, damit der Text auf die Seite passt.`);
    }

    const LH = adjustedFontSize * 2.4; // Increased line height for more spacing
    const topY = adjustedFontSize * 1.8; // Increased top margin
    const hasMargin = selectedPaper !== 'grid' && selectedPaper !== 'blank';
    const marginX = 54;
    const startX = hasMargin ? marginX + 10 : 24;
    const maxW = W - startX - 45; // Increased right margin

    // Draw paper first
    drawPaper(ctx, W, H, selectedPaper, LH, topY);

    ctx.font = `${adjustedFontSize}px '${selectedFont}', cursive`;
    const lines = wrapText(ctx, text, maxW);
    const nL = lines.length;

    // Line-level noise (affects whole line consistently)
    const nLineY = makeNoise(nL + 6);  // vertical offset of line baseline
    const nLineSlope = makeNoise(nL + 6); // slope per line (tilts across width)
    const nLineSz = makeNoise(nL + 6);  // global size bias per line
    const nLineSkew = makeNoise(nL + 6);  // italic-lean bias per line

    const [ir, ig, ib] = hexToRgb(selectedColor);

    lines.forEach((line, li) => {
      if (!line && li > 0) {
        return; // skip blank lines but keep spacing
      }
      const baseY = topY + li * LH;
      if (baseY > H - 16) return;

      // Line-level properties - balanced for handwriting look
      const lineDrift = nLineY(li) * (chaos / 10) * adjustedFontSize * 0.08; // Moderate drift
      // slope: line gently climbs or descends across its width
      const lineSlope = nLineSlope(li) * (chaos / 10) * 0.030;
      // size modifier for whole line (some lines written bigger/smaller)
      const lineSizeMod = nLineSz(li) * (chaos / 10) * 0.14;
      // global lean for the line (some lines more upright, some more leaning)
      const lineLean = nLineSkew(li) * (chaos / 10) * 0.10;

      // Per-character noise
      const nY = makeNoise(line.length + 5);
      const nR = makeNoise(line.length + 5);
      const nSz = makeNoise(line.length + 5);
      const nAl = makeNoise(line.length + 5);
      const nSp = makeNoise(line.length + 5);
      const nSqz = makeNoise(line.length + 5);
      const nPrs = makeNoise(line.length + 5); // pen pressure (affects weight/opacity)
      const nSkew = makeNoise(line.length + 5); // additional character skew
      const nBaseline = makeNoise(line.length + 5); // baseline shift per character

      // Occasionally one or two words in the line are written in a "rush"
      // (slightly smaller & more compressed)
      const rushWord = chaos > 4 && sr() < 0.35 ? Math.floor(sr() * 5) : -99;
      let wordIdx = 0;
      let x = startX;

      for (let ci = 0; ci < line.length; ci++) {
        const ch = line[ci];
        if (ch === ' ') wordIdx++;
        const inRush = wordIdx === rushWord;

        // Vertical position - natural handwriting variation
        const charSlope = (x - startX) * lineSlope * 0.7; // Moderate slope
        const bounce = nY(ci) * (chaos / 10) * adjustedFontSize * 0.18; // Moderate bounce for handwriting feel
        const baselineShift = nBaseline(ci) * (chaos / 10) * adjustedFontSize * 0.08; // Moderate baseline variation
        const rushDip = inRush ? adjustedFontSize * 0.06 : 0;
        const cy = baseY + lineDrift + bounce + charSlope + rushDip + baselineShift;

        // Rotation - natural handwriting variation
        const baseRot = lineLean * 0.8 + nR(ci) * (chaos / 10) * 0.15; // Moderate rotation for handwriting
        const extraRot = nSkew(ci) * (chaos / 10) * 0.10; // Moderate additional skew
        const rot = baseRot + extraRot;

        // Size with more variation
        const rushScale = inRush ? 0.88 : 1;
        const sizeVariation = nSz(ci) * (chaos / 10) * 0.35; // Increased size variation
        const sz = adjustedFontSize * (1 + lineSizeMod + sizeVariation) * rushScale;

        // Opacity - always 100% saturation
        const al = 1.0; // Always full opacity

        // Spacing with more chaos
        const spacingVariation = nSp(ci + 0.5) * (chaos / 10) * 0.40; // Increased spacing variation
        const spaceMult = (1 + spacingVariation) * (inRush ? 0.82 : 1);

        // Horizontal squeeze with more chaos
        const squeezeVariation = nSqz(ci + 1) * (chaos / 10) * 0.20; // Increased squeeze
        const sqz = 1 + squeezeVariation;

        // Enhanced ink color - make it bold and preserve true black
        const isBlack = ir === 0 && ig === 0 && ib === 0;
        
        let r2, g2, b2;
        
        if (isBlack) {
          // True black - keep it exactly #000000
          r2 = 0;
          g2 = 0;
          b2 = 0;
        } else {
                    // For other colors, apply darkening
          const pressure = clamp01(0.5 + nPrs(ci) * 0.5);
          const pressureIntensity = 0.5 + (pressure * 0.5);

          const darknessFactor = 0.3;
          
          r2 = ir * darknessFactor * pressureIntensity;
          g2 = ig * darknessFactor * pressureIntensity;  
          b2 = ib * darknessFactor * pressureIntensity;
          
          // Almost no fade effect
          const fade = (1 - pressure) * 2 * (chaos / 10);
          r2 = Math.min(255, r2 + fade * 0.05);
          g2 = Math.min(255, g2 + fade * 0.02);
          b2 = Math.min(255, b2 + fade * 0.01);
          
          // Ensure minimum darkness for bold appearance
          const maxRGB = Math.max(r2, g2, b2);
          if (maxRGB > 80) {
            const scale = 0.6;
            r2 *= scale;
            g2 *= scale;
            b2 *= scale;
          }
          
          // Ensure minimum RGB values for readability
          r2 = Math.max(20, r2);
          g2 = Math.max(20, g2);
          b2 = Math.max(20, b2);
        }
        
        // Final clamp to valid range
        r2 = clamp(r2);
        g2 = clamp(g2);
        b2 = clamp(b2);

        // Additional chaos effects
        const verticalStretch = 1 + (chaos / 10) * 0.1 * Math.sin(ci * 0.5); // Subtle vertical variation
        const charShear = nSkew(ci + 2) * (chaos / 10) * 0.1; // Character shearing
        
        ctx.save();
        ctx.globalAlpha = al;
        ctx.translate(x, cy);
        ctx.rotate(rot);
        ctx.transform(1, charShear, 0, verticalStretch, 0, 0); // Apply shear and stretch
        ctx.scale(sqz, 1);
        ctx.font = `${sz}px '${selectedFont}', cursive`;
        ctx.fillStyle = `rgb(${r2},${g2},${b2})`;
        
        // Add slight character wobble for high chaos
        if (chaos > 7) {
          const wobbleX = (Math.random() - 0.5) * (chaos / 10) * 2;
          const wobbleY = (Math.random() - 0.5) * (chaos / 10) * 2;
          ctx.translate(wobbleX, wobbleY);
        }
        
        ctx.fillText(ch, 0, 0);
        ctx.restore();

        // Advance cursor
        ctx.font = `${adjustedFontSize}px '${selectedFont}', cursive`;
        const charWidth = ctx.measureText(ch).width * spaceMult * sqz;
        // Add extra space after words (when current char is space or next char is space)
        const extraWordSpace = (ch === ' ' || (ci < line.length - 1 && line[ci + 1] === ' ')) ? adjustedFontSize * 0.15 : 0;
        x += charWidth + extraWordSpace;
      }
    });
  }, [text, fontSize, chaos, selectedFont, selectedColor, selectedPaper, sr, srG, makeNoise, drawPaper, wrapText, hexToRgb, clamp, clamp01]);

  const downloadImage = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const fileName = 'handschrift.png';
    const isIPad = /iPad|iPhone|iPod/.test(navigator.userAgent) ||
      (navigator.userAgent.includes('Macintosh') && navigator.maxTouchPoints > 1);

    canvas.toBlob((blob) => {
      if (!blob) return;

      const file = new File([blob], fileName, { type: 'image/png' });

      const fallback = () => {
        const url = URL.createObjectURL(blob);
        if (isIPad) {
          window.open(url, '_blank');
          setTimeout(() => URL.revokeObjectURL(url), 30000);
        } else {
          const a = document.createElement('a');
          a.href = url;
          a.download = fileName;
          document.body.appendChild(a);
          a.click();
          a.remove();
          setTimeout(() => URL.revokeObjectURL(url), 1000);
        }
      };

      if (isIPad && navigator.canShare && navigator.canShare({ files: [file] })) {
        navigator.share({ files: [file], title: fileName })
          .catch((err) => {
            if (err.name !== 'AbortError') fallback();
          });
        return;
      }

      fallback();
    }, 'image/png');
  }, []);

  // Handle text input with debounced rendering
  useEffect(() => {
    clearTimeout(renderTimeoutRef.current);
    renderTimeoutRef.current = setTimeout(render, 350);
    return () => clearTimeout(renderTimeoutRef.current);
  }, [text, render]);

  // Initial render
  useEffect(() => {
    render();
  }, [render]);

  return (
    <div className="handwriting-converter">
      <header className="nav">
        <div className="nav-brand">
          <PenLine size={18} strokeWidth={1.5} />
          <span>Handschrift Converter</span>
        </div>
        <div className="nav-btns">
          <button className="btn ghost" onClick={render} data-testid="regenerate-button">
            <Shuffle size={16} strokeWidth={1.5} /> Neu
          </button>
          <button className="btn primary" onClick={downloadImage} data-testid="download-button">
            <Download size={16} strokeWidth={1.5} /> PNG
          </button>
        </div>
      </header>

      <main className="content">
        <section className="card input-card">
          <div className="cl">
            <PenLine size={13} strokeWidth={1.5} /> Text
          </div>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Text hier eingeben..."
            data-testid="text-input"
          />
        </section>

        <section className="card canvas-card">
          <canvas ref={canvasRef} id="paper" />
        </section>

        <section className="card controls">
          <div className="control-block">
            <div className="cl">Schriftstil</div>
            <div className="font-scroll">
              {FONTS.map(font => (
                <button
                  key={font.v}
                  className={`fb ${font.v === selectedFont ? 'active' : ''}`}
                  style={{ fontFamily: `'${font.v}', cursive` }}
                  onClick={() => {
                    setSelectedFont(font.v);
                    render();
                  }}
                  data-testid="font-option"
                >
                  {font.l}
                </button>
              ))}
            </div>
          </div>

          <div className="control-block">
            <div className="cl">Schriftgröße — {fontSize}px</div>
            <div className="srow">
              <input
                type="range"
                min="20"
                max="48"
                value={fontSize}
                onChange={(e) => setFontSize(parseInt(e.target.value))}
                data-testid="font-size-slider"
              />
            </div>
          </div>

          <div className="control-block">
            <div className="cl">
              <Tornado size={13} strokeWidth={1.5} /> Chaos-Level — {chaos}
            </div>
            <div className="srow">
              <input
                type="range"
                min="1"
                max="10"
                value={chaos}
                onChange={(e) => setChaos(parseInt(e.target.value))}
                data-testid="chaos-slider"
              />
            </div>
          </div>

          <div className="control-block">
            <div className="cl">Tintenfarbe</div>
            <div className="swatches">
              {COLORS.map(color => (
                <div
                  key={color.h}
                  className={`sw ${color.h === selectedColor ? 'active' : ''}`}
                  style={{ background: color.h }}
                  title={color.n}
                  onClick={() => {
                    setSelectedColor(color.h);
                    render();
                  }}
                  data-testid="color-swatch"
                />
              ))}
            </div>
          </div>

          <div className="control-block">
            <div className="cl">Papier</div>
            <div className="paperopts">
              {PAPERS.map(paper => (
                <button
                  key={paper.v}
                  className={`btn paper ${paper.v === selectedPaper ? 'active' : ''}`}
                  onClick={() => {
                    setSelectedPaper(paper.v);
                    render();
                  }}
                  data-testid="paper-option"
                >
                  {paper.l}
                </button>
              ))}
            </div>
          </div>

          <hr className="divider" />
          <button
            className="btn primary wide"
            onClick={render}
            data-testid="regenerate-button"
          >
            <RotateCw size={16} strokeWidth={1.5} /> Neu generieren
          </button>
        </section>
      </main>
    </div>
  );
};

export default HandwritingConverter;
