#!/usr/bin/env python3
"""Inline CSS from styles.css into experience.html, producing experience-inlined.html."""

import re
import sys
from pathlib import Path


def parse_css_rules(css_text: str) -> list[tuple[str, str]]:
    """Parse CSS text into (selector, declarations) pairs, handling nested braces."""
    # Remove comments
    css_text = re.sub(r'/\*.*?\*/', '', css_text, flags=re.DOTALL)

    rules = []
    i = 0
    while i < len(css_text):
        # Skip whitespace
        while i < len(css_text) and css_text[i] in ' \t\n\r':
            i += 1
        if i >= len(css_text):
            break

        # Find the opening brace
        brace_pos = css_text.find('{', i)
        if brace_pos == -1:
            break

        selector = css_text[i:brace_pos].strip()

        # Find matching closing brace (handle nesting)
        depth = 1
        j = brace_pos + 1
        while j < len(css_text) and depth > 0:
            if css_text[j] == '{':
                depth += 1
            elif css_text[j] == '}':
                depth -= 1
            j += 1

        body = css_text[brace_pos + 1:j - 1].strip()

        # Flatten nested @-rules
        if selector.startswith('@media') or selector.startswith('@layer'):
            rules.extend(parse_css_rules(body))
        elif selector.startswith('@'):
            # Skip keyframes, font-face, etc.
            pass
        else:
            rules.append((selector, body))

        i = j

    return rules


def extract_classes_from_html(html: str) -> set[str]:
    """Extract all class names referenced in the HTML."""
    classes = set()
    for match in re.finditer(r'class="([^"]*)"', html):
        for cls in match.group(1).split():
            classes.add(cls)
    return classes


def selector_matches_classes(selector: str, classes: set[str]) -> bool:
    """Check if a CSS selector references any of the given classes."""
    # Extract class names from the selector
    selector_classes = re.findall(r'\.([a-zA-Z_][a-zA-Z0-9_-]*)', selector)
    return any(cls in classes for cls in selector_classes)

    # Also match element selectors and pseudo-elements that might apply
    # For simplicity, we include rules that reference our classes


def main():
    base = Path(__file__).parent
    html_path = base / 'experience.html'
    css_path = base / 'styles.css'
    out_path = base / 'experience-inlined.html'

    html = html_path.read_text(encoding='utf-8')
    css = css_path.read_text(encoding='utf-8')

    # Get all classes used in the HTML
    classes = extract_classes_from_html(html)
    print(f"Found {len(classes)} unique classes in HTML")

    # Parse CSS and filter to relevant rules
    all_rules = parse_css_rules(css)
    print(f"Parsed {len(all_rules)} CSS rules total")

    # Elements used in the HTML
    html_elements = set(re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)', html))

    relevant = []
    for selector, body in all_rules:
        # Include rules that reference classes from our HTML
        if selector_matches_classes(selector, classes):
            relevant.append((selector, body))
            continue

        # Include reset/universal selectors (*, :root, html, body)
        # Check comma-separated selector parts individually
        parts = [p.strip() for p in selector.split(',')]
        for part in parts:
            part_classes = re.findall(r'\.([a-zA-Z_][a-zA-Z0-9_-]*)', part)
            if not part_classes:
                # No class references - bare element, universal, or pseudo selector
                if part.startswith('*') or part.startswith(':') or \
                   any(re.search(rf'(?:^|[\s>+~])({re.escape(tag)})(?:[\s>+~:.\[#{{]|$)', part)
                       for tag in html_elements):
                    relevant.append((selector, body))
                    break

    print(f"Filtered to {len(relevant)} relevant CSS rules")

    # Build the inline style block
    css_lines = []
    for selector, body in relevant:
        css_lines.append(f"{selector} {{ {body} }}")
    inline_css = '\n'.join(css_lines)

    # Build output: wrap the HTML snippet with a <style> block
    output = f"""<style>
{inline_css}
</style>
{html}"""

    out_path.write_text(output, encoding='utf-8')
    print(f"Wrote {out_path} ({len(output)} bytes)")


if __name__ == '__main__':
    main()
