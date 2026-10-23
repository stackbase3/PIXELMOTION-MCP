/**
 * PixelMotion 3D Feature Callouts & Connectors
 * Renders dimensional callout cards, animated SVG connector curves,
 * and boundary tracing frames around target interface features.
 */

class FeatureCalloutEngine {
  constructor() {}

  /**
   * Generates a curved 3D connector path from interface coordinate (x1, y1) to callout badge (x2, y2).
   */
  renderConnectorSVG(x1, y1, x2, y2, color = "#38BDF8", progress = 1.0) {
    const dx = x2 - x1;
    const dy = y2 - y1;
    const cx1 = x1 + dx * 0.4;
    const cy1 = y1;
    const cx2 = x1 + dx * 0.6;
    const cy2 = y2;

    const pathData = `M ${x1} ${y1} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${x2} ${y2}`;
    const strokeDashoffset = Math.round((1 - Math.max(0, Math.min(1, progress))) * 400);

    return `
      <svg class="feature-connector" style="
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 250;
      ">
        <defs>
          <filter id="subtleGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <path d="${pathData}" fill="none" stroke="${color}" stroke-width="2.5"
              stroke-linecap="round" stroke-dasharray="400" stroke-dashoffset="${strokeDashoffset}"
              filter="url(#subtleGlow)" />
        <circle cx="${x1}" cy="${y1}" r="4" fill="${color}" opacity="${progress > 0.1 ? 1 : 0}" />
        <circle cx="${x2}" cy="${y2}" r="5" fill="#FFFFFF" stroke="${color}" stroke-width="2" opacity="${progress > 0.9 ? 1 : 0}" />
      </svg>
    `;
  }

  /**
   * Generates an animated highlight border tracing an interface boundary.
   */
  renderHighlightFrame(x, y, width, height, color = "#38BDF8", progress = 1.0) {
    const perimeter = 2 * (width + height);
    const dashOffset = Math.round((1 - Math.max(0, Math.min(1, progress))) * perimeter);

    return `
      <div class="feature-highlight-boundary" style="
        position: absolute;
        left: ${x - 4}px;
        top: ${y - 4}px;
        width: ${width + 8}px;
        height: ${height + 8}px;
        pointer-events: none;
        z-index: 200;
      ">
        <svg width="100%" height="100%" style="overflow: visible;">
          <rect x="0" y="0" width="${width + 8}" height="${height + 8}" rx="8"
                fill="none" stroke="${color}" stroke-width="2"
                stroke-dasharray="${perimeter}" stroke-dashoffset="${dashOffset}" />
        </svg>
      </div>
    `;
  }

  /**
   * Generates a sleek, dimensional callout card with title, metric, and description.
   */
  renderCalloutCard(callout, progress = 1.0) {
    const opacity = Math.min(1, progress * 1.5);
    const translateY = (1 - progress) * 20;

    return `
      <div class="callout-card-3d" style="
        position: absolute;
        left: ${callout.x}px;
        top: ${callout.y}px;
        width: ${callout.width || 320}px;
        padding: 16px 20px;
        background: rgba(15, 23, 42, 0.92);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 12px;
        box-shadow: 0 20px 40px -8px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(255, 255, 255, 0.05);
        opacity: ${opacity};
        transform: translate3d(0, ${translateY}px, ${callout.z || 60}px);
        transform-style: preserve-3d;
        z-index: 300;
        color: #F8FAFC;
        font-family: 'Inter', -apple-system, sans-serif;
      ">
        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: #38BDF8; font-weight: 600; margin-bottom: 4px;">
          ${callout.category || "Feature Spotlight"}
        </div>
        <div style="font-size: 18px; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">
          ${callout.title}
        </div>
        <div style="font-size: 13px; line-height: 1.45; color: #94A3B8;">
          ${callout.description}
        </div>
        ${callout.badge ? `
          <div style="margin-top: 10px; display: inline-flex; align-items: center; padding: 4px 10px; background: rgba(56, 189, 248, 0.12); border-radius: 20px; font-size: 12px; font-weight: 600; color: #38BDF8;">
            ${callout.badge}
          </div>
        ` : ''}
      </div>
    `;
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { FeatureCalloutEngine };
}
