"""Package the completed report for XeLaTeX/Overleaf without any student CSVs."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import re

LATEX = Path(__file__).resolve().parents[1]
ROOT = LATEX.parents[1]
archive = LATEX / 'output/oulad_week3_sources.zip'
sources = [p for p in LATEX.rglob('*') if p.is_file() and
           'output' not in p.relative_to(LATEX).parts and '__pycache__' not in p.parts]
text = '\n'.join(p.read_text(encoding='utf-8') for p in LATEX.rglob('*.tex'))
figures = re.findall(r'\\reportfigure(?:\[[^]]*\])?\{([^}]+\.png)\}', text)
with ZipFile(archive, 'w', compression=ZIP_DEFLATED) as bundle:
    for path in sources:
        name = str(path.relative_to(LATEX)).replace('\\', '/')
        if name == 'preamble.tex':
            content = path.read_text(encoding='utf-8').replace(r'\graphicspath{{../figures/}}', r'\graphicspath{{figures/}}')
            bundle.writestr(name, content.encode('utf-8'))
        else:
            bundle.write(path, name)
    for name in sorted(set(figures)):
        bundle.write(ROOT / 'report/figures' / name, 'figures/' + name)
    validation = LATEX / 'output/validation.json'
    if validation.is_file():
        bundle.write(validation, 'output/validation.json')
    bundle.writestr('OVERLEAF.txt', 'Select main.tex and XeLaTeX. Fill metadata.tex before submission.\nTables are already generated; no CSV data is included.\n')
with ZipFile(archive) as bundle:
    assert bundle.testzip() is None
    assert 'main.tex' in bundle.namelist()
    assert not any(name.endswith('.csv') for name in bundle.namelist())
print(f'Source archive: {archive} ({archive.stat().st_size:,} bytes), with {len(set(figures))} figures.')
