"""Validate local LaTeX sources and evidence without claiming a successful TeX build."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

import pandas as pd
from PIL import Image

LATEX = Path(__file__).resolve().parents[1]
ROOT = LATEX.parents[1]
OUTPUT = LATEX / 'output'
OUTPUT.mkdir(exist_ok=True)
tex_files = sorted(LATEX.rglob('*.tex'))
assert tex_files
texts = {p: p.read_text(encoding='utf-8') for p in tex_files}
combined = '\n'.join(texts.values())


def without_comments(source: str) -> str:
    return '\n'.join(re.split(r'(?<!\\)%', line, maxsplit=1)[0] for line in source.splitlines())


for file, source in texts.items():
    cleaned = without_comments(source)
    depth = 0
    for token in re.finditer(r'\\[{}]|[{}]', cleaned):
        if token.group().startswith('\\'):
            continue
        depth += 1 if token.group() == '{' else -1
        assert depth >= 0, f'Closing brace mismatch: {file}'
    assert depth == 0, f'Unbalanced braces: {file}'
    environments: list[str] = []
    for token in re.finditer(r'\\(begin|end)\{([^}]+)\}', cleaned):
        direction, name = token.groups()
        if direction == 'begin':
            environments.append(name)
        else:
            assert environments and environments.pop() == name, f'Environment mismatch: {file}, {name}'
    assert not environments, file

inputs = re.findall(r'\\input\{([^}]+)\}', combined)
for item in inputs:
    target = LATEX / (item if item.endswith('.tex') else item + '.tex')
    assert target.is_file(), target
labels = [label for label in re.findall(r'\\label\{([^}]+)\}', combined) if not label.startswith('#')]
labels += re.findall(r'\\reportfigure(?:\[[^]]*\])?\{[^}]*\}\{.*?\}\{(fig:[^}]+)\}', combined, re.S)
assert len(labels) == len(set(labels)), 'Duplicate labels'
references = re.findall(r'\\(?:ref|pageref|autoref)\{([^}]+)\}', combined)
assert set(references) <= set(labels), set(references) - set(labels)
unused_labels = sorted(set(labels) - set(references))
figure_names = re.findall(r'\\reportfigure(?:\[[^]]*\])?\{([^}]+\.png)\}', combined)
assert len(figure_names) == len(set(figure_names)) == 9
image_evidence = []
for name in figure_names:
    path = ROOT / 'report/figures' / name
    assert path.is_file(), path
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        image_evidence.append({'file': name, 'pixels': list(image.size)})
cite_keys = {k.strip() for group in re.findall(r'\\(?:auto|text)?cite\{([^}]+)\}', combined) for k in group.split(',')}
bib = (LATEX / 'references.bib').read_text(encoding='utf-8')
bib_keys = set(re.findall(r'@\w+\{([^,]+),', bib))
assert cite_keys == bib_keys, {'missing': sorted(cite_keys - bib_keys), 'unused': sorted(bib_keys - cite_keys)}
macro_definitions = set(re.findall(r'\\newcommand\{\\([A-Za-z]+)\}', combined))
metric_prefixes = ('NStudents', 'NEnroll', 'NVle', 'NTotal', 'NRaw', 'NPass', 'NFail', 'NWithdraw',
                   'NDistinction', 'NExact', 'NDomain', 'NRelation', 'NState', 'NPrecourse', 'NImd',
                   'NUnknown', 'NWhitespace', 'NBase', 'NWeek', 'NMerge', 'NMissing', 'NFinal',
                   'NFuture', 'NLate', 'NClicks', 'Pct', 'Click', 'Score', 'Weekly', 'WeekEight',
                   'WeekFour', 'WeekTwenty', 'RawSize', 'ContentClick', 'ForumClick', 'QuizClick', 'Resource')
used_metrics = {command for command in re.findall(r'\\([A-Za-z]+)', combined) if command.startswith(metric_prefixes)}
assert used_metrics <= macro_definitions, used_metrics - macro_definitions

manifest = json.loads((LATEX / 'source_manifest.json').read_text(encoding='utf-8'))
source_checks = {}
for record in manifest['sources']:
    path = ROOT / record['path']
    with path.open('rb') as handle:
        digest = hashlib.file_digest(handle, 'sha256').hexdigest()
    source_checks[record['path']] = digest == record['sha256']
assert all(source_checks.values())
assert manifest['unique_students'] == 28785 and manifest['feature_count'] == 23
integrated = pd.read_csv(ROOT / 'report/tables/3_5_4_integration_summary.csv')
assert integrated.iloc[:, 2].tolist() == [27528, 26516, 25722, 24932, 23562]
assert integrated.iloc[:, 3].eq(29).all() and integrated.iloc[:, 4].eq(23).all()
appendix = (LATEX / 'generated/features_rows.tex').read_text(encoding='utf-8')
assert sum(line.endswith(r'\\') for line in appendix.splitlines()) == 23
chapter2 = (LATEX / 'sections/chapter2.tex').read_text(encoding='utf-8')
chapter3 = (LATEX / 'sections/chapter3.tex').read_text(encoding='utf-8')
assert len(re.findall(r'\\section\{', chapter2)) == 4
assert len(re.findall(r'\\section\{', chapter3)) == 6
assert r'\setcounter{chapter}{1}' in (LATEX / 'main.tex').read_text(encoding='utf-8')

# Check preservation against the preceding notebook task, when its local audit exists.
prior_state = ROOT / 'tmp/postprocess_survey_before.json'
preservation_checks = {}
if prior_state.is_file():
    prior = json.loads(prior_state.read_text(encoding='utf-8'))
    for relative, expected in prior['protected_hashes'].items():
        path = ROOT.parent / relative
        with path.open('rb') as handle:
            preservation_checks[relative] = hashlib.file_digest(handle, 'sha256').hexdigest() == expected
    for relative, expected in prior['raw_stats'].items():
        path = ROOT / relative
        preservation_checks[relative] = {'size': path.stat().st_size, 'mtime_ns': path.stat().st_mtime_ns} == expected
    assert all(preservation_checks.values())

log = OUTPUT / 'main.log'
log_checks = None
if log.is_file():
    log_text = log.read_text(encoding='utf-8', errors='replace')
    patterns = {'tex_error': r'^! ', 'overfull_box': r'Overfull \\[hv]box',
                'missing_glyph': r'Missing character:', 'undefined_reference': r'(?:Reference|Citation).*undefined|There were undefined references'}
    log_checks = {name: not bool(re.search(pattern, log_text, re.M)) for name, pattern in patterns.items()}
    assert all(log_checks.values()), log_checks
result = {'status': 'passed_static_checks', 'tex_files_checked': len(tex_files),
          'figure_files_checked': image_evidence, 'figures_total_including_tikz': 10,
          'tables_including_appendix': len([label for label in labels if label.startswith('tab:')]),
          'labels': len(labels), 'unreferenced_labels': unused_labels,
          'bibliography_entries_used': sorted(cite_keys), 'source_hash_checks': source_checks,
          'preservation_checks': preservation_checks, 'xelatex_available': shutil.which('xelatex') is not None,
          'pdf_exists': (OUTPUT / 'main.pdf').is_file(), 'tex_log_checks': log_checks,
          'pdf_visual_inspection': ('Pending: compiled PDF needs visual inspection.' if (OUTPUT / 'main.pdf').is_file()
                                    else 'Pending: no locally compiled PDF is available.')}
(OUTPUT / 'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in result.items() if k not in ['source_hash_checks', 'preservation_checks', 'figure_files_checked']}, ensure_ascii=False, indent=2))
