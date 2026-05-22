#firstcomefirstserve
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

shared_data=0
print_lock=threading.Lock()

def reader(id):
    global read_count,shared_data
    
    with print_lock:
      print(f" Reader {id} đã đến và chờ được đọc.")
    
    # GIAI ĐOẠN VÀO (Entry Section)
    service_queue.acquire()           # Chờ đến lượt phục vụ
    read_count_lock.acquire()         # Khóa để cập nhật read_count
    
    read_count += 1
    if read_count == 1:               # Nếu là Reader đầu tiên
        resource.acquire()            # Khóa tài nguyên không cho Writer vào
        
    read_count_lock.release()
    service_queue.release()           # Cho phép người tiếp theo trong hàng đợi vào
    
    # GIAI ĐOẠN ĐỌC (Critical Section)
    with print_lock:
        print(f" Reader {id} đang đọc dữ liệu {shared_data} (Tổng số người đang đọc: {read_count})")
    time.sleep(random.uniform(1, 2))  # Mô phỏng thời gian đọc
    with print_lock:
        print(f" Reader {id} đã đọc xong")
    # GIAI ĐOẠN RA (Exit Section)
    read_count_lock.acquire()
    read_count -= 1
    if read_count == 0:               # Nếu là Reader cuối cùng rời đi
        with print_lock:
            print(f"Reader {id} mở khóa")               
        resource.release()            # Giải phóng tài nguyên cho Writer
    read_count_lock.release()

def writer(id):
    global shared_data
    with print_lock:
        print (f" Writer {id} đã đến và chuẩn bị viết")
    
    # GIAI ĐOẠN VÀO (Entry Section)
    service_queue.acquire()           # Chờ đến lượt phục vụ
    resource.acquire()                # Chờ lấy quyền ghi độc quyền
    service_queue.release()           # Cho phép người tiếp theo trong hàng đợi vào
    
    # GIAI ĐOẠN GHI (Critical Section)
    shared_data+=10
    with print_lock:
        print (f" Writer {id} đang ghi dữ liệu mới: {shared_data}")
    time.sleep(random.uniform(1, 2))  # Mô phỏng thời gian ghi
    
    # GIAI ĐOẠN RA (Exit Section)
    with print_lock:
        print(f" Writer {id} đã ghi xong")
    resource.release()
