import threading
import time
import random

# Khởi tạo các Semaphore
# service_queue: Đảm bảo thứ tự phục vụ (ai đến trước vào hàng đợi trước)
service_queue = threading.Semaphore(value=1)
# resource: Bảo vệ tài nguyên chung, chỉ cho phép 1 Writer hoặc n Readers
resource = threading.Semaphore(value=1)
# read_count_lock: Bảo vệ biến read_count khi nhiều Reader cùng cập nhật
read_count_lock = threading.Semaphore(value=1)

read_count = 0

def reader(id):
    global read_count
    
    print(f"[Reader {id}] đang đợi...")
    
    # GIAI ĐOẠN VÀO (Entry Section)
    service_queue.acquire()           # Chờ đến lượt phục vụ
    read_count_lock.acquire()         # Khóa để cập nhật read_count
    
    read_count += 1
    if read_count == 1:               # Nếu là Reader đầu tiên
        resource.acquire()            # Khóa tài nguyên không cho Writer vào
        
    read_count_lock.release()
    service_queue.release()           # Cho phép người tiếp theo trong hàng đợi vào
    
    # GIAI ĐOẠN ĐỌC (Critical Section)
    print(f"--- [Reader {id}] ĐANG ĐỌC dữ liệu... (Tổng số reader: {read_count})")
    time.sleep(random.uniform(1, 2))  # Mô phỏng thời gian đọc
    
    # GIAI ĐOẠN RA (Exit Section)
    read_count_lock.acquire()
    read_count -= 1
    if read_count == 0:               # Nếu là Reader cuối cùng rời đi
        resource.release()            # Giải phóng tài nguyên cho Writer
    print(f"--- [Reader {id}] đã đọc xong và rời đi.")
    read_count_lock.release()

def writer(id):
    print(f"    [Writer {id}] đang đợi...")
    
    # GIAI ĐOẠN VÀO (Entry Section)
    service_queue.acquire()           # Chờ đến lượt phục vụ
    resource.acquire()                # Chờ lấy quyền ghi độc quyền
    service_queue.release()           # Cho phép người tiếp theo trong hàng đợi vào
    
    # GIAI ĐOẠN GHI (Critical Section)
    print(f"    ===> [Writer {id}] ĐANG GHI dữ liệu...")
    time.sleep(random.uniform(1, 2))  # Mô phỏng thời gian ghi
    
    # GIAI ĐOẠN RA (Exit Section)
    print(f"    ===> [Writer {id}] đã ghi xong và rời đi.")
    resource.release()
