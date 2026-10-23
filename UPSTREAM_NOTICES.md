# Upstream project review and provenance

Reviewed on 2026-10-23. This project does not contain a fork or vendored copy of the repositories listed below. The new animation templates in `remotion_templates/` are independently authored implementations based on general motion-design ideas; they do not copy source files from those projects.

| Upstream | License observed in repository | Practical note |
|---|---|---|
| [Magic UI](https://github.com/magicuidesign/magicui) | MIT (`LICENSE.md`) | MIT allows use, modification, distribution, and commercial use, subject to retaining its copyright and permission notice in copies/substantial portions. Any Magic UI component copied/adapted later should retain its required notice. |
| [Remotion](https://github.com/remotion-dev/remotion) | Remotion's custom license (`LICENSE.md`), not MIT | The reviewed license allows eligible individuals and small organizations (up to 3 employees), nonprofits, and evaluation use to use/modify Remotion for video/image creation, including commercial video output. It prohibits copying/modifying Remotion code to sell, rent, license, relicense, or sublicense a derivative of Remotion. Larger for-profit organizations need a company license. Check the current license and eligibility before use; this is a summary, not legal advice. |
| [HyperFrames](https://github.com/heygen-com/hyperframes) | Apache License 2.0 (`LICENSE`) | Apache-2.0 permits commercial use and modification, with conditions including preserving notices, providing the license, and marking modified files; patent and NOTICE provisions also apply. No HyperFrames source was copied into this project. |

Licenses can change. These notes describe the repository license files inspected at the review date; inspect the current upstream license before redistributing upstream-derived code. The project’s existing MIT license does not override third-party terms for any future copied or vendored component.

## New templates

- `AnimatedGradientText.tsx` — deterministic gradient text sweep.
- `DrawPath.tsx` — deterministic SVG stroke reveal with a moving endpoint.
- `SpotlightCard.tsx` — focused UI card entrance treatment.

All three are original PixelMotion additions and require the host project to have `react` and `remotion` installed. They use Remotion's public frame hooks and do not vendor Remotion's implementation.
