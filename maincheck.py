import threading
import time
import random
import tkinter as tk
from tkinter import ttk, messagebox
import importlib
import sys

# Khởi tạo dữ liệu dùng chung cho GUI
active_readers = set()
active_writers = set()
waiting_threads = []
gui_lock = threading.Lock()

# Lưu lại hàm print gốc của Python để dùng khi cần debug
original_print = print

import reader_priority as rp
import writer_priority as wp

fcfs = importlib.import_module("reader-writer fcfs khong test")


def update_gui_display():
    """Cập nhật trạng thái trực quan lên giao diện đồ họa"""
    with gui_lock:
        # 1. Cập nhật vùng chờ
        lbl_queue.config(text=", ".join(waiting_threads) if waiting_threads else "Trống")
        # 2. Cập nhật vùng đọc (Nhiều reader có thể cùng ở đây)
        lbl_readers.config(text=", ".join(sorted(list(active_readers))) if active_readers else "Trống")
        # 3. Cập nhật vùng ghi (Chỉ tối đa 1 writer)
        lbl_writers.config(text=", ".join(active_writers) if active_writers else "Trống")
        # 4. Trực quan hóa trạng thái Khóa
        if active_writers:
            lbl_lock_status.config(text="WRITER LOCK ACTIVE (Độc chiếm)", bg="#ff4d4d", fg="white")
        elif active_readers:
            lbl_lock_status.config(text=f"READER LOCK ACTIVE ({len(active_readers)} đang đọc)", bg="#ff9933",
                                   fg="black")
        else:
            lbl_lock_status.config(text="TÀI NGUYÊN TỰ DO (Sẵn sàng)", bg="#2ecc71", fg="white")


def custom_print(*args, **kwargs):
    """
    Hàm print giả lập: Đánh chặn các câu lệnh print từ file thuật toán
    để cập nhật trạng thái chính xác lên GUI theo thời gian thực.
    """
    message = " ".join(map(str, args))

    # In ra terminal gốc để vẫn theo dõi được bài làm
    original_print(message, **kwargs)

    # Phân tích nội dung chuỗi print từ file thuật toán của bạn
    text_lower = message.lower()

    with gui_lock:
        # Tìm xem từ khóa thuộc về Reader hay Writer nào
        for i in range(100):  # Giả định tối đa 100 luồng
            r_name = f"Reader-{i}"
            w_name = f"Writer-{i}"

            # --- XỬ LÝ READER ---
            if f"reader {i}" in text_lower or f"reader-{i}" in text_lower:
                if "vào" in text_lower or "bắt đầu" in text_lower or "đang đọc" in text_lower:
                    if r_name in waiting_threads: waiting_threads.remove(r_name)
                    active_readers.add(r_name)
                elif "ra" in text_lower or "xong" in text_lower or "kết thúc" in text_lower:
                    active_readers.discard(r_name)

            # --- XỬ LÝ WRITER ---
            if f"writer {i}" in text_lower or f"writer-{i}" in text_lower:
                if "vào" in text_lower or "bắt đầu" in text_lower or "đang ghi" in text_lower:
                    if w_name in waiting_threads: waiting_threads.remove(w_name)
                    active_writers.add(w_name)
                elif "ra" in text_lower or "xong" in text_lower or "kết thúc" in text_lower:
                    active_writers.discard(w_name)

    # Đẩy lệnh cập nhật giao diện về luồng chính của Tkinter
    root.after(0, update_gui_display)


# Ghi đè hàm print toàn cục của hệ thống bằng hàm custom_print của chúng ta
import builtins

builtins.print = custom_print


def make_gui_wrapper(original_func, is_writer=False):
    """
    Wrapper rút gọn: Chỉ làm đúng nhiệm vụ đưa luồng vào Hàng đợi chờ (Queue)
    khi luồng vừa được khởi tạo.
    """

    def wrapper(thread_id):
        t_name = f"Writer-{thread_id}" if is_writer else f"Reader-{thread_id}"

        # Bước 1: Luồng xuất hiện -> Đưa thẳng vào hàng đợi
        with gui_lock:
            if t_name not in waiting_threads:
                waiting_threads.append(t_name)
        root.after(0, update_gui_display)

        # Bước 2: Chạy hàm gốc.
        # Khi hàm gốc gọi print("Reader X bắt đầu đọc..."), hàm custom_print ở trên sẽ tự xử lý.
        original_func(thread_id)

    return wrapper


