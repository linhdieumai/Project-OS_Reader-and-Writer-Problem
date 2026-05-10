from threading import Semaphore,Thread,Lock
from time import sleep
from random import uniform
#số reader
readcnt=0
#mutex của reader
read_m=Lock()
#quyền truy cập của writer
write_lock=Semaphore(1)
#dữ liệu đọc/viết
shared_data=0
#để print đúng thứ tự
print_lock=Lock()

def reader(reader_id):
    global readcnt,shared_data
    #khóa quyền reader để cập nhật số reader + khóa quyền write
    read_m.acquire()
    readcnt+=1
    if(readcnt==1):
        write_lock.acquire()
    read_m.release()

    with print_lock:
        print(f"Reader {reader_id} đọc {shared_data}")
    read_time=uniform(1,5)
    sleep(read_time)
    with print_lock:
        print(f"Reader {reader_id} đã đọc xong")

    #đọc xong-> cập nhật số người đọc và trả quyền write khi hết người đọc
    read_m.acquire()
    readcnt-=1
    if(readcnt==0):
        with print_lock:
            print(f"Reader {reader_id} mở khóa")
        write_lock.release()
    read_m.release()
    
def writer(writer_id):
    global shared_data
    with print_lock:
        print(f"Write {writer_id} xin vào")
    #xin quyền write
    write_lock.acquire()

    with print_lock:
        print(f"Writer {writer_id} sửa {shared_data} thành",end=' ')
    shared_data+=10
    with print_lock:
        print(f"{shared_data}")
    write_time=uniform(1,2)
    with print_lock:
        print(f"Writer {writer_id} đã sửa xong")
    sleep(write_time)

    #viết xong
    write_lock.release()

#ví dụ
threads=[]

#15 reader vào đọc trước -> 160 writer xin vào sửa -> 5 reader đến sau => 5 reader đến sau sẽ chen hàng và đc đọc rồi writer ms được sửa
for i in range(15):
    t=Thread(target=reader,args=(i,))
    threads.append(t)

for i in range(160):
    t=Thread(target=writer,args=(i,))
    threads.append(t)

for i in range(5):
    t=Thread(target=reader,args=(15+i,))
    threads.append(t)

for t in threads:
    t.start()

for t in threads:
    t.join()