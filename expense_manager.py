"""
Ứng dụng Quản lý Chi tiêu Cá nhân (Personal Expense Manager)
Chạy: python expense_manager.py
"""

import csv
import os
import unicodedata
from datetime import datetime
from collections import defaultdict

try:
    import matplotlib

    # Máy không có màn hình (server, WSL...) thì dùng backend không cửa sổ
    # để vẫn lưu được ảnh biểu đồ.
    if os.name != "nt" and not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY") \
            and os.uname().sysname != "Darwin":
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "expenses.csv")
SCREENSHOT_DIR = os.path.join(BASE_DIR, "screenshots")
CATEGORIES = ["Ăn uống", "Đi lại", "Học tập", "Giải trí", "Sức khỏe", "Khác"]


# ---------------------------------------------------------------------------
# Chuẩn hóa danh mục
# ---------------------------------------------------------------------------
def strip_accents(text):
    """Bỏ dấu tiếng Việt và chuyển về chữ thường: 'Ăn uống' -> 'an uong'."""
    text = text.replace("đ", "d").replace("Đ", "D")
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn").lower().strip()


_CATEGORY_LOOKUP = {strip_accents(c): c for c in CATEGORIES}


def normalize_category(name):
    """
    Đưa tên danh mục về một dạng chuẩn để thống kê không bị tách nhóm.
    - 'an uong', 'AN UONG', 'Ăn uống' đều thành 'Ăn uống'
    - Danh mục tự đặt: gom khoảng trắng, viết hoa chữ cái đầu ('cafe' -> 'Cafe')
    - Để trống -> 'Khác'
    """
    name = " ".join(name.split())
    if not name:
        return "Khác"
    known = _CATEGORY_LOOKUP.get(strip_accents(name))
    if known:
        return known
    return name[0].upper() + name[1:].lower()


# ---------------------------------------------------------------------------
# Lớp dữ liệu
# ---------------------------------------------------------------------------
class Expense:
    def __init__(self, date, category, amount, note=""):
        self.date = date
        self.category = normalize_category(category)
        self.amount = amount
        self.note = note

    def to_row(self):
        return [self.date, self.category, f"{self.amount:.0f}", self.note]

    @staticmethod
    def from_row(row):
        return Expense(row[0], row[1], float(row[2]), row[3] if len(row) > 3 else "")

    def __str__(self):
        return f"{self.date} | {self.category:<10} | {self.amount:>12,.0f} VND | {self.note}"


class ExpenseManager:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.expenses = []
        self._ensure_data_file()
        self.load()

    def _ensure_data_file(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["date", "category", "amount", "note"])

    def load(self):
        self.expenses = []
        with open(self.data_file, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if row:
                    self.expenses.append(Expense.from_row(row))

    def save(self):
        with open(self.data_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "category", "amount", "note"])
            for e in self.expenses:
                writer.writerow(e.to_row())

    def add_expense(self, date, category, amount, note=""):
        if amount <= 0:
            raise ValueError("Số tiền phải lớn hơn 0")
        expense = Expense(date, category, amount, note)
        self.expenses.append(expense)
        self.save()
        return expense

    def update_expense(self, index, date=None, category=None, amount=None, note=None):
        """Sửa một khoản chi. Tham số nào là None thì giữ nguyên giá trị cũ."""
        if index < 0 or index >= len(self.expenses):
            raise IndexError("Chỉ số không hợp lệ")
        if amount is not None and amount <= 0:
            raise ValueError("Số tiền phải lớn hơn 0")
        expense = self.expenses[index]
        if date is not None:
            expense.date = date
        if category is not None:
            expense.category = normalize_category(category)
        if amount is not None:
            expense.amount = amount
        if note is not None:
            expense.note = note
        self.save()
        return expense

    def delete_expense(self, index):
        if index < 0 or index >= len(self.expenses):
            raise IndexError("Chỉ số không hợp lệ")
        removed = self.expenses.pop(index)
        self.save()
        return removed

    def total(self):
        return sum(e.amount for e in self.expenses)

    def total_by_category(self):
        totals = defaultdict(float)
        for e in self.expenses:
            totals[e.category] += e.amount
        return dict(totals)

    def total_by_month(self):
        totals = defaultdict(float)
        for e in self.expenses:
            month_key = e.date[:7]
            totals[month_key] += e.amount
        return dict(sorted(totals.items()))

    def filter_by_category(self, category):
        target = normalize_category(category)
        return [e for e in self.expenses if e.category == target]


# ---------------------------------------------------------------------------
# Hàm nhập liệu
# ---------------------------------------------------------------------------
def parse_date(text):
    text = text.strip()
    if not text:
        return datetime.now().strftime("%Y-%m-%d")
    try:
        datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Ngày không hợp lệ, cần dạng YYYY-MM-DD (ví dụ 2026-11-08)")
    return text


def parse_amount(text):
    try:
        return float(text.strip().replace(",", ""))
    except ValueError:
        raise ValueError("Số tiền không hợp lệ, hãy nhập một con số")


def parse_index(text):
    try:
        return int(text.strip())
    except ValueError:
        raise ValueError("STT không hợp lệ, hãy nhập một số nguyên")


def prompt_category(allow_empty=False):
    print("Danh mục:")
    for i, c in enumerate(CATEGORIES, start=1):
        print(f"  {i}. {c}")
    choice = input("Chọn danh mục (số hoặc gõ tên): ").strip()
    if allow_empty and not choice:
        return None
    if choice.isdigit() and 1 <= int(choice) <= len(CATEGORIES):
        return CATEGORIES[int(choice) - 1]
    return choice or "Khác"


