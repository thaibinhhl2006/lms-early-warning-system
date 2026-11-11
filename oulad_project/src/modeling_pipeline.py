"""Quy trình dùng chung cho giai đoạn mô hình hóa OULAD (tuần 4).

Module gom các hằng số và hàm đã được xây dựng, kiểm tra trong ``modeling_prep.ipynb`` (Chương 4):

* 4.1 — phương án chia tập theo sinh viên: ``load_week_split``, ``cv_splits``;
* 4.2 — tiền xử lý: ``make_xy``, ``build_preprocessor``;
* 4.3 — danh sách đặc trưng đã chọn: ``load_selected_features``;
* 4.4 — 3 phương án xử lý mất cân bằng: ``build_imbalance_pipeline``;
* 4.5 — tập đặc trưng–nhãn theo mốc: ``load_modeling_data``;
* 4.6 — huấn luyện thử theo 5 fold: ``evaluate_cv``.

Nguyên tắc sử dụng
------------------
* Tập kiểm tra (``part='test'``) chỉ dùng cho lần đánh giá cuối cùng.
* Mọi phép biến đổi học tham số (trung vị của ``late_submission_rate``) và SMOTENC nằm trong pipeline,
  được fit lại trên phần huấn luyện của từng vòng cross-validation.

Ví dụ::

    import sys; sys.path.insert(0, 'src')
    import modeling_pipeline as mp
    train_df = mp.load_modeling_data(8, 'train')
    X, y = mp.make_xy(train_df)
    model = mp.build_imbalance_pipeline('class_weight', estimator=...)
    # cross_validate(model, X, y, cv=mp.cv_splits(train_df), scoring='f1_macro')
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder

# ----------------------------------------------------------------------------- đường dẫn
ROOT = Path(__file__).resolve().parents[1]
PRE_DIR = ROOT / 'data' / 'preprocessed'
MODEL_DATA_DIR = ROOT / 'data' / 'modeling'
FEATURE_MANIFEST_PATH = PRE_DIR / 'feature_manifest.json'
ASSIGN_PATH = PRE_DIR / 'split_assignment.csv'
SELECTION_PATH = PRE_DIR / 'selected_features.json'

# ----------------------------------------------------------------------------- cấu hình chung
STUDENT_KEY = ['code_module', 'code_presentation', 'id_student']
TARGET = 'final_result'
LABELS = ['Pass', 'Withdrawn', 'Fail', 'Distinction']
WEEKS = [4, 8, 12, 16, 24]
SEED = 42
N_FOLDS = 5
STRATEGIES = ['none', 'class_weight', 'smotenc']

# Danh mục cố định theo miền giá trị đã khảo sát ở Chương 2–3 (không học từ dữ liệu huấn luyện).
CATEGORIES = {
    'gender': ['F', 'M'],
    'disability': ['N', 'Y'],
    'region': ['East Anglian Region', 'East Midlands Region', 'Ireland', 'London Region', 'North Region',
               'North Western Region', 'Scotland', 'South East Region', 'South Region', 'South West Region',
               'Wales', 'West Midlands Region', 'Yorkshire Region'],
    'highest_education': ['No Formal quals', 'Lower Than A Level', 'A Level or Equivalent',
                          'HE Qualification', 'Post Graduate Qualification'],
    'age_band': ['0-35', '35-55', '55<='],
    'imd_band': ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-60%', '60-70%', '70-80%',
                 '80-90%', '90-100%', 'Unknown'],
}
ALL_FEATURES = json.loads(FEATURE_MANIFEST_PATH.read_text(encoding='utf-8'))['feature_columns']   # 23 của Chương 3
CAT_COLS = list(CATEGORIES)
IMPUTE_COLS = ['late_submission_rate']
LOG_COLS = ['total_clicks', 'avg_clicks_per_day', 'clicks_oucontent', 'clicks_forumng',
            'clicks_quiz', 'clicks_resource']
PASS_COLS = [c for c in ALL_FEATURES if c not in CAT_COLS + IMPUTE_COLS + LOG_COLS]
LATE_FLAG = 'missingindicator_late_submission_rate'   # tên cột cờ thiếu do SimpleImputer sinh ra

MODEL_DTYPES = {
    'code_module': 'string', 'code_presentation': 'string', 'id_student': 'int64',
    'prediction_week': 'int64', 'cutoff_day': 'int64', 'fold': 'int64', TARGET: 'string',
    **{c: 'string' for c in CAT_COLS}, 'late_submission_rate': 'float64',
}


# ----------------------------------------------------------------------------- dữ liệu
def load_selected_features() -> list[str]:
    """Danh sách đặc trưng chung cho 5 mốc (mục 4.3)."""
    return json.loads(SELECTION_PATH.read_text(encoding='utf-8'))['selected_features']


def load_split_assignment() -> pd.DataFrame:
    """Phương án chia tập ở cấp sinh viên: id_student → split (train/test), fold (1..5)."""
    return pd.read_csv(ASSIGN_PATH, dtype={'id_student': 'int64', 'split': 'string', 'fold': 'Int64'})


def load_week_split(week: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(train_df, test_df) của một mốc từ tệp Chương 3 + phương án chia; train_df có cột fold (1..5)."""
    df = pd.read_csv(PRE_DIR / f'oulad_week{week}.csv')
    df = df.merge(load_split_assignment(), on='id_student', how='left', validate='many_to_one')
    if df['split'].isna().any():
        raise ValueError('Có lượt học chưa được gán tập')
    train_df = df[df['split'] == 'train'].drop(columns='split').reset_index(drop=True)
    test_df = df[df['split'] == 'test'].drop(columns=['split', 'fold']).reset_index(drop=True)
    return train_df, test_df


