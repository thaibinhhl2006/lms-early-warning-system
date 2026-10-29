# OULAD — Data Exploration & Preprocessing

## Cấu trúc

- `data/raw/`: 7 file CSV nguyên gốc (không chỉnh sửa).
- `data/preprocessed/`: đầu ra trung gian và dữ liệu tích hợp sau khi chạy notebook.
- `preprocess.ipynb`: Phần 2 (khám phá, đánh giá) và Phần 3 (tiền xử lý, tích hợp).
- `modeling.ipynb`: khung huấn luyện và đánh giá mô hình (chưa triển khai).
- `models/`, `report/`, `tmp/`: đầu ra mô hình, báo cáo và tệp tạm.

## Cách sử dụng

### 1. Cài đặt và mở notebook trên Windows

Mở PowerShell và chạy lần lượt (cần Python đã được cài):

```powershell
cd C:\Users\Admin\Downloads\OULAD_project_skeleton\oulad_project
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m jupyterlab
```

Giữ cửa sổ PowerShell đang chạy. Trong trang JupyterLab mở trên trình duyệt, nhấp đúp `preprocess.ipynb` và chọn kernel Python của môi trường `.venv` nếu được hỏi. Dùng `Shift+Enter` để chạy ô hiện tại rồi chuyển sang ô tiếp theo. Ô Markdown là hướng dẫn; ô Code là mã thực thi. Dấu `[*]` cạnh ô nghĩa là mã đang chạy, hãy chờ trước khi chạy tiếp.

Nếu dùng VS Code, mở thư mục `oulad_project`, cài extension Python và Jupyter, mở notebook rồi chọn **Select Kernel → Python Environments → .venv**.

### 2. Khám phá dữ liệu — Phần 2

Chạy ô thiết lập thư viện đầu tiên, sau đó chạy lần lượt các mục:

| Mục | Nội dung sử dụng | Kết quả cần đọc |
| --- | --- | --- |
| 2.1 | Quy mô 7 bảng | `table_stats_df`: số dòng, số cột, dung lượng |
| 2.2 | Kiểu dữ liệu, khóa và miền giá trị | Kiểu của từng cột, kiểm tra khóa, các nhóm giá trị |
| 2.3 | Phân phối dữ liệu | Biểu đồ kết quả học tập, điểm và số click trên mẫu |
| 2.4 | Chất lượng dữ liệu | `missing_df`, `duplicate_df`, số điểm ngoài khoảng 0–100 |
| 2.5 | Tổng hợp nhận xét | Điền `TODO` từ các số liệu thực tế ở trên |

Để xem thêm dữ liệu, chèn ô Code sau ô thiết lập, ví dụ:

```python
display(tables['studentInfo'].head())
display(tables['studentInfo'].describe(include='all'))
display(tables['studentInfo'].isna().sum())
display(vle_sample.head())
```

`tables` chứa 6 bảng nhỏ; `vle_sample` chỉ gồm 100.000 dòng đầu của `studentVle`, không phải mẫu ngẫu nhiên đại diện. Các ô đếm dòng, kiểm tra thiếu và tổng hợp VLE đọc toàn bộ file theo từng khối, có thể cần chờ lâu hơn các ô khác.

### 3. Tiền xử lý và tích hợp — Phần 3

1. Ở mục 3.1, đặt `PREDICTION_DAY = 28` và `WINDOW_START_DAY = 0` nếu muốn tổng hợp hoạt động từ ngày 0 đến hết ngày 28, bao gồm hai đầu mút. Thay mốc nếu bài toán yêu cầu.
2. Chạy mục 3.2 để tạo các bản sao `cleaned`. Mã hiện tại giữ nguyên giá trị thiếu; các phương án điền thiếu còn là gợi ý trong `TODO` hoặc chú thích. Chỉ sửa sau khi đánh giá ý nghĩa từng cột.
3. Đọc và hoàn thiện mục 3.3–3.4 nếu phát hiện dữ liệu cần xử lý. Hai mục này hiện chủ yếu là hướng dẫn, chưa tự xóa dòng, sửa ngoại lai hay đổi kiểu dữ liệu.
4. Chạy tuần tự tất cả các ô của mục 3.5: tạo bảng nền → đếm bài đã nộp trong cửa sổ → tổng hợp click VLE → ghép thành `integrated`. Mỗi dòng ứng với một sinh viên trong một học phần và đợt mở lớp.
5. Chạy mục 3.6 để lưu CSV. Với mốc 28, các tệp gồm:

