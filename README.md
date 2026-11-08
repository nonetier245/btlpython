# Ứng dụng Quản lý Chi tiêu Cá nhân (Personal Expense Manager)

## 1. Mục tiêu đề tài

Xây dựng một ứng dụng dòng lệnh (CLI) bằng Python giúp người dùng:
- Ghi lại, sửa và xóa các khoản chi tiêu hằng ngày (ngày, danh mục, số tiền, ghi chú)
- Lưu trữ dữ liệu bền vững bằng file CSV
- Thống kê tổng chi tiêu theo danh mục và theo tháng
- Trực quan hóa dữ liệu bằng biểu đồ tròn (pie chart) và biểu đồ cột (bar chart)

## 2. Cấu trúc project

```
expense_manager/
├── expense_manager.py     # Toàn bộ mã nguồn chương trình
├── data/
│   └── expenses.csv       # File dữ liệu (tự tạo nếu chưa có), kèm dữ liệu mẫu
├── screenshots/           # Nơi lưu ảnh chụp màn hình & biểu đồ xuất ra (tự tạo nếu chưa có)
├── requirements.txt        # Thư viện cần cài (matplotlib)
└── README.md               # Báo cáo mô tả đề tài
```

## 3. Kiến thức & kỹ thuật Python đã sử dụng

- **Lập trình hướng đối tượng (OOP)**: class `Expense` (đối tượng dữ liệu) và class `ExpenseManager` (xử lý nghiệp vụ: thêm/xóa/thống kê/lưu/đọc).
- **Xử lý file**: đọc/ghi dữ liệu với module `csv`.
- **Xử lý ngoại lệ**: `try/except` bắt lỗi nhập liệu sai (`ValueError`, `IndexError`) và việc người dùng thoát đột ngột bằng Ctrl+C / Ctrl+D (`KeyboardInterrupt`, `EOFError`).
- **Chuẩn hóa dữ liệu**: dùng `unicodedata` để bỏ dấu tiếng Việt khi so khớp danh mục, nên "an uong", "AN UONG", "Ăn uống" đều được gom vào cùng một nhóm khi thống kê.
- **Cấu trúc dữ liệu**: `defaultdict` để gom nhóm và tính tổng theo danh mục/tháng.
- **Module chuẩn**: `datetime` để xử lý và kiểm tra định dạng ngày tháng.
- **Trực quan hóa dữ liệu**: `matplotlib` để vẽ pie chart (tỉ lệ chi tiêu theo danh mục) và bar chart (chi tiêu theo tháng), đồng thời lưu ảnh ra file.
- **Thiết kế module hóa**: tách riêng logic (class) và giao diện người dùng (hàm `action_*`, vòng lặp menu), dễ bảo trì và mở rộng.

## 4. Hướng dẫn cài đặt & chạy chương trình

```bash
cd expense_manager
pip install -r requirements.txt
python expense_manager.py
```

Chương trình hiển thị menu:

```
===== QUẢN LÝ CHI TIÊU CÁ NHÂN =====
1. Thêm khoản chi
2. Xem danh sách chi tiêu
3. Sửa một khoản chi
4. Xóa một khoản chi
5. Thống kê theo danh mục
6. Thống kê theo tháng
7. Vẽ biểu đồ (pie + bar)
0. Thoát
```

Dữ liệu mẫu (10 khoản chi trong tháng 10-11/2026) đã có sẵn trong `data/expenses.csv` để kiểm thử nhanh chức năng thống kê và vẽ biểu đồ.

## 5. Minh chứng sản phẩm

- Ảnh chụp menu chương trình: `screenshots/menu.png`
- Ảnh chụp chức năng thống kê theo danh mục: `screenshots/thong_ke.png`
- Biểu đồ trực quan hóa (tự động lưu khi chọn chức năng 7): `screenshots/bieu_do_chi_tieu.png`

> Ghi chú: chạy chức năng 7 trong chương trình sẽ tự động tạo file biểu đồ nói trên. Hai ảnh `menu.png` và `thong_ke.png` cần tự chụp màn hình console khi chạy chương trình (chức năng 5 cho ảnh thống kê) rồi bỏ vào thư mục `screenshots/`.

## 6. Hướng phát triển thêm (nếu có thời gian)

- Xuất báo cáo ra file Excel/PDF
- Xây dựng giao diện đồ họa (Tkinter) thay cho CLI
