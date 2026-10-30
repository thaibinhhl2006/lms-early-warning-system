# Bàn giao Chương 2 – Khám phá và đánh giá dữ liệu OULAD

Đã chỉnh trực tiếp [preprocess.ipynb](../preprocess.ipynb), chỉ còn phần thiết lập và Chương 2 (2.1–2.4).
Bản sao lưu giữ nguyên byte của notebook ban đầu, bao gồm Chương 3:
[preprocess_with_ch3_backup.ipynb](../tmp/preprocess_with_ch3_backup.ipynb).

## Kiểm tra thực thi

- Đã kiểm tra cú pháp mọi ô Python và đúng thứ tự 4 mục chính, 13 tiểu mục.
- Luồng phân tích đã chạy thành công từ kernel mới; 0 ô đầu ra lỗi. Các chỉnh sửa trình bày sau đó được kiểm tra riêng trên số liệu đã kiểm chứng.
- Nhật ký VLE gồm 10,655,280 dòng được khảo sát toàn bộ theo khối 250.000 dòng, không dùng mẫu đầu tệp.
- Kiểm tra trùng toàn dòng qua 64 phân vùng tạm, so sánh chính xác mọi cột và tính cả trùng xuyên khối. Phân vùng tạm đã tự dọn.
- Hàm phân vị từ tần suất đã đối chiếu độc lập với NumPy trên mọi điểm score có giá trị; trung bình và độ lệch chuẩn khớp Pandas.
- SHA-256 của cả 7 CSV gốc và modeling.ipynb khớp trước/sau, đồng thời bản sao lưu khớp notebook ban đầu.
- Không điền/thay giá trị thiếu, không xóa trùng, không xử lý ngoại lai, không chuẩn hóa/mã hóa, không huấn luyện và không xuất dữ liệu huấn luyện.

Chi tiết kiểm tra máy đọc được: [ch2_validation.json](../tmp/ch2_validation.json).
Các bảng xuất ra là bảng báo cáo mô tả/kiểm toán, không phải dữ liệu đã tiền xử lý.
Các PNG được lưu ở 220 dpi.

## Một số kết quả cần chú ý

- Phát hiện 787,170 dòng dư trùng toàn dòng trong studentVle (7.3876%).
  Sáu bảng còn lại không có dòng dư trùng hoàn toàn. Chưa xóa dòng nào và chưa kết luận log lặp là lỗi.
- Có 7 cột thiếu thông tin; số lượng và tỷ lệ ở bảng dưới.
- Có 0 lượt vi phạm trong 62 phép kiểm tra miền đã định nghĩa,
  và 0 lượt dòng không khớp trong 11 hướng đối chiếu quan hệ.
  Kết luận chỉ có hiệu lực với các quy tắc đã áp dụng, không khẳng định dữ liệu hoàn toàn không lỗi.
- Đối chiếu trạng thái và mốc rút học, ngoại lai IQR, ngày âm, trọng số theo loại đánh giá
  và nhãn IMD được báo cáo riêng trong notebook; chưa tự động sửa trường hợp nào.

| Bảng | Cột | Số giá trị thiếu | Tỷ lệ thiếu (%) |
| --- | --- | --- | --- |
| assessments | date | 11 | 5.339805825242719 |
| studentInfo | imd_band | 1111 | 3.4087073911576105 |
| studentRegistration | date_registration | 45 | 0.13806645598748196 |
| studentRegistration | date_unregistration | 22521 | 69.09765900653514 |
| studentAssessment | score | 173 | 0.09947559685358112 |
| vle | week_from | 5243 | 82.3852922690132 |
| vle | week_to | 5243 | 82.3852922690132 |

## Danh mục đầy đủ 30 bảng thống kê và 7 hình

Các tệp dưới đây tính đường dẫn từ thư mục oulad_project.
Một số tệp hình gồm nhiều ô biểu đồ có liên quan để tiện sử dụng trong báo cáo.

