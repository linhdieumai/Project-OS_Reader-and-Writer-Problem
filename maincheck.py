#check
import threading
import time
import random
import sys

# Import các hàm từ 3 file bạn đã cung cấp
import reader_priority as rp
import writer_priority as wp
import importlib

# Vì tên file có dấu cách, ta dùng importlib để load
fcfs = importlib.import_module("reader-writer fcfs khong test")


def run_benchmark(mode_name, reader_func, writer_func, n_r, n_w):
    """
    Chạy kiểm thử và tính toán Thông lượng (Throughput)
    """
    print("\n" + "#" * 30)
    print(f"BẮT ĐẦU CHẠY: {mode_name.upper()}")
    print("#" * 30 + "\n")
    threads = []
    start_time = time.time()

    # Tạo danh sách task
    tasks = [('R', i) for i in range(n_r)] + [('W', i) for i in range(n_w)]
    random.shuffle(tasks)

    for task_type, task_id in tasks:
        target = reader_func if task_type == 'R' else writer_func
        t = threading.Thread(target=target, args=(task_id,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end_time = time.time()
    total_time = end_time - start_time
    total_tasks = n_r + n_w

    # Tính thông lượng: Tổng số task / Tổng thời gian
    throughput = total_tasks / total_time if total_time > 0 else 0

    return total_time, throughput


if __name__ == "__main__":
    # Định nghĩa 3 kịch bản kiểm thử
    scenarios = [
        {"name": "Reader > Writer (Tra cứu)", "n_r": 15, "n_w": 3},
        {"name": "Writer > Reader (Cập nhật)", "n_r": 3, "n_w": 15},
        {"name": "Reader = Writer (Cân bằng)", "n_r": 10, "n_w": 10}
    ]

    algorithms = [
        {"name": "Reader Priority", "rf": rp.reader, "wf": rp.writer},
        {"name": "Writer Priority", "rf": wp.reader, "wf": wp.writer},
        {"name": "Fairness (FCFS)", "rf": fcfs.reader, "wf": fcfs.writer}
    ]

    # Lưu kết quả để in bảng
    final_results = []

    print("--- BẮT ĐẦU QUÁ TRÌNH KIỂM THỬ CHUYÊN SÂU ---")

    for sc in scenarios:
        print(f"\n>>> Đang chạy kịch bản: {sc['name']}...")
        for algo in algorithms:
            t, tp = run_benchmark(algo['name'], algo['rf'], algo['wf'], sc['n_r'], sc['n_w'])
            final_results.append({
                "scenario": sc['name'],
                "algo": algo['name'],
                "time": t,
                "throughput": tp
            })

    # IN BẢNG TỔNG KẾT CHO BÁO CÁO
    print("\n" + "=" * 90)
    print(f"{'KỊCH BẢN':<25} | {'PHƯƠNG PHÁP':<20} | {'THỜI GIAN (s)':<15} | {'THÔNG LƯỢNG':<15}")
    print("=" * 90)

    current_scenario = ""
    for res in final_results:
        # In dòng kẻ phân cách khi đổi kịch bản cho dễ nhìn
        if res['scenario'] != current_scenario:
            if current_scenario != "": print("-" * 90)
            current_scenario = res['scenario']
            scenario_display = res['scenario']
        else:
            scenario_display = ""  # Để trống tên kịch bản ở các dòng dưới cho thoáng

        print(f"{scenario_display:<25} | {res['algo']:<20} | {res['time']:<15.4f} | {res['throughput']:<15.2f} t/s")

    print("=" * 90)