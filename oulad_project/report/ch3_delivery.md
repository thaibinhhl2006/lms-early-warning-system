# Bàn giao cập nhật Chương 2 và Chương 3

Chương 2 giữ cấu trúc 2 tiểu mục ở 2.1 theo xác nhận của người dùng; thêm xu hướng VLE theo tuần và đề xuất 5 cutoff.
Chương 3 đã thực thi tuần tự: xử lý IMD, chuẩn hóa cách ghi/kiểu, xác định cohort, tổng hợp sự kiện và xuất dữ liệu.

| Mốc dự đoán (tuần) | Ngày chốt dữ liệu | Số lượt học | Số đặc trưng đầu vào (X) |
| --- | --- | --- | --- |
| 4 | 27 | 27,528 | 23 |
| 8 | 55 | 26,516 | 23 |
| 12 | 83 | 25,722 | 23 |
| 16 | 111 | 24,932 | 23 |
| 24 | 167 | 23,562 | 23 |

Kiểm tra: đủ khóa, không nhân dòng khi merge, khớp nhãn, cutoff, thiếu có lý do, bất biến khi thay đổi dữ liệu tương lai, đọc lại từng CSV.
Cả 7 CSV raw và modeling.ipynb giữ nguyên SHA-256. Không commit/push, không chia tập, OHE, StandardScaler hoặc huấn luyện.

Các giới hạn và quyết định còn mở:
- Log VLE trùng hoàn toàn chưa xác định là lỗi; giữ nguyên, nên các tổng click bao gồm chúng.
- Score không được dùng do không có ngày công bố điểm; Exam và điểm chuyển không được coi là bài nộp thông thường.
- Ngày đăng ký thiếu: giữ ở cơ sở, loại khỏi cohort. Ngày rút thiếu: coi là chưa ghi nhận rút; không dùng nhãn tương lai để suy diễn.
- OULAD không có lịch sử cập nhật thuộc tính nền hoặc công bố/điều chỉnh lịch đánh giá. Cần xác minh giả định khả dụng khi triển khai LMS thực tế.
- late_submission_rate còn NA khi không có bài đủ điều kiện làm mẫu số; chưa áp dụng điền thiếu học tham số.

Danh mục đầy đủ: report/tables/3_6_4_output_inventory.csv. Danh sách X và quy tắc dữ liệu: data/preprocessed/feature_manifest.json.