def modeling_path(week: int, part: str = 'train') -> Path:
    if part not in ('train', 'test'):
        raise ValueError("part phải là 'train' hoặc 'test'")
    return MODEL_DATA_DIR / f'week{week}_{part}.csv'


def load_modeling_data(week: int, part: str = 'train') -> pd.DataFrame:
    """Tập đặc trưng–nhãn đã xuất ở mục 4.5 (chưa biến đổi). part='test' chỉ dùng khi đánh giá cuối cùng."""
    path = modeling_path(week, part)
    dtypes = {k: v for k, v in MODEL_DTYPES.items() if not (part == 'test' and k == 'fold')}
    return pd.read_csv(path, dtype=dtypes)


def cv_splits(train_df: pd.DataFrame) -> list[tuple[np.ndarray, np.ndarray]]:
    """Danh sách (train_idx, val_idx) theo fold đã gán; dùng làm tham số cv= của scikit-learn."""
    folds = train_df['fold'].to_numpy()
    return [(np.flatnonzero(folds != k), np.flatnonzero(folds == k)) for k in range(1, N_FOLDS + 1)]


def make_xy(df: pd.DataFrame, features: list[str] | None = None) -> tuple[pd.DataFrame, pd.Series]:
    """Tách X và y (4 nhãn). Mặc định dùng danh sách đặc trưng đã chọn ở mục 4.3."""
    features = load_selected_features() if features is None else features
    return df[features].copy(), df[TARGET].copy()


# ----------------------------------------------------------------------------- tiền xử lý
def _pick(cols, features):
    return [c for c in cols if c in features]


def build_preprocessor(features: list[str] | None = None) -> ColumnTransformer:
    """Bộ tiền xử lý mục 4.2 (chưa fit): One-Hot, điền trung vị + cờ thiếu, log1p, giữ nguyên phần còn lại."""
    features = load_selected_features() if features is None else features
    cat_cols = _pick(CAT_COLS, features)
    transformers = [
        ('onehot', OneHotEncoder(categories=[CATEGORIES[c] for c in cat_cols], drop='if_binary',
                                 handle_unknown='error', sparse_output=False), cat_cols),
        ('impute', SimpleImputer(strategy='median', add_indicator=True), _pick(IMPUTE_COLS, features)),
        ('log1p', FunctionTransformer(np.log1p, feature_names_out='one-to-one'), _pick(LOG_COLS, features)),
        ('keep', 'passthrough', _pick(PASS_COLS, features)),
    ]
    preprocessor = ColumnTransformer([t for t in transformers if t[2]],
                                     remainder='drop', verbose_feature_names_out=False)
    return preprocessor.set_output(transform='pandas')


def to_float(X):
    """Chuyển cột số sang số thực trước SMOTENC (tránh imblearn cắt phần thập phân của mẫu nội suy)."""
    return X.astype(float)


def build_prepare_step(features: list[str] | None = None) -> ColumnTransformer:
    """Bước 1 của pipeline mục 4.4: điền thiếu + cờ, log1p, số thực; biến phân loại giữ dạng nhãn."""
    features = load_selected_features() if features is None else features
    transformers = [
        ('impute', SimpleImputer(strategy='median', add_indicator=True), _pick(IMPUTE_COLS, features)),
        ('log1p', FunctionTransformer(np.log1p, feature_names_out='one-to-one'), _pick(LOG_COLS, features)),
        ('numeric', FunctionTransformer(to_float, feature_names_out='one-to-one'), _pick(PASS_COLS, features)),
        ('categorical', 'passthrough', _pick(CAT_COLS, features)),
    ]
    ct = ColumnTransformer([t for t in transformers if t[2]], remainder='drop', verbose_feature_names_out=False)
    return ct.set_output(transform='pandas')


