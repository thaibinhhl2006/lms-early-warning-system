# Báo cáo tiến độ tuần 3 — OULAD

Bộ mã nguồn hoàn chỉnh dùng XeLaTeX, gồm bìa riêng, mục lục tự động, Chương 2 (2.1–2.4), Chương 3 (3.1–3.6), kết quả và kế hoạch, tài liệu tham khảo và phụ lục 23 đặc trưng.

## Trạng thái bàn giao

- Nội dung được viết từ notebook và kết quả thực tế của chính dự án.
- Đã đọc đủ 7 trang `../../latex/ProjectI_W2_Report.pdf` để tham khảo cách trình bày; không lấy nội dung, thông tin cá nhân, danh sách tài liệu hay phương án xử lý từ báo cáo đó.
- Môi trường tạo báo cáo chưa có XeLaTeX/Biber. Vì vậy chưa có PDF được biên dịch, chưa thể xác nhận số trang, ngắt trang thực tế, font khi biên dịch hoặc cảnh báo tràn lề của TeX. Không có PDF giả lập thay thế.
- Có kiểm tra tĩnh mã nguồn, dữ liệu bảng, tham chiếu, đường dẫn hình và dấu vết nguồn. Kết quả ở `output/validation.json` sau khi chạy script kiểm tra.
- Không chỉnh sửa notebook, CSV nguồn, dữ liệu theo tuần hoặc hình đã xuất. Không chia tập, mã hóa hay huấn luyện mô hình.

## Các tệp chính

| Tệp/thư mục | Vai trò |
|---|---|
| `main.tex` | Tệp chính để biên dịch |
| `metadata.tex` | Thông tin cá nhân và tên đề tài cần xác nhận |
| `preamble.tex` | A4, lề 2,4 cm, chữ 11pt, giãn dòng 1,23; navy/teal/xám |
| `sections/` | Các phần nội dung đã viết đầy đủ |
| `generated/` | Tám bảng chọn lọc, các dòng phụ lục và số liệu dùng trong nội dung |
| `references.bib` | Ba nguồn thực sự được sử dụng |
| `source_manifest.json` | Nguồn dữ liệu và SHA-256 để đối chiếu |
| `ASSETS.md` | Danh sách hình và bảng trong báo cáo |
| `scripts/prepare_tables.py` | Tạo lại bảng/số liệu từ dữ liệu hiện có, không tiền xử lý lại |
| `scripts/validate_source.py` | Kiểm tra nguồn và tham chiếu; không thay thế biên dịch |
| `scripts/package_sources.py` | Đóng gói nguồn cùng hình cho Overleaf |
| `build.ps1`, `latexmkrc` | Lệnh biên dịch khi đã có XeLaTeX và Biber |
| `output/` | Kết quả kiểm tra, gói nguồn và PDF sau khi biên dịch |

## Thông tin cần điền trước khi nộp

Mở `metadata.tex` và điền họ tên sinh viên, mã số sinh viên, giảng viên hướng dẫn và thời gian thực hiện. Tên đề tài đang là cách diễn đạt dựa trên dự án LMS Early Warning System; cần sửa thành đúng tên đã đăng ký nếu khác. Trường/khoa là tùy chọn. Không có thông tin cá nhân nào được suy ra từ PDF tham khảo.

## Biên dịch trên máy đã có LaTeX

Chạy tại thư mục này:

```powershell
latexmk -xelatex main.tex
```

Hoặc dùng:

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

Script chỉ gọi công cụ đã cài, không tải hoặc cài phần mềm. Kết quả mong đợi là `output/main.pdf`.

Nếu không có `latexmk` nhưng đã có XeLaTeX và Biber:

```powershell
xelatex -interaction=nonstopmode -halt-on-error -output-directory=output main.tex
biber --input-directory=output --output-directory=output main
xelatex -interaction=nonstopmode -halt-on-error -output-directory=output main.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=output main.tex
```

