#!/usr/bin/env python3
"""Offline structural checks. No writes, no network, no semantic approval."""
import argparse
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
PERSONAL = {"index", "log", "ThinkDesk"}


def validate(root=ROOT, distribution=False):
    issues = []
    files = [p for p in root.rglob('*') if p.is_file() and '.git' not in p.parts]
    required = ['README.md', 'AGENTS.md', 'Schema.md', 'FIRST-RUN.md', 'LICENSE',
                'NOTICE.md', '.gitignore', 'index.example.md', 'log.example.md',
                'ThinkDesk.example.md', 'Rules/raw-rules.md', 'Rules/ingest-workflow.md']
    for name in required:
        if not (root / name).is_file():
            issues.append('missing: ' + name)
    for p in files:
        if p.is_symlink():
            issues.append('symlink: ' + str(p.relative_to(root)))
        if p.suffix != '.md':
            continue
        text = p.read_text(encoding='utf-8')
        # Inline references inside YAML are real links too. Code fences are examples.
        body = re.sub(r'```.*?```', '', text, flags=re.S)
        for raw in re.findall(r'\[\[([^\]]+)\]\]', body):
            target = raw.split('|')[0].split('#')[0]
            if not target:
                continue
            candidates = [root / target, p.parent / target]
            # A dot can be part of a note name: keep it when appending .md.
            candidates += [x.with_name(x.name + '.md') for x in candidates
                           if x.suffix != '.md']
            if target in PERSONAL:
                candidates.append(root / (target + '.example.md'))
            if not any(x.is_file() for x in candidates):
                issues.append(f'{p.relative_to(root)}: broken wiki link {target}')
        for raw in re.findall(r'\]\(([^)]+)\)', body):
            target = unquote(raw.strip('<>').split('#')[0])
            if not target or re.match(r'^[a-zA-Z][\w+.-]*:', target):
                continue
            if not (p.parent / target).exists():
                issues.append(f'{p.relative_to(root)}: broken Markdown link {target}')
    skills = list((root / '.agents/skills').glob('*/SKILL.md'))
    if len(skills) != 4:
        issues.append(f'expected 4 skills, got {len(skills)}')
    for p in skills:
        t = p.read_text(encoding='utf-8')
        if not t.startswith('---\n') or not re.search(r'^name: ' + re.escape(p.parent.name) + r'$', t, re.M):
            issues.append(f'invalid skill identity: {p.parent.name}')
        for field in ['description:']:
            if field not in t:
                issues.append(f'missing skill field: {p.parent.name}/{field}')
        if not (p.parent / 'agents/openai.yaml').is_file():
            issues.append(f'missing UI metadata: {p.parent.name}')
    if distribution:
        for p in files:
            rel = p.relative_to(root)
            if rel.parts[0] in {'Raw', 'Wiki'} and p.name != '.gitkeep':
                issues.append('private knowledge in distribution: ' + str(rel))
            if rel.name in {'.env', '.DS_Store'} or '__pycache__' in rel.parts:
                issues.append('runtime file in distribution: ' + str(rel))
        for name in ['USER-CONTEXT.md', 'index.md', 'log.md', 'ThinkDesk.md', '.obsidian', '.codex', '.git']:
            if (root / name).exists():
                issues.append('private/runtime path in distribution: ' + name)
    return issues


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--distribution', action='store_true', help='require an empty public template')
    args = parser.parse_args()
    problems = validate(distribution=args.distribution)
    for issue in problems:
        print('ERROR:', issue)
    print(f'structural_issues={len(problems)}; semantic_review=not_performed')
    raise SystemExit(bool(problems))