| Tệp trong `data/preprocessed/` | Nội dung |
| --- | --- |
| `assessment_features_t028.csv` | Số bài nộp theo lượt học trong cửa sổ |
| `vle_features_t028.csv` | Tổng click và click theo loại hoạt động |
| `oulad_integrated_t028.csv` | Bảng nền ghép với hai nhóm đặc trưng |

Kiểm tra nhanh sau khi chạy:

```python
print(integrated.shape)
display(integrated.head())
display(integrated.isna().sum())
assert not integrated.duplicated(STUDENT_KEY).any()
assert len(integrated) == len(base)
```

Nếu đổi mốc ngày, chạy lại từ mục 3.1 đến hết 3.6. Nếu sửa các ô khám phá hoặc quy tắc xử lý, dùng **Kernel → Restart Kernel and Run All Cells** để kiểm tra toàn bộ luồng từ đầu. Tệp đầu ra có cùng mốc ngày sẽ được ghi đè khi chạy lại; dữ liệu thô được giữ nguyên.

### 4. Lỗi thường gặp và phạm vi kết quả

- `ModuleNotFoundError`: chọn lại kernel `.venv` và cài đủ `requirements.txt` bằng Python của môi trường đó.
- `FileNotFoundError`: chạy `print(Path.cwd())` trong notebook; thư mục làm việc phải là `oulad_project`, có thư mục con `data/raw` chứa đủ 7 CSV.
- `NameError`: một ô phụ thuộc chưa được chạy; chạy lại tuần tự từ ô thiết lập.
- `AssertionError` hoặc `ValueError` khi ghép bảng: đọc thông báo và kiểm tra khóa/dữ liệu liên quan trước khi tiếp tục.

Notebook là khung phân tích có thể chạy phần mã hiện có, chưa phải quy trình làm sạch hoàn chỉnh. Các bảng tổng hợp và CSV được tạo bằng mã; nhiều phần nhận xét, biểu đồ bổ sung, kiểm tra chất lượng và quyết định xử lý vẫn cần hoàn thiện tại `TODO`. `modeling.ipynb` hiện chỉ là khung, chưa huấn luyện mô hình.

Bảng tích hợp vẫn chứa nhãn `final_result` và các cột đăng ký, bao gồm `date_unregistration`; không đưa tất cả các cột vào mô hình tự động. Cần chọn đặc trưng đã biết tại mốc dự đoán và chia train/test trước khi fit phép điền thiếu, mã hóa hoặc chuẩn hóa có học tham số.

## Lưu ý phân tích

- Không chỉnh sửa file CSV gốc. Giữ riêng dữ liệu thô và dữ liệu xử lý.
- Các cột `date` là số ngày tương đối tính từ ngày bắt đầu học phần, không phải ngày lịch.
- `date_unregistration` trống có ý nghĩa nghiệp vụ; không tự động điền bằng 0.
- Điểm `score` có thể chưa sẵn có tại mốc dự đoán; khung tích hợp không đưa điểm vào đặc trưng mặc định.
- `studentVle` rất lớn: notebook đọc theo chunks để tổng hợp rồi mới JOIN, tránh nhân số dòng.
- Chỉ các phép tiền xử lý không học tham số từ tập dữ liệu mới có thể được làm độc lập trước chia tập; median imputation, scaling và feature selection phải fit trên train.

Khung notebook được xây dựng theo đề cương Phần 2 và 3 đã thống nhất, không phải kết quả nghiên cứu hoàn chỉnh.
