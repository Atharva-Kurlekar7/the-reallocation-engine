#!/bin/bash
# Markdown -> print-ready PDF, via pandoc + headless Chrome.
#
#   ./scripts/md-to-pdf.sh FILE.md [FILE2.md ...]
#
# Writes FILE.pdf beside each input. No LaTeX required.
set -euo pipefail

CHROME=""
for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
         "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" \
         "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"; do
  [[ -x "$c" ]] && { CHROME="$c"; break; }
done
[[ -n "$CHROME" ]] || { echo "no Chrome/Brave/Edge found for PDF printing" >&2; exit 1; }
command -v pandoc >/dev/null || { echo "pandoc not found (brew install pandoc)" >&2; exit 1; }
[[ $# -gt 0 ]] || { echo "usage: $0 FILE.md [FILE2.md ...]" >&2; exit 1; }

CSS="$(cat <<'STYLE'
@page { size: Letter; margin: 0.75in; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
  font-size: 10.5pt; line-height: 1.5; color: #1a1a1a; max-width: none; margin: 0;
}
h1 { font-size: 20pt; margin: 0 0 .3em; border-bottom: 3px solid #c8102e; padding-bottom: .25em; }
h2 { font-size: 13pt; margin: 1.4em 0 .5em; color: #c8102e; page-break-after: avoid; }
h3 { font-size: 11pt; margin: 1.1em 0 .4em; page-break-after: avoid; }
p, li { orphans: 3; widows: 3; }
table { border-collapse: collapse; width: 100%; margin: .8em 0; font-size: 9.5pt;
        page-break-inside: avoid; }
th, td { border: 1px solid #d0d0d0; padding: 5px 8px; text-align: left; vertical-align: top; }
th { background: #f4f4f4; font-weight: 600; }
code { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 9pt;
       background: #f4f4f4; padding: 1px 4px; border-radius: 3px; }
pre { background: #f7f7f7; border: 1px solid #e0e0e0; border-left: 3px solid #c8102e;
      padding: 9px 11px; overflow-x: auto; page-break-inside: avoid; border-radius: 3px; }
pre code { background: none; padding: 0; font-size: 8.5pt; line-height: 1.4; }
blockquote { border-left: 3px solid #c8102e; margin: .8em 0; padding: .3em 0 .3em 1em;
             color: #444; background: #fafafa; }
a { color: #0b5fff; text-decoration: none; word-break: break-all; }
hr { border: none; border-top: 1px solid #ddd; margin: 1.6em 0; }
STYLE
)"

for md in "$@"; do
  [[ -f "$md" ]] || { echo "skip (not found): $md" >&2; continue; }
  base="${md%.md}"
  tmp_css="$(mktemp -t mdpdf).css"
  tmp_html="$(mktemp -t mdpdf).html"
  printf '%s' "$CSS" > "$tmp_css"

  pandoc "$md" --standalone --embed-resources --css="$tmp_css" \
         --metadata title="$(basename "$base")" -o "$tmp_html"

  "$CHROME" --headless --disable-gpu --no-pdf-header-footer \
            --print-to-pdf="$base.pdf" "file://$tmp_html" >/dev/null 2>&1

  rm -f "$tmp_css" "$tmp_html"
  if [[ -f "$base.pdf" ]]; then
    printf '  %-62s %s\n' "${base##*/}.pdf" "$(du -h "$base.pdf" | cut -f1)"
  else
    echo "  FAILED: $md" >&2
  fi
done
