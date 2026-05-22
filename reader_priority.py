#reader-prio
from threading import Semaphore,Thread,Lock
from time import sleep
from random import uniform
#số reader
read_count=0
#mutex của reader
read_m=Lock()
#quyền truy cập của writer
write_lock=Semaphore(1)
#dữ liệu đọc/viết
shared_data=0
#để print đúng thứ tự
print_lock=Lock()

def reader(reader_id):
    global read_count,shared_data
    #khóa quyền reader để cập nhật số reader + khóa quyền write
    with print_lock:
      print(f" Reader {reader_id} đã đến và chờ được đọc.")
    read_m.acquire()
    read_count+=1
    if(read_count==1):
        write_lock.acquire()
    read_m.release()

    with print_lock:
        print(f" Reader {reader_id} đang đọc dữ liệu {shared_data} (Tổng số người đang đọc: {read_count})")
    read_time=uniform(1,2)
    sleep(read_time)
    with print_lock:
        print(f" Reader {reader_id} đã đọc xong")

    #đọc xong-> cập nhật số người đọc và trả quyền write khi hết người đọc
    read_m.acquire()
    read_count-=1
    if(read_count==0):
        with print_lock:
            print(f"Reader {reader_id} mở khóa")
        write_lock.release()
    read_m.release()
    
def writer(writer_id):
    global shared_data
    with print_lock:
        print (f" Writer {writer_id} đã đến và chuẩn bị viết")
    #xin quyền write
    write_lock.acquire()

    shared_data+=10
    with print_lock:
        print (f" Writer {writer_id} đang ghi dữ liệu mới: {shared_data}")
    write_time=uniform(1,2)
    
    sleep(write_time)
    with print_lock:
        print(f" Writer {writer_id} đã ghi xong")
    #viết xong
    write_lock.release()

