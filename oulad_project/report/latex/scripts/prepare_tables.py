"""Generate selected report tables and numerical macros from existing OULAD outputs.

Read-only with respect to the notebook, raw data and preprocessed data.
Run from any working directory with the project's Python environment.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pandas as pd

LATEX = Path(__file__).resolve().parents[1]
ROOT = LATEX.parents[1]
GENERATED = LATEX / 'generated'
GENERATED.mkdir(parents=True, exist_ok=True)
SOURCES: set[Path] = set()


def load(stem: str) -> pd.DataFrame:
    path = ROOT / 'report/tables' / f'{stem}.csv'
    SOURCES.add(path)
    return pd.read_csv(path)


def text(value: object) -> str:
    replacements = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
                    '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
                    '^': r'\textasciicircum{}'}
    return ''.join(replacements.get(c, c) for c in str(value))


def code(value: object) -> str:
    return r'\code{' + str(value) + '}'


def number(value: object, decimals: int = 0) -> str:
    return r'\num{' + f'{float(value):.{decimals}f}' + '}'


def table(stem: str, specification: str, headers: list[str], rows: list[list[str]]) -> None:
    assert all(len(row) == len(headers) for row in rows), stem
    stretchy = 'Y' in specification or 'X' in specification
    environment = 'tabularx' if stretchy else 'tabular'
    opening = r'\begin{tabularx}{\linewidth}{' if stretchy else r'\begin{tabular}{'
    lines = [f'% Generated from project outputs; see source_manifest.json.',
             opening + specification + '}', r'\toprule',
             ' & '.join(r'\textbf{' + h + '}' for h in headers) + r' \\', r'\midrule']
    lines += [' & '.join(row) + r' \\' for row in rows]
    lines += [r'\bottomrule', r'\end{' + environment + '}', '']
    (GENERATED / f'{stem}.tex').write_text('\n'.join(lines), encoding='utf-8')


metrics: dict[str, str] = {}


def metric(name: str, value: object, decimals: int = 0, percent: bool = False) -> None:
    metrics[name] = number(value, decimals) + (r'\,\%' if percent else '')


sizes = load('2_1_1_table_size')
table('dataset', '@{}lrrY@{}', ['Bảng', 'Bản ghi', 'Cột', 'Nội dung'], [
    [code(row.iloc[0]) if row.iloc[0] != 'Tổng' else r'\textbf{Tổng}',
     number(row.iloc[2]), number(row.iloc[3]), text(row.iloc[1])]
    for _, row in sizes.iterrows()])
info_path = ROOT / 'data/raw/studentInfo.csv'
SOURCES.add(info_path)
unique_students = pd.read_csv(info_path, usecols=['id_student'])['id_student'].nunique()
metric('NStudents', unique_students)
metric('NEnrollments', sizes.loc[sizes.iloc[:, 0].eq('studentInfo')].iloc[0, 2])
metric('NVleRecords', sizes.loc[sizes.iloc[:, 0].eq('studentVle')].iloc[0, 2])
metric('NTotalRecords', sizes.iloc[-1, 2])
metric('NRawColumns', sizes.iloc[-1, 3])
metric('RawSizeMiB', sizes.iloc[-1, 4], 2)
load('2_1_2_key_catalog')
schema_sizes = [len(load('2_2_1_schema_' + name)) for name in sizes.iloc[:-1, 0]]
assert sum(schema_sizes) == int(sizes.iloc[-1, 3]) == 43

target = load('2_2_2_final_result')
for _, row in target.iterrows():
    metric('N' + row.iloc[0], row.iloc[1])
    metric('Pct' + row.iloc[0], row.iloc[2], 2, True)

demographics = load('2_2_3_demographics')
for name, field, category in [('PctMale', 'gender', 'M'), ('PctYoung', 'age_band', '0-35'),
                               ('PctALevel', 'highest_education', 'A Level or Equivalent'),
                               ('PctLowerALevel', 'highest_education', 'Lower Than A Level')]:
    row = demographics.loc[demographics.iloc[:, 0].eq(field) & demographics.iloc[:, 1].eq(category)].iloc[0]
    metric(name, row.iloc[3], 2, True)

score = load('2_2_4_score_summary').iloc[0]
metric('ScoreMedian', score['Trung vị'])
metric('ScoreMean', score['Trung bình'], 2)
score_types = load('2_2_4_score_by_type')
for _, row in score_types.iterrows():
    metric('ScoreMean' + row.iloc[0], row['Điểm trung bình'], 2)
clicks = load('2_2_5_click_summary').iloc[0]
metric('ClickMedian', clicks['Trung vị'])
metric('ClickMean', clicks['Trung bình'], 2)
metric('ClickMax', clicks['Lớn nhất'])
metric('ClickPninetyfive', clicks['P95'])
activity = load('2_2_5_activity_type')
metric('NClicks', activity['Tổng số click'].sum())
for name, kind, column in [('ContentClickPct', 'oucontent', 'Tỷ lệ click (%)'),
                            ('ForumClickPct', 'forumng', 'Tỷ lệ click (%)'),
                            ('QuizClickPct', 'quiz', 'Tỷ lệ click (%)'),
                            ('ResourceClickPct', 'resource', 'Tỷ lệ click (%)'),
                            ('ResourceAssetPct', 'resource', 'Tỷ lệ tài nguyên (%)')]:
    metric(name, activity.loc[activity.iloc[:, 0].eq(kind), column].iloc[0], 2, True)
weekly = load('2_2_5_vle_weekly_trend')
peak = weekly.loc[weekly.iloc[:, 0].ge(1)].sort_values('Tổng số click', ascending=False).iloc[0]
metric('WeeklyPeak', peak.iloc[0])
metric('WeeklyPeakClicks', peak['Tổng số click'])

missing = load('2_3_1_missing_all_columns')
missing = missing.loc[missing['Số giá trị thiếu'].gt(0)]
table('missing_raw', '@{}p{.54\linewidth}rr@{}', ['Thuộc tính', 'Số thiếu', 'Tỷ lệ (\%)'], [
    [code(row.iloc[0]) + r'\newline ' + code(row.iloc[1]), number(row.iloc[3]), number(row.iloc[4], 2)]
    for _, row in missing.iterrows()])
outliers = load('2_3_3_iqr_outliers')
table('outliers', '@{}Yrrr@{}', ['Thuộc tính', 'Ngưỡng dưới', 'Ngưỡng trên', 'Số ngoài ngưỡng'], [
    [code(row['Cột dữ liệu']), number(row['Ngưỡng dưới'], 1), number(row['Ngưỡng trên'], 1),
     number(row['Số giá trị dưới ngưỡng'] + row['Số giá trị trên ngưỡng'])]
    for _, row in outliers.iterrows()])
duplicates = load('2_3_2_exact_duplicates')
dup = duplicates.loc[duplicates.iloc[:, 0].eq('studentVle')].iloc[0]
metric('NExactDuplicates', dup['Số bản ghi trùng lặp dư'])
metric('PctExactDuplicates', dup['Tỷ lệ bản ghi trùng lặp dư (%)'], 2, True)
invalid = load('2_3_3_invalid_values')
metric('NDomainRules', len(invalid))
assert invalid['Số lượt vi phạm'].sum() == 0
relations = load('2_3_4_referential_integrity')
metric('NRelationChecks', len(relations))
assert relations['Số bản ghi không liên kết được'].sum() == 0
load('2_3_2_key_checks')
load('2_3_1_assessment_date_context')
context = load('2_3_4_consistency_context')
for name, index in [('NStateMismatch', 1), ('NWithdrawalMissingDate', 2), ('NPrecourseLogs', 6)]:
    metric(name, context.iloc[index, 1])
metric('PctPrecourseLogs', context.iloc[6, 3], 2, True)
load('2_3_4_weights_by_course')

config = load('3_1_2_prediction_config')
table('cutoffs', '@{}rrr@{}', ['Mốc (tuần)', 'Ngày bắt đầu', 'Ngày chốt dữ liệu'], [
    [number(row.iloc[0]), number(row.iloc[1]), number(row.iloc[2])] for _, row in config.iterrows()])
load('3_1_3_processing_plan')
after = load('3_2_4_missing_before_after')
decisions = {
    'imd_band': ('Gán Unknown; thêm cờ thiếu.', 'Không còn NA; giữ nguyên lượt học.'),
    'date_registration': ('Giữ NA trong bảng cơ sở.', 'Loại khỏi nhóm dự đoán ở cả năm mốc.'),
    'date_unregistration': ('Giữ NA; giả định chưa ghi nhận rút.', 'Vẫn xét chọn nếu đăng ký hợp lệ; không xác nhận trạng thái thực tế.'),
    'score': ('Giữ NA; không dùng điểm trong X.', 'Không điền điểm 0 hoặc trung vị.'),
    'date': ('Giữ NA; không suy diễn hạn nộp.', 'Không xét tỷ lệ muộn nếu thiếu hạn; Exam không thuộc nhóm bài nộp dùng cho X.'),
    'week_from': ('Giữ NA.', 'Dùng ngày tương tác thực tế để tổng hợp.'),
    'week_to': ('Giữ NA.', 'Dùng ngày tương tác thực tế để tổng hợp.'),
}
table('missing_actions', '@{}p{.24\linewidth}rp{.27\linewidth}Y@{}',
      ['Thuộc tính', 'Số thiếu', 'Quyết định', 'Kết quả / cách sử dụng'], [
          [code(row.iloc[1]), number(row.iloc[2]), text(decisions[row.iloc[1]][0]), text(decisions[row.iloc[1]][1])]
          for _, row in after.iterrows()])
metric('NImdUnknown', after.loc[after.iloc[:, 1].eq('imd_band')].iloc[0, 2])
metric('NUnknownRegistration', after.loc[after.iloc[:, 1].eq('date_registration')].iloc[0, 2])
normalization = load('3_4_2_label_normalization')
metric('NImdLabels', normalization.iloc[1, 1])
metric('NWhitespaceChanges', normalization.iloc[0, 1])
load('3_4_1_dtype_audit')
load('3_3_1_duplicates_treatment')
load('3_3_2_invalid_treatment')
load('3_3_3_outlier_treatment')
base = load('3_5_1_student_base').iloc[0]
metric('NBaseColumns', base['Số cột'])
cohorts = load('3_5_1_prediction_cohorts')
integrated = load('3_5_4_integration_summary')
table('integrated', '@{}rrrrrr@{}', ['Mốc (tuần)', 'Ngày chốt', 'Lượt học', 'Số cột', 'Cột X', 'Trùng khóa'], [
    [number(row.iloc[i]) for i in range(6)] for _, row in integrated.iterrows()])
for week, word in [(4, 'Four'), (8, 'Eight'), (24, 'TwentyFour')]:
    row = cohorts.loc[cohorts.iloc[:, 0].eq(week)].iloc[0]
    metric('NWeek' + word, row.iloc[3])
    metric('NWithdrawnByWeek' + word, row.iloc[6])
metric('NLateRegistrationWeekFour', cohorts.iloc[0, 5])
load('3_5_2_assessment_features')
load('3_5_2_assessment_exclusions')
load('3_5_3_vle_features')
merge = load('3_5_5_merge_audit')
metric('NMergeChecks', len(merge))
assert merge['Số bản ghi trước'].equals(merge['Số bản ghi sau'])
missing_features = load('3_5_5_missing_features')
metric('NMissingLateRateWeekEight', missing_features.iloc[1, 2])
metric('PctMissingLateRateWeekEight', missing_features.iloc[1, 3], 2, True)
quality = load('3_6_1_quality_checks')
future = load('3_6_1_future_invariance')
assert quality.iloc[:, 1:].all(axis=None) and future.iloc[:, 1:].all(axis=None)
metric('NFinalChecks', quality.iloc[:, 1:].size)
metric('NFutureChecks', future.iloc[:, 1:].size)
load('3_6_2_before_after')
load('3_6_2_processing_changes')
zero = load('3_6_3_zero_submissions')
table('zero_submissions', '@{}rrrr@{}', ['Mốc (tuần)', 'Lượt học được chọn', 'Chưa có bài nộp', 'Tỷ lệ (\%)'], [
    [number(row.iloc[0]), number(row.iloc[1]), number(row.iloc[2]), number(row.iloc[3], 2)]
    for _, row in zero.iterrows()])
metric('PctZeroSubWeekFour', zero.iloc[0, 3], 2, True)
metric('PctZeroSubWeekTwentyFour', zero.iloc[-1, 3], 2, True)
daily = {}
week8 = None
for week in [4, 8, 12, 16, 24]:
    path = ROOT / 'data/preprocessed' / f'oulad_week{week}.csv'
    SOURCES.add(path)
    frame = pd.read_csv(path, usecols=['total_clicks', 'active_days', 'avg_clicks_per_day'])
    daily[week] = frame['avg_clicks_per_day'].median()
    assert len(frame) == integrated.loc[integrated.iloc[:, 0].eq(week)].iloc[0, 2]
    if week == 8:
        week8 = frame
assert week8 is not None and week8['active_days'].between(0, 56).all()
metric('WeekEightClickMedian', week8['total_clicks'].median())
metric('WeekEightClickPninetyfive', week8['total_clicks'].quantile(.95))
metric('WeekEightClickSkew', week8['total_clicks'].skew(), 2)
metric('WeekEightActiveMedian', week8['active_days'].median())
metric('WeekEightActiveMax', week8['active_days'].max())
metric('WeekEightInactivePct', week8['active_days'].eq(0).mean() * 100, 2, True)
metric('WeekFourDailyMedian', daily[4], 2)
metric('WeekTwentyFourDailyMedian', daily[24], 2)
exports = load('3_6_4_exports')
table('exports', '@{}Yrr@{}', ['Tệp CSV', 'Lượt học', 'Số cột'], [
    [code(Path(row.iloc[0]).name), number(row.iloc[1]), number(row.iloc[2])] for _, row in exports.iterrows()])
dictionary = load('3_5_4_feature_dictionary')
assert len(dictionary) == 23
original_fields = {'gender', 'region', 'highest_education', 'age_band', 'num_of_prev_attempts',
                   'studied_credits', 'disability', 'date_registration', 'module_presentation_length'}
appendix_rows = []
for _, row in dictionary.iterrows():
    name = row.iloc[0]
    source = 'studentInfo' if name in original_fields | {'imd_band', 'imd_band_missing'} else str(row.iloc[1])
    if name == 'date_registration':
        source = 'studentRegistration'
    if name == 'module_presentation_length':
        source = 'courses'
    description = str(row.iloc[2]).replace('0..cutoff', 'ngày 0 đến ngày chốt').replace('<= cutoff', 'không sau ngày chốt').replace('cutoff', 'ngày chốt')
    description = description.replace('NA nếu mẫu số 0', 'để thiếu nếu mẫu số bằng 0')
    if name in original_fields:
        kind = 'Thuộc tính gốc. '
    elif name == 'imd_band':
        kind = 'Chuẩn hóa nhãn. '
    elif name == 'imd_band_missing':
        kind = 'Cờ mới. '
    else:
        kind = 'Tổng hợp mới. '
    source_tex = ' + '.join(code(part.strip()) for part in source.split('+'))
    appendix_rows.append(code(name) + ' & ' + source_tex + ' & ' + text(kind + description) + r' \\')
(GENERATED / 'features_rows.tex').write_text('\n'.join(appendix_rows) + '\n', encoding='utf-8')
(GENERATED / 'metrics.tex').write_text('% Calculated from existing project data.\n' + '\n'.join(
    r'\newcommand{' + chr(92) + name + '}{' + value + '}' for name, value in metrics.items()) + '\n', encoding='utf-8')

manifest_path = ROOT / 'data/preprocessed/feature_manifest.json'
SOURCES.update({manifest_path, ROOT / 'preprocess.ipynb'})
tex_sources = '\n'.join(p.read_text(encoding='utf-8') for p in (LATEX / 'sections').glob('*.tex'))
for figure_name in re.findall(r'\\reportfigure(?:\[[^]]*\])?\{([^}]+\.png)\}', tex_sources):
    SOURCES.add(ROOT / 'report/figures' / figure_name)
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
assert manifest['feature_columns'] == dictionary.iloc[:, 0].tolist()
records = []
for path in sorted(SOURCES):
    with path.open('rb') as handle:
        sha = hashlib.file_digest(handle, 'sha256').hexdigest()
    records.append({'path': str(path.relative_to(ROOT)).replace('\\', '/'), 'sha256': sha,
                    'bytes': path.stat().st_size})
(LATEX / 'source_manifest.json').write_text(json.dumps({'sources': records,
    'unique_students': int(unique_students), 'feature_count': 23,
    'median_daily_clicks': {str(w): float(v) for w, v in daily.items()}},
    ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Generated 8 selected tables, feature appendix and {len(metrics)} numerical macros.')
print(f'Checked {len(records)} source files; no source file was modified.')
