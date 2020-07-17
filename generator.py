import os
import time
import datetime

def create_log():
    with open("./resources/loremipsum.txt","r") as reader:
        txt = reader.readlines()
    
    
    year = 2020
    month = 6
    day = 0
    hour = 13
    minute = 10
    second = 0

    #custom_data = f'{year}-{month}-{day}'
    for i in range(1,31):           
        custom_data = f'{year}-{month}-{i}'
        for file in range (1,100):
            filename = f"{custom_data}-execution{file}.log"
            with open(f"./bkplogs/{filename}","w+") as f:
                f.writelines(txt)
            date = datetime.datetime(year=year,month=month,day=i,hour=hour,minute=minute,second=second)
            modTime = time.mktime(date.timetuple())
            os.utime(f"./bkplogs/{filename}",(modTime,modTime))
    


if __name__ == '__main__':
    create_log()
    