| Loại | Tệp | Nội dung |
| --- | --- | --- |
| Bảng | report/tables/2_1_1_table_size.csv | Nội dung và quy mô 7 bảng OULAD |
| Bảng | report/tables/2_1_2_key_catalog.csv | Khóa kỳ vọng và đường liên kết |
| Bảng | report/tables/2_2_1_schema_courses.csv | Cấu trúc và miền giá trị – courses |
| Bảng | report/tables/2_2_1_schema_assessments.csv | Cấu trúc và miền giá trị – assessments |
| Bảng | report/tables/2_2_1_schema_studentInfo.csv | Cấu trúc và miền giá trị – studentInfo |
| Bảng | report/tables/2_2_1_schema_studentRegistration.csv | Cấu trúc và miền giá trị – studentRegistration |
| Bảng | report/tables/2_2_1_schema_studentAssessment.csv | Cấu trúc và miền giá trị – studentAssessment |
| Bảng | report/tables/2_2_1_schema_vle.csv | Cấu trúc và miền giá trị – vle |
| Bảng | report/tables/2_2_1_schema_studentVle.csv | Cấu trúc và miền giá trị – studentVle |
| Bảng | report/tables/2_2_1_numeric_summary.csv | Thống kê mô tả toàn bộ các cột định lượng và thời gian |
| Bảng | report/tables/2_2_2_final_result.csv | Phân phối final_result theo lượt học |
| Bảng | report/tables/2_2_3_demographics.csv | Phân phối sáu đặc trưng nhân khẩu học (theo lượt học) |
| Bảng | report/tables/2_2_4_score_summary.csv | Thống kê điểm trên toàn bộ bài nộp |
| Bảng | report/tables/2_2_4_score_by_type.csv | Điểm và số bài nộp theo assessment_type |
| Bảng | report/tables/2_2_5_click_summary.csv | Phân phối số click trên toàn bộ nhật ký VLE |
| Bảng | report/tables/2_2_5_activity_type.csv | Phân phối tài nguyên, bản ghi và click theo activity_type |
| Bảng | report/tables/2_3_1_missing_all_columns.csv | Kiểm tra thiếu trên mọi cột của 7 bảng |
| Bảng | report/tables/2_3_1_missing_by_table.csv | Thiếu dữ liệu theo bảng (đơn vị ô) |
| Bảng | report/tables/2_3_1_assessment_date_context.csv | Ngữ cảnh thiếu hạn đánh giá theo loại bài |
| Bảng | report/tables/2_3_2_exact_duplicates.csv | Kiểm tra bản ghi trùng lặp hoàn toàn trong 7 bảng |
| Bảng | report/tables/2_3_2_key_checks.csv | Kiểm tra khóa kỳ vọng của 6 bảng có khóa |
| Bảng | report/tables/2_3_3_invalid_values.csv | Kiểm tra miền hợp lệ (không bao gồm NA) |
| Bảng | report/tables/2_3_3_iqr_outliers.csv | Ứng viên ngoại lai theo quy tắc Tukey trên dữ liệu thô |
| Bảng | report/tables/2_3_4_referential_integrity.csv | Kiểm tra toàn vẹn quan hệ trên toàn bộ dữ liệu |
| Bảng | report/tables/2_3_4_consistency_context.csv | Tính nhất quán thời gian, trạng thái và cách ghi nhãn |
| Bảng | report/tables/2_3_4_weights_by_course.csv | Trọng số theo đợt học và nhóm đánh giá |
| Bảng | report/tables/2_4_1_quality_summary.csv | Tổng hợp kết quả đánh giá chất lượng dữ liệu thô |
| Bảng | report/tables/2_4_2_preprocessing_proposals.csv | Đề xuất tiền xử lý và những quyết định còn mở |
| Bảng | report/tables/2_4_2_source_integrity.csv | Đối chiếu SHA-256 của 7 CSV gốc và modeling.ipynb |
| Bảng | report/tables/2_4_2_output_inventory.csv | Danh mục bảng và hình đã xuất cho báo cáo |
| Hình | report/figures/2_1_2_relationships.png | Sơ đồ quan hệ giữa 7 bảng |
| Hình | report/figures/2_2_2_final_result.png | Phân phối final_result |
| Hình | report/figures/2_2_3_demographics.png | Bốn phân phối nhân khẩu học |
| Hình | report/figures/2_2_4_score_distribution.png | Histogram điểm và boxplot theo loại đánh giá |
| Hình | report/figures/2_2_5_click_distribution.png | Phân phối sum_click toàn bộ log |
| Hình | report/figures/2_2_5_activity_type.png | Tỷ trọng tài nguyên và click theo activity_type |
| Hình | report/figures/2_3_1_missing_values.png | Tỷ lệ thiếu theo cột |

## Phần còn mở và quyết định cần chốt

Không còn tiểu mục Chương 2 bắt buộc nào chưa triển khai/chưa chạy.
Những việc sau được để lại đúng phạm vi đề xuất, chưa thực hiện:

| Phạm vi | Quyết định còn cần |
| --- | --- |
| vle.week_from | Chọn phương án sau khi chốt biến sử dụng và mốc dự đoán |
| vle.week_to | Chọn phương án sau khi chốt biến sử dụng và mốc dự đoán |
| studentRegistration.date_unregistration | Chọn phương án sau khi chốt biến sử dụng và mốc dự đoán |
| assessments.date | Chọn phương án sau khi chốt biến sử dụng và mốc dự đoán |
| studentInfo.imd_band | Chọn phương án sau khi chốt biến sử dụng và mốc dự đoán |
| studentRegistration.date_registration | Chọn phương án sau khi chốt biến sử dụng và mốc dự đoán |
| studentAssessment.score | Chọn phương án sau khi chốt biến sử dụng và mốc dự đoán |
| Trùng toàn dòng | Xác nhận ý nghĩa bản ghi lặp |
| Giá trị không hợp lệ và khóa ngoại | Chỉ cần can thiệp nếu phát hiện lỗi có căn cứ |
| Ngoại lai IQR | Không cắt IQR tự động; chọn theo mục tiêu mô hình |
| IMD: cách ghi nhãn | Có dùng IMD và xem là thứ bậc hay danh nghĩa |
| final_result và chia tập | Mục tiêu dự đoán, định nghĩa nhãn và đơn vị chia tập |
| Mốc ngày và khả dụng thông tin | Ngày dự đoán, cửa sổ quan sát và quy tắc khả dụng score |
| Mã hóa, điền thiếu, chuẩn hóa và tích hợp | Chưa bắt đầu Chương 3 cho đến khi phạm vi được chốt |

Các quyết định này không cản trở việc sử dụng kết quả Chương 2. Chương 3 vẫn nằm trong bản sao lưu
và chưa được triển khai trong notebook hiện tại.