def build_encode_step(features: list[str] | None = None) -> ColumnTransformer:
    """Bước One-Hot của pipeline mục 4.4 (danh mục cố định); các cột khác giữ nguyên."""
    features = load_selected_features() if features is None else features
    cat_cols = _pick(CAT_COLS, features)
    ct = ColumnTransformer([
        ('onehot', OneHotEncoder(categories=[CATEGORIES[c] for c in cat_cols], drop='if_binary',
                                 handle_unknown='error', sparse_output=False), cat_cols),
    ], remainder='passthrough', verbose_feature_names_out=False)
    return ct.set_output(transform='pandas')


def evaluate_cv(model, X: pd.DataFrame, y: pd.Series, splits) -> tuple[pd.DataFrame, np.ndarray]:
    """Huấn luyện thử theo các fold đã gán (mục 4.6); chỉ dùng phần huấn luyện.

    Với mỗi vòng: clone model, fit trên phần fit, dự đoán fold validation. Trả về:
    * bảng chỉ số theo vòng (accuracy, macro-F1, balanced accuracy, precision/recall/F1 từng lớp);
    * ma trận nhầm lẫn cộng dồn qua 5 vòng (hàng = nhãn thật, cột = nhãn dự đoán, thứ tự LABELS).
    """
    from sklearn.metrics import (accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score,
                                 precision_recall_fscore_support)
    rows, cm_total = [], np.zeros((len(LABELS), len(LABELS)), dtype=int)
    for k, (tr, va) in enumerate(splits, start=1):
        fitted = clone(model).fit(X.iloc[tr], y.iloc[tr])
        y_true = y.iloc[va].astype(str).to_numpy()
        y_pred = np.asarray(fitted.predict(X.iloc[va])).astype(str)
        p, r, f, _ = precision_recall_fscore_support(y_true, y_pred, labels=LABELS, zero_division=0)
        row = {'fold': k, 'n_fit': len(tr), 'n_val': len(va),
               'accuracy': accuracy_score(y_true, y_pred),
               'f1_macro': f1_score(y_true, y_pred, labels=LABELS, average='macro', zero_division=0),
               'balanced_accuracy': balanced_accuracy_score(y_true, y_pred)}
        for i, lab in enumerate(LABELS):
            row[f'precision_{lab}'], row[f'recall_{lab}'], row[f'f1_{lab}'] = p[i], r[i], f[i]
        rows.append(row)
        cm_total += confusion_matrix(y_true, y_pred, labels=LABELS)
    return pd.DataFrame(rows), cm_total


def build_imbalance_pipeline(strategy: str, estimator=None, features: list[str] | None = None):
    """Pipeline cho một phương án xử lý mất cân bằng (mục 4.4).

    strategy: 'none' | 'class_weight' | 'smotenc'. estimator=None → chỉ gồm các bước tiền xử lý.
    Thứ tự: prepare → [SMOTENC, chỉ khi fit] → One-Hot → mô hình.
    """
    from imblearn.over_sampling import SMOTENC
    from imblearn.pipeline import Pipeline as ImbPipeline

    if strategy not in STRATEGIES:
        raise ValueError(f'strategy phải thuộc {STRATEGIES}')
    features = load_selected_features() if features is None else features
    steps = [('prepare', build_prepare_step(features))]
    if strategy == 'smotenc':
        categorical = _pick(CAT_COLS, features) + ([LATE_FLAG] if 'late_submission_rate' in features else [])
        steps.append(('smotenc', SMOTENC(categorical_features=categorical, k_neighbors=5,
                                         sampling_strategy='not majority', random_state=SEED)))
    steps.append(('encode', build_encode_step(features)))
    if estimator is not None:
        est = clone(estimator)
        if strategy == 'class_weight':
            if 'class_weight' not in est.get_params():
                raise ValueError('Mô hình không có tham số class_weight; cần truyền sample_weight '
                                 '(sklearn.utils.class_weight.compute_sample_weight) khi fit.')
            est.set_params(class_weight='balanced')
        steps.append(('clf', est))
    return ImbPipeline(steps)
