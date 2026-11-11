# Dữ liệu cho mô hình hóa (tuần 4)

Được tạo bởi `modeling_prep.ipynb` (mục 4.5). Không chỉnh sửa thủ công; chạy lại notebook nếu cần tạo lại.

| Tệp | Nội dung |
| --- | --- |
| `week{N}_train.csv` | Phần huấn luyện tại mốc tuần N (N = 4, 8, 12, 16, 24); cột `fold` = 1..5 cho cross-validation |
| `week{N}_test.csv` | Tập kiểm tra tại mốc tuần N — **chỉ dùng cho lần đánh giá cuối cùng** |
| `modeling_manifest.json` | Cấu hình, kiểu dữ liệu, phiên bản thư viện, số dòng và SHA-256 của từng tệp |

- Mỗi dòng là một lượt học (`code_module`, `code_presentation`, `id_student`); nhãn `final_result` gồm 4 lớp.
- 20 đặc trưng ở dạng **giá trị gốc, chưa biến đổi**. Điền thiếu, log1p, One-Hot và SMOTENC
  nằm trong pipeline của `src/modeling_pipeline.py` và phải được fit lại trong từng vòng cross-validation.
- Một sinh viên chỉ thuộc tập huấn luyện hoặc tập kiểm tra, và chỉ thuộc một fold, ở cả 5 mốc.

```python
import sys; sys.path.insert(0, 'src')          # chạy từ thư mục oulad_project/
import modeling_pipeline as mp
from sklearn.model_selection import cross_validate

train_df = mp.load_modeling_data(8, 'train')
X, y = mp.make_xy(train_df)
model = mp.build_imbalance_pipeline('class_weight', estimator=...)   # 'none' | 'class_weight' | 'smotenc'
scores = cross_validate(model, X, y, cv=mp.cv_splits(train_df), scoring=['f1_macro', 'balanced_accuracy'])
```

Cần các thư viện: pandas, numpy, scikit-learn 1.6.1, imbalanced-learn 0.13.0.
