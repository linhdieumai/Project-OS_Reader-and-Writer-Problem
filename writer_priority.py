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

# người đọc
def reader (reader_id):
    global read_count

    print(f" Reader {reader_id} đã đến và chờ được đọc.")

    # xin phép đi qua cửa (Sẽ bị chặn nếu writer đang viết (đang giữ read_lock))
    read_lock.acquire()

    # cập nhật số lượng người đọc
    read_m.acquire()
    read_count += 1
    if (read_count == 1):
        resource.acquire() # người đọc đầu khóa tài nguyên lại không cho người viết vào
    read_m.release() # release biến read_count

    read_lock.release() # release để người đọc khác có thể vào

    # bắt đầu đọc
    print(f" Reader {reader_id} đang đọc dữ liệu {shared_data} (Tổng số người đang đọc: {read_count})")
    time.sleep(random.uniform(0.5,1.5)) # Mô phỏng thời gian đọc
    print(f" Reader {reader_id} đã đọc xong")
    # kết thúc đọc

    # giảm số lượng người đọc (đến 0 thì sẽ nhả cho người viết)
    read_m.acquire()
    read_count -= 1
    if (read_count == 0):
        resource.release() # release tài nguyên cho người viết
    read_m.release()

# người viết
def writer(writer_id):
    global write_count, shared_data

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
    print (f" Writer {writer_id} đang ghi dữ liệu mới: {shared_data}")
    time.sleep(random.uniform(1,2))
    print(f" Writer {writer_id} đã ghi xong")
    # kết thúc ghi

    # release tài nguyên 
    resource.release()

    # giảm số lượng người viết
    write_m.acquire()
    write_count -= 1
    if(write_count == 0):
        # không còn một người viết nào nữa thì mở cửa lại cho người đọc
        read_lock.release()
    write_m.release()

# main
print("Bắt đầu mô phỏng Reader-Writer (Writer priority)\n")

threads = []

# Kịch bản mô phòng (để thấy rõ sự ưu tiên):
# Cho 1 writer W1 vào trước, 1 reader R1 vào và cuối cùng là 2 W2,W3 writer vào
# Sẽ thấy dù R1 đến trước nhưng phải chờ W2,W3 viết xong mới được vào, thấy hiện tượng starvation cho người đọc.

# Tạo 1 writer đến sớm 
t1 = threading.Thread(target = writer, args = (1,)) # Tạo luồng mới tên t, phân công nó chạy hàm writer và đưa cho nó số 1 như tên của nó là writer 1
threads.append(t1)
t1.start()

time.sleep(0.1) # chờ cho writer này kịp vào viết

# Tạo 1 reader vào tiếp theo
t2 = threading.Thread(target = reader, args = (1,))
threads.append(t2)
t2.start()

time.sleep(0.1)

# Tạo 2 writer đến muộn nhưng lại được vào trước reader
for i in range (2,4):
    t3 = threading.Thread(target = writer, args = (i,))
    threads.append(t3)
    t3.start()

# chờ tất cả các luồn chạy xong
for t in threads:
    t.join()

print("Hoàn thành mô phỏng !")

    
