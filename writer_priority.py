#writer-prio
import threading
import time
import random

# các biến đếm số người đọc và số người viết
read_count = 0
write_count = 0

# các mutex bảo vệ biến đếm
read_m = threading.Lock()
write_m = threading.Lock()

#semaphore bảo vệ tài nguyên dùng chung, chỉ cho 1 thread dùng tài nguyên tại 1 lần
resource = threading.Semaphore(1) 

# semaphore chặn người đọc khi có người viết đang chờ (thể hiện tính writer priority)
read_lock = threading.Semaphore(1)

# biến dữ liệu dùng chung (mô phỏng)
shared_data = 0

print_lock=threading.Lock()

# người đọc
def reader (reader_id):
    global read_count

    with print_lock:
      print(f" Reader {reader_id} đã đến và chờ được đọc.")

    # xin phép đi qua cửa (Sẽ bị chặn nếu writer đang viết (đang giữ read_lock))
    read_lock.acquire()

    # cập nhật số lượng người đọc
    read_m.acquire()
    read_count += 1
    if (read_count == 1):
        resource.acquire() # người đọc đầu khóa tài nguyên lại không cho người viết vào
    with print_lock: # bắt đầu đọc
      print(f" Reader {reader_id} đang đọc dữ liệu {shared_data} (Tổng số người đang đọc: {read_count})")
    read_m.release() # release biến read_count

    read_lock.release() # release để người đọc khác có thể vào

    time.sleep(random.uniform(1,2)) # Mô phỏng thời gian đọc
    with print_lock:
      print(f" Reader {reader_id} đã đọc xong")
    # kết thúc đọc

    # giảm số lượng người đọc (đến 0 thì sẽ nhả cho người viết)
    read_m.acquire()
    read_count -= 1
    if (read_count == 0):
        with print_lock:
          print(f"Reader {reader_id} mở khóa")
        resource.release() # release tài nguyên cho người viết
    read_m.release()

# người viết
def writer(writer_id):
    global write_count, shared_data

    with print_lock:
      print (f" Writer {writer_id} đã đến và chuẩn bị viết")

    # cập nhật số lượng người viết
    write_m.acquire()
    write_count += 1
    if (write_count == 1):
        read_lock.acquire() # khóa cửa không cho người đọc mới vào (ưu tiên writer vì người đọc chỉ khóa tài liệu chung thôi còn người viết khóa luôn người đọc)
    write_m.release() # release biến write_count 

    # chờ để lấy quyền ghi độc quyền vào tài nguyên
    resource.acquire()

    # bắt đầu ghi dữ liệu
    shared_data += 10 # thay đổi dữ liệu
    with print_lock:
      print (f" Writer {writer_id} đang ghi dữ liệu mới: {shared_data}")
    time.sleep(random.uniform(1,2))
    
    # kết thúc ghi

    # release tài nguyên 
    resource.release()

    # giảm số lượng người viết
    write_m.acquire()
    write_count -= 1
    with print_lock:
      print(f" Writer {writer_id} đã ghi xong")
    if(write_count == 0):
        # không còn một người viết nào nữa thì mở cửa lại cho người đọc
        read_lock.release()
    write_m.release()