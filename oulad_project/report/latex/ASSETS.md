# Hình, bảng và nguồn đã sử dụng

Đường dẫn nguồn bên dưới tính từ thư mục dự án `oulad_project/`. Không có hình lấy từ PDF tham khảo.

## Hình

| Nhãn LaTeX | Nội dung | Nguồn |
|---|---|---|
| `fig:relations` | Quan hệ bảy bảng | `report/figures/2_1_2_relationships.png` |
| `fig:target` | Bốn nhãn kết quả cuối kỳ | `report/figures/2_2_2_final_result.png` |
| `fig:demographics` | Các phân phối nhân khẩu học tiêu biểu | `report/figures/2_2_3_demographics.png` |
| `fig:scores` | Điểm bài nộp | `report/figures/2_2_4_score_distribution.png` |
| `fig:rawclicks` | Click trên từng bản ghi VLE | `report/figures/2_2_5_click_distribution.png` |
| `fig:activities` | Tỷ trọng tài nguyên và click | `report/figures/2_2_5_activity_type.png` |
| `fig:weekly` | Tổng click theo tuần học | `report/figures/2_2_5_vle_weekly_trend.png` |
| `fig:pipeline` | Luồng tích hợp ba nhóm đặc trưng | Sơ đồ TikZ mới trong `sections/chapter3.tex`, dựa trên code notebook |
| `fig:week8` | Phân phối theo lượt học ở tuần 8 | `report/figures/3_6_3_week8_interaction_distributions.png` |
| `fig:daily` | Trung vị click bình quân/ngày ở năm mốc | `report/figures/3_6_3_median_daily_clicks_by_week.png` |

Không đưa hình missing-value vào báo cáo vì đã có bảng tổng hợp giá trị thiếu; không lặp lại toàn bộ hình của notebook.

## Bảng trong báo cáo

| Nhãn LaTeX | Nội dung | Nguồn chính |
|---|---|---|
| `tab:progress` | Nội dung hoàn thiện tuần 3 | Nội dung thực tế của notebook; tổng hợp biên tập |
| `tab:dataset` | Vai trò và quy mô bảy bảng | `report/tables/2_1_1_table_size.csv` |
| `tab:keys` | Khóa kỳ vọng | `report/tables/2_1_2_key_catalog.csv` |
| `tab:missing-raw` | Giá trị thiếu trên dữ liệu thô | `report/tables/2_3_1_missing_all_columns.csv` |
| `tab:outliers` | Ngưỡng và số ứng viên ngoại lai | `report/tables/2_3_3_iqr_outliers.csv` |
| `tab:decisions` | Phát hiện nối với phương án xử lý | Các bảng chất lượng và `3_1_3_processing_plan.csv` |
| `tab:cutoffs` | Năm mốc quan sát | `report/tables/3_1_2_prediction_config.csv` |
| `tab:missing-actions` | Quyết định xử lý thiếu và kết quả | `report/tables/3_2_4_missing_before_after.csv` và code tương ứng |
| `tab:integrated` | Quy mô bộ dữ liệu theo mốc | `report/tables/3_5_4_integration_summary.csv` |
| `tab:final-checks` | Các kiểm tra sau tích hợp | `3_6_1_quality_checks.csv`, `3_6_1_future_invariance.csv`, `3_5_5_missing_features.csv`, kiểm tra xuất |
| `tab:zero-submissions` | Chưa có bài nộp tại từng mốc | `report/tables/3_6_3_zero_submissions.csv` |
| `tab:exports` | Các CSV đầu ra | `report/tables/3_6_4_exports.csv` |
| `tab:features` | 23 đặc trưng ứng viên và nguồn gốc | `report/tables/3_5_4_feature_dictionary.csv`, `feature_manifest.json` và code tạo đặc trưng |

Tám bảng định lượng và các dòng phụ lục được sinh bằng `scripts/prepare_tables.py`. Bảng khóa, phương án và kiểm tra được biên tập ngắn để dễ đọc; các số lượng dùng macro tính từ nguồn. `source_manifest.json` liệt kê toàn bộ CSV/notebook thực sự đã đọc, bao gồm các bảng dùng kiểm chứng nhận xét nhưng không chèn nguyên bảng vào PDF.

## Tài liệu tham khảo

- Bài báo gốc OULAD, DOI `10.1038/sdata.2017.171`.
- Trang dữ liệu chính thức của The Open University.
- NIST/SEMATECH e-Handbook, mục về ngoại lai và ngưỡng boxplot.

PDF mẫu chỉ dùng để tham khảo cách trình bày, không là nguồn số liệu hoặc phương pháp của báo cáo.
