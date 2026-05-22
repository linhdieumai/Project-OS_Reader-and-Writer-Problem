#firstcomefirstserve
import threading
import time
import random

# khởi tạo các semaphore
# đảm bảo thứ tự phục vụ (ai đến trước vào hàng đợi trước)
service_queue = threading.Semaphore(1)
# bảo vệ tài nguyên chung, chỉ cho phép 1 writer hoặc n readers
resource = threading.Semaphore(1)
# bảo vệ biến read_count khi nhiều reader cùng đọc
read_m = threading.Semaphore(1)

read_count = 0
shared_data = 0
print_lock = threading.Lock()

def reader(id):
    global read_count, shared_data
    
    with print_lock:
      print(f" Reader {id} đã đến và chờ được đọc.")
    
    # entry
    service_queue.acquire()           # chờ đến lượt phục vụ
    read_m.acquire()         # khóa để cập nhật read_count
    
    read_count += 1
    if read_count == 1:               # nếu là reader đầu tiên
        resource.acquire()            # khóa tài nguyên không cho writer vào
    # critical
    with print_lock:
        print(f" Reader {id} đang đọc dữ liệu {shared_data} (Tổng số người đang đọc: {read_count})")    
    read_m.release()
    service_queue.release()           # cho phép người tiếp theo trong hàng đợi vào
    
    
    time.sleep(random.uniform(1, 2))  # mô phỏng thời gian đọc
    with print_lock:
        print(f" Reader {id} đã đọc xong")
        
    # exit
    read_m.acquire()
    read_count -= 1
    if read_count == 0:               # nếu là reader cuối cùng rời đi
        with print_lock:
            print(f"Reader {id} mở khóa")               
        resource.release()            # giải phóng tài nguyên cho writer
    read_m.release()

def writer(id):
    global shared_data
    with print_lock:
        print (f" Writer {id} đã đến và chuẩn bị viết")
    
    # entry 
    service_queue.acquire()           # chờ đến lượt phục vụ
    resource.acquire()                # chờ lấy quyền ghi độc quyền
    service_queue.release()           # cho phép người tiếp theo trong hàng đợi vào
    
    # critical 
    shared_data += 10 
    with print_lock:
        print (f" Writer {id} đang ghi dữ liệu mới: {shared_data}")
    time.sleep(random.uniform(1, 2))  # mô phỏng thời gian ghi
    
    # exit
    with print_lock:
        print(f" Writer {id} đã ghi xong")
    resource.release()