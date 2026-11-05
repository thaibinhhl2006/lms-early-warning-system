# Trạng thái biên dịch

Mã nguồn báo cáo đã được hoàn thiện. Môi trường hiện tại không có XeLaTeX, latexmk hoặc Biber, nên **chưa tạo được PDF bằng XeLaTeX**.

Các kiểm tra đã thực hiện: đối chiếu số liệu nguồn; cấu trúc và tham chiếu LaTeX; đường dẫn và tính hợp lệ của hình; danh sách tài liệu tham khảo; bảo toàn notebook, dữ liệu và các đầu ra cũ. Chi tiết ở `validation.json`.

Chưa xác minh được: ngắt trang thực tế, số trang cuối, cảnh báo font/glyph và tràn lề sau biên dịch, bố cục từng trang PDF. Kiểm tra tĩnh không thay thế những kiểm tra này.

Dùng `oulad_week3_sources.zip` trên Overleaf, chọn `main.tex` và XeLaTeX; hoặc chạy `latexmk -xelatex main.tex` tại thư mục mã nguồn trên máy đã có công cụ. Điền `metadata.tex` và xem log/PDF trước khi nộp.