Các lượt sau Biber giúp cập nhật mục lục, số hình/bảng và tham chiếu. Dùng XeLaTeX, không dùng pdfLaTeX. Font chính là TeX Gyre Termes (serif), dự phòng Times New Roman. Các gói thông dụng được khai báo trong `preamble.tex`.

## Biên dịch trên Overleaf

1. Dùng `output/oulad_week3_sources.zip` đã đóng gói, hoặc tạo lại bằng script bên dưới.
2. Tạo dự án từ ZIP; chọn tệp chính `main.tex` và compiler **XeLaTeX**.
3. Điền `metadata.tex`, rồi Recompile. BibLaTeX sử dụng Biber.
4. Kiểm tra trang, hình, bảng, mục lục và log trước khi nộp.

Gói ZIP có hình trong `figures/` và đã điều chỉnh đường dẫn hình bên trong gói. Gói không chứa CSV gốc hoặc dữ liệu sinh viên. Các bảng LaTeX đã được tạo sẵn, không cần chạy Python trên Overleaf. Muốn tạo lại bảng từ CSV phải dùng bản dự án gốc với cấu trúc thư mục hiện tại.

## Cập nhật số liệu và kiểm tra

Từ thư mục gốc dự án, dùng Python có Pandas (ví dụ môi trường `oulad`):

```powershell
C:\ProgramData\miniconda3\envs\oulad\python.exe -X utf8 oulad_project/report/latex/scripts/prepare_tables.py
C:\ProgramData\miniconda3\envs\oulad\python.exe -X utf8 oulad_project/report/latex/scripts/validate_source.py
C:\ProgramData\miniconda3\envs\oulad\python.exe -X utf8 oulad_project/report/latex/scripts/package_sources.py
```

Nếu chạy ngay tại thư mục `report/latex/`, có thể dùng `python scripts/prepare_tables.py` tương tự. Script chỉ đọc các bảng đã xuất, năm CSV theo tuần và cột mã sinh viên trong bảng nhỏ `studentInfo`; không đọc lại `studentVle` và không tạo đặc trưng lại.

Số liệu nội dung đi qua macro trong `generated/metrics.tex`; các bảng ngắn đi qua `generated/`. Khi thay nguồn dữ liệu, tạo lại bảng rồi rà lại nhận xét và các ảnh notebook: script không tự vẽ lại hình hoặc sửa kết luận theo dữ liệu mới.

## Kiểm tra bắt buộc sau khi có PDF

- Điền đầy đủ thông tin bìa; kiểm tra tiếng Việt và dấu toán học.
- Xem mục lục, số trang, chú thích hình/bảng và tham chiếu; không có `??`.
- Kiểm tra log không có `Overfull`, `Missing character`, lỗi hoặc tham chiếu chưa xác định.
- Kiểm tra bảng dài ở phụ lục được ngắt đúng trang và tên trường có thể xuống dòng.
- Xem các hình toàn trang ở mức 100%; không giảm font để nhét nội dung.
- Chạy lại `validate_source.py`; nếu có `output/main.log`, script cũng kiểm tra các cảnh báo quan trọng trong log.

## Những nội dung chưa đủ dữ liệu để kết luận

- Chưa có kết quả huấn luyện, phân chia tập hoặc đánh giá mô hình; không có Accuracy/Recall/F1.
- Không có thời điểm công bố điểm hoặc lịch sử cập nhật thông tin nền/lịch hạn nộp.
- Chưa xác minh được log trùng là lỗi thu thập; chưa khôi phục được thời điểm rút trong các trường hợp thiếu.
- Bộ 23 đặc trưng là ứng viên ban đầu; giá trị thiếu của tỷ lệ nộp muộn còn cần phương án tương thích mô hình.
- So sánh giữa mốc là so sánh các nhóm có thể thay đổi, không phải thiết kế theo dõi cùng một nhóm cố định.