def show_menu():
    print("\n===== QUẢN LÝ CHI TIÊU CÁ NHÂN =====")
    print("1. Thêm khoản chi")
    print("2. Xem danh sách chi tiêu")
    print("3. Sửa một khoản chi")
    print("4. Xóa một khoản chi")
    print("5. Thống kê theo danh mục")
    print("6. Thống kê theo tháng")
    print("7. Vẽ biểu đồ (pie + bar)")
    print("0. Thoát")


# ---------------------------------------------------------------------------
# Các chức năng của menu
# ---------------------------------------------------------------------------
def action_add(manager):
    date = parse_date(input("Ngày (YYYY-MM-DD, Enter = hôm nay): "))
    category = prompt_category()
    amount = parse_amount(input("Số tiền (VND): "))
    note = input("Ghi chú (tùy chọn): ").strip()
    expense = manager.add_expense(date, category, amount, note)
    print(f"Đã thêm: {expense}")


def action_list(manager):
    if not manager.expenses:
        print("Chưa có khoản chi tiêu nào.")
        return
    print(f"\n{'STT':<5}{'Thông tin'}")
    for i, e in enumerate(manager.expenses):
        print(f"{i:<5}{e}")
    print(f"\nTổng cộng: {manager.total():,.0f} VND")


def action_edit(manager):
    action_list(manager)
    if not manager.expenses:
        return
    index = parse_index(input("Nhập STT cần sửa: "))
    if index < 0 or index >= len(manager.expenses):
        raise IndexError("Chỉ số không hợp lệ")
    current = manager.expenses[index]
    print(f"Đang sửa: {current}")
    print("(Nhấn Enter để giữ nguyên giá trị cũ)")

    date_text = input(f"Ngày [{current.date}]: ")
    date = parse_date(date_text) if date_text.strip() else None
    category = prompt_category(allow_empty=True)
    amount_text = input(f"Số tiền [{current.amount:,.0f}]: ")
    amount = parse_amount(amount_text) if amount_text.strip() else None
    note_text = input(f"Ghi chú [{current.note}]: ")
    note = note_text.strip() if note_text.strip() else None

    updated = manager.update_expense(index, date, category, amount, note)
    print(f"Đã cập nhật: {updated}")


def action_delete(manager):
    action_list(manager)
    if not manager.expenses:
        return
    index = parse_index(input("Nhập STT cần xóa: "))
    removed = manager.delete_expense(index)
    print(f"Đã xóa: {removed}")


def action_stats_category(manager):
    totals = manager.total_by_category()
    if not totals:
        print("Chưa có dữ liệu để thống kê.")
        return
    grand_total = sum(totals.values())
    print("\nThống kê theo danh mục:")
    for category, amount in sorted(totals.items(), key=lambda x: -x[1]):
        percent = (amount / grand_total * 100) if grand_total else 0
        print(f"  {category:<12}: {amount:>12,.0f} VND ({percent:5.1f}%)")


def action_stats_month(manager):
    totals = manager.total_by_month()
    if not totals:
        print("Chưa có dữ liệu để thống kê.")
        return
    print("\nThống kê theo tháng:")
    for month, amount in totals.items():
        print(f"  {month}: {amount:>12,.0f} VND")


def action_chart(manager):
    if not HAS_MATPLOTLIB:
        print("Chưa cài đặt matplotlib. Chạy: pip install matplotlib")
        return
    by_category = manager.total_by_category()
    by_month = manager.total_by_month()
    if not by_category:
        print("Chưa có dữ liệu để vẽ biểu đồ.")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.pie(by_category.values(), labels=by_category.keys(), autopct="%1.1f%%")
    ax1.set_title("Chi tiêu theo danh mục")

    ax2.bar(by_month.keys(), by_month.values(), color="steelblue")
    ax2.set_title("Chi tiêu theo tháng")
    ax2.set_ylabel("VND")
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax2.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    output_path = os.path.join(SCREENSHOT_DIR, "bieu_do_chi_tieu.png")
    plt.savefig(output_path)
    print(f"Đã lưu biểu đồ tại: {output_path}")

    # Chỉ mở cửa sổ khi người dùng muốn, để chương trình không bị treo chờ đóng cửa sổ.
    if input("Mở cửa sổ biểu đồ? (y/N): ").strip().lower() == "y":
        plt.show()
    plt.close(fig)


def main():
    manager = ExpenseManager()
    actions = {
        "1": action_add,
        "2": action_list,
        "3": action_edit,
        "4": action_delete,
        "5": action_stats_category,
        "6": action_stats_month,
        "7": action_chart,
    }
    try:
        while True:
            show_menu()
            choice = input("Chọn chức năng: ").strip()
            if choice == "0":
                break
            action = actions.get(choice)
            if not action:
                print("Lựa chọn không hợp lệ, vui lòng thử lại.")
                continue
            try:
                action(manager)
            except ValueError as e:
                print(f"Lỗi dữ liệu: {e}")
            except IndexError as e:
                print(f"Lỗi: {e}")
    except (EOFError, KeyboardInterrupt):
        print()  # xuống dòng cho gọn khi người dùng nhấn Ctrl+C / Ctrl+D
    print("Tạm biệt!")


if __name__ == "__main__":
    main()