def start_benchmark_thread():
    """Chạy benchmark trên luồng nền để tránh treo giao diện Tkinter"""
    active_readers.clear()
    active_writers.clear()
    waiting_threads.clear()

    n_r = int(ent_readers.get())
    n_w = int(ent_writers.get())
    algo_name = combo_algo.get()

    if algo_name == "Reader Priority":
        rf, wf = rp.reader, rp.writer
    elif algo_name == "Writer Priority":
        rf, wf = wp.reader, wp.writer
    else:
        rf, wf = fcfs.reader, fcfs.writer

    gui_reader = make_gui_wrapper(rf, is_writer=False)
    gui_writer = make_gui_wrapper(wf, is_writer=True)

    def run():
        btn_start.config(state=tk.DISABLED)
        lbl_result.config(text="Đang chạy mô phỏng...", fg="blue")
        threads = []
        start_time = time.time()

        tasks = [('R', i) for i in range(n_r)] + [('W', i) for i in range(n_w)]
        random.shuffle(tasks)

        for task_type, task_id in tasks:
            target = gui_reader if task_type == 'R' else gui_writer
            t = threading.Thread(target=target, args=(task_id,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        end_time = time.time()
        total_time = end_time - start_time
        total_tasks = n_r + n_w
        throughput = total_tasks / total_time if total_time > 0 else 0

        lbl_result.config(
            text=f"Hoàn thành! Thời gian: {total_time:.4f}s | Thông lượng: {throughput:.2f} t/s",
            fg="#2ecc71"
        )
        btn_start.config(state=tk.NORMAL)

    threading.Thread(target=run, daemon=True).start()


# --- KHỞI TẠO CỬA SỔ TKINTER
root = tk.Tk()
root.title("Mô phỏng Đồng bộ hóa: Reader - Writer Problems")
root.geometry("650x550")
root.configure(bg="#f5f6fa")

frame_config = tk.LabelFrame(root, text=" Cấu hình kiểm thử ", font=("Arial", 11, "bold"), bg="#f5f6fa", pady=10)
frame_config.pack(fill="x", padx=15, pady=10)

tk.Label(frame_config, text="Thuật toán:", bg="#f5f6fa").grid(row=0, column=0, padx=5, pady=5, sticky="e")
combo_algo = ttk.Combobox(frame_config, values=["Reader Priority", "Writer Priority", "Fairness (FCFS)"],
                          state="readonly", width=15)
combo_algo.current(0)
combo_algo.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_config, text="Số Reader:", bg="#f5f6fa").grid(row=0, column=2, padx=5, pady=5, sticky="e")
ent_readers = tk.Entry(frame_config, width=5)
ent_readers.insert(0, "15")
ent_readers.grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame_config, text="Số Writer:", bg="#f5f6fa").grid(row=0, column=4, padx=5, pady=5, sticky="e")
ent_writers = tk.Entry(frame_config, width=5)
ent_writers.insert(0, "10")
ent_writers.grid(row=0, column=5, padx=5, pady=5)

btn_start = tk.Button(frame_config, text="BẮT ĐẦU CHẠY", bg="#3498db", fg="white", font=("Arial", 10, "bold"),
                      command=start_benchmark_thread)
btn_start.grid(row=0, column=6, padx=15, pady=5)

frame_monitor = tk.LabelFrame(root, text=" Trực quan hóa trạng thái Lock & Tài nguyên ", font=("Arial", 11, "bold"),
                              bg="#f5f6fa", pady=15)
frame_monitor.pack(fill="both", expand=True, padx=15, pady=10)

lbl_lock_status = tk.Label(frame_monitor, text="TÀI NGUYÊN TỰ DO (Sẵn sàng)", font=("Arial", 12, "bold"), bg="#2ecc71",
                           fg="white", height=2)
lbl_lock_status.pack(fill="x", padx=15, pady=5)

lbl_q_title = tk.Label(frame_monitor, text="Hàng đợi đang chờ (Queue):", font=("Arial", 10, "bold"), bg="#f5f6fa")
lbl_q_title.pack(anchor="w", padx=15, pady=(10, 0))
lbl_queue = tk.Label(frame_monitor, text="Trống", font=("Courier", 10), bg="white", anchor="w", justify="left",
                     relief="sunken", height=2, wraplength=550)
lbl_queue.pack(fill="x", padx=15, pady=2)

lbl_r_title = tk.Label(frame_monitor, text="Vùng các Reader đang đọc dữ liệu (Shared):", font=("Arial", 10, "bold"),
                       fg="#e67e22", bg="#f5f6fa")
lbl_r_title.pack(anchor="w", padx=15, pady=(10, 0))
lbl_readers = tk.Label(frame_monitor, text="Trống", font=("Courier", 10), bg="white", fg="#e67e22", anchor="w",
                       justify="left", relief="sunken", height=2, wraplength=550)
lbl_readers.pack(fill="x", padx=15, pady=2)

lbl_w_title = tk.Label(frame_monitor, text="Vùng Writer đang độc chiếm ghi dữ liệu (Exclusive):",
                       font=("Arial", 10, "bold"), fg="#c0392b", bg="#f5f6fa")
lbl_w_title.pack(anchor="w", padx=15, pady=(10, 0))
lbl_writers = tk.Label(frame_monitor, text="Trống", font=("Courier", 10), bg="white", fg="#c0392b", anchor="w",
                       justify="left", relief="sunken", height=2, wraplength=550)
lbl_writers.pack(fill="x", padx=15, pady=2)

frame_result = tk.LabelFrame(root, text=" Kết quả hiệu năng (Benchmark) ", font=("Arial", 11, "bold"), bg="#f5f6fa",
                             pady=10)
frame_result.pack(fill="x", padx=15, pady=15)

lbl_result = tk.Label(frame_result, text="Nhấn 'Bắt đầu chạy' để xem kết quả đánh giá thông lượng.",
                      font=("Arial", 10, "italic"), bg="#f5f6fa", fg="gray")
lbl_result.pack(pady=5)

root.mainloop()