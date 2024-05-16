import my_parameters
import my_os
import my_serial
import my_crc
import my_server

class Command:
    def __init__(self, data=0, flag=0):
        self.data = data
        self.flag = flag

    def read_connection(self):
        self.data = my_serial.serialUART.ReadSerial()

    def turn_mixer_1_on(self):
        my_serial.serialUART.ser.write(my_crc.crc_calc.export("MIXER1_ON"))
        # turn mixer 1 off

    def turn_mixer_1_off(self):
        my_serial.serialUART.ser.write(my_crc.crc_calc.export("MIXER1_OFF"))

        # turn mixer 2 on
    def turn_mixer_2_on(self):
        my_serial.serialUART.ser.write(my_crc.crc_calc.export("MIXER2_ON"))
        # turn mixer 2 off

    def turn_mixer_2_off(self):
        my_serial.serialUART.ser.write(my_crc.crc_calc.export("MIXER2_OFF"))

        # turn mixer 3 on
    def turn_mixer_3_on(self):
        my_serial.serialUART.ser.write(my_crc.crc_calc.export("MIXER3_ON"))
        # turn mixer 3 off

    def turn_mixer_3_off(self):
        my_serial.serialUART.ser.write(my_crc.crc_calc.export("MIXER3_OFF"))

        # select area 1
    def select_area_1(self):
        my_serial.serialUART.ser.write(my_crc.crc_calc.export("SELECTOR1_ON"))
        # unselect area 1

    def unselect_area_1(self):
        my_serial.serialUART.ser.write(my_crc.crc_calc.export("SELECTOR1_OFF"))

        # select area 2
    def select_area_2(self):
        my_serial.serialUART.ser.write(my_crc.crc_calc.export("SELECTOR2_ON"))
        # unselect area 2

    def unselect_area_2(self):
        my_serial.serialUART.ser.write(my_crc.crc_calc.export("SELECTOR2_OFF"))

        # select area 3
    def select_area_3(self):
        my_serial.serialUART.ser.write(my_crc.crc_calc.export("SELECTOR3_ON"))
        # unselect area 3

    def unselect_area_3(self):
        my_serial.serialUART.ser.write(my_crc.crc_calc.export("SELECTOR3_OFF"))

        # turn in_pump on
    def turn_in_pump_on(self):
        my_serial.serialUART.ser.write(my_crc.crc_calc.export("PUMP_IN_ON"))
        # turn in_pump off

    def turn_in_pump_off(self):
        my_serial.serialUART.ser.write(my_crc.crc_calc.export("PUMP_IN_OFF"))

        # turn out_pump on
    def turn_out_pump_on(self):
        my_serial.serialUART.ser.write(my_crc.crc_calc.export("PUMP_OUT_ON"))
        # turn out_pump off

    def turn_out_pump_off(self):
        my_serial.serialUART.ser.write(my_crc.crc_calc.export("PUMP_OUT_OFF"))

    def get_Temperature(self):
        my_serial.serialUART.ser.write(my_crc.crc_calc.export("SOIL_TEMPERATURE"))

    def get_Humidity(self):
        my_serial.serialUART.ser.write(my_crc.crc_calc.export("SOIL_HUMIDITY"))

command = Command()
count_temp = 0

def my_fsm_temperature():
    global command, count_temp
    data = my_serial.serialUART.ReadSerial()
    if data == -2:
        if count_temp % 10 == 0:   
            my_os.operation_system.add_process(command.get_Temperature)
            print("sent temperature")
        elif count_temp/10 > 3:
            print("time out temperature")
            my_os.operation_system.remove_process(my_fsm_temperature)
            count_temp = 0
    elif data != -2:
        print(data)
        my_server.server_gateway.client.publish("kido2k3/feeds/iot-temperature", data/100)
        my_os.operation_system.remove_process(my_fsm_temperature)
    count_temp += 1

def get_temperature():
    global command, count_temp
    count_temp = 0
    my_os.operation_system.add_process(my_fsm_temperature, 0, 1)
    my_os.operation_system.add_process(command.get_Temperature)

count_humid = 0

def my_fsm_humidity():
    global command, count_humid
    data = my_serial.serialUART.ReadSerial()
    if data == -2:
        if count_humid % 10 == 0:   
            my_os.operation_system.add_process(command.get_Humidity)
            print("sent humidity")
        elif count_humid/10 > 3:
            print("time out humidity")
            my_os.operation_system.remove_process(my_fsm_humidity)
            count_humid = 0
    elif data != -2:
        print(data)
        my_server.server_gateway.client.publish("kido2k3/feeds/iot-humidity", data/100)
        my_os.operation_system.remove_process(my_fsm_humidity)
    count_humid += 1

def get_humidity():
    global command, count_humid
    count_humid = 0
    my_os.operation_system.add_process(my_fsm_humidity, 0, 1)
    my_os.operation_system.add_process(command.get_Humidity)

def my_fsm(state, task, command, count, flag):
    my_os.operation_system.add_process(command.read_connection, 0, 0)
    
    if state == my_parameters.ST_IDLE:
        state = my_parameters.ST_MIXER1
        my_os.operation_system.add_process(command.turn_mixer_1_on)
        print("state mixer1: ", task.mixer[0])
        print("task :", task.id)
    
    elif state == my_parameters.ST_MIXER1:
        if command.data == -2 and command.flag == 0:
            if count % 10 == 0:
                my_os.operation_system.add_process(command.turn_mixer_1_on)
            if count / 10 > 3:
                print("time out1")
                print("state mixer2: ", task.mixer[1])
                my_os.operation_system.add_process(command.turn_mixer_1_off)
                count = 0
                state = my_parameters.ST_MID_1_2
        elif command.data != -2:
            command.flag = 1
            command.count = 0
        else:
            if count >= (task.mixer[0] / my_parameters.SPEED) * 10:
                my_os.operation_system.add_process(command.turn_mixer_1_off)
                count = 0
                state = my_parameters.ST_MID_1_2
                command.flag = 0
                print("state mixer2: ", task.mixer[1])
    
    elif state == my_parameters.ST_MID_1_2:
        if command.data == -2:
            if count % 10 == 0:
                my_os.operation_system.add_process(command.turn_mixer_1_off)
            if count / 10 > 3:
                print("time out turn mixer1 off")
                my_os.operation_system.add_process(command.turn_mixer_2_on)
                state = my_parameters.ST_MIXER2
                count = 0
        elif command.data != -2:
            my_os.operation_system.add_process(command.turn_mixer_2_on)
            state = my_parameters.ST_MIXER2
            count = 0
    
    elif state == my_parameters.ST_MIXER2:
        if command.data == -2 and command.flag == 0:
            if count % 10 == 0:
                my_os.operation_system.add_process(command.turn_mixer_2_on)
            if count / 10 > 3:
                print("time out2")
                print("state mixer3: ", task.mixer[2])
                my_os.operation_system.add_process(command.turn_mixer_2_off)
                count = 0
                state = my_parameters.ST_MID_2_3
        elif command.data != -2:
            command.flag = 1
            command.count = 0
        else:
            if count >= (task.mixer[1] / my_parameters.SPEED) * 10:
                my_os.operation_system.add_process(command.turn_mixer_2_off)
                count = 0
                state = my_parameters.ST_MID_2_3
                command.flag = 0
                print("state mixer3: ", task.mixer[2])
    
    elif state == my_parameters.ST_MID_2_3:
        if command.data == -2:
            if count % 10 == 0:
                my_os.operation_system.add_process(command.turn_mixer_2_off)
            if count / 10 > 3:
                print("time out turn mixer2 off")
                my_os.operation_system.add_process(command.turn_mixer_3_on)
                state = my_parameters.ST_MIXER3
                count = 0
        elif command.data != -2:
            my_os.operation_system.add_process(command.turn_mixer_3_on)
            state = my_parameters.ST_MIXER3
            count = 0
    
    elif state == my_parameters.ST_MIXER3:
        if command.data == -2 and command.flag == 0:
            if count % 10 == 0:
                my_os.operation_system.add_process(command.turn_mixer_3_on)
            if count / 10 > 3:
                print("time out3")
                print("state pump in")
                my_os.operation_system.add_process(command.turn_mixer_3_off)
                count = 0
                state = my_parameters.ST_MID_3_4
        elif command.data != -2:
            command.flag = 1
            command.count = 0
        else:
            if count >= (task.mixer[2] / my_parameters.SPEED) * 10:
                my_os.operation_system.add_process(command.turn_mixer_3_off)
                count = 0
                state = my_parameters.ST_MID_3_4
                command.flag = 0
                print("state pump in")
    
    elif state == my_parameters.ST_MID_3_4:
        if command.data == -2:
            if count % 10 == 0:
                my_os.operation_system.add_process(command.turn_mixer_3_off)
            if count / 10 > 3:
                print("time out turn mixer3 off")
                my_os.operation_system.add_process(command.turn_in_pump_on)
                state = my_parameters.ST_PUMP_IN
                count = 0
        elif command.data != -2:
            my_os.operation_system.add_process(command.turn_in_pump_on)
            state = my_parameters.ST_PUMP_IN
            count = 0
    
    elif state == my_parameters.ST_PUMP_IN:
        if command.data == -2 and command.flag == 0:
            if count % 10 == 0:
                my_os.operation_system.add_process(command.turn_in_pump_on)
            if count / 10 > 3:
                print("time out4")
                print("state selector")
                my_os.operation_system.add_process(command.turn_in_pump_off)
                count = 0
                state = my_parameters.ST_MID_4_5
        elif command.data != -2:
            command.flag = 1
            command.count = 0
        else:
            if count >= 20 * 10:
                my_os.operation_system.add_process(command.turn_in_pump_off)
                count = 0
                state = my_parameters.ST_MID_4_5
                command.flag = 0
                print("state selector")
    
    elif state == my_parameters.ST_MID_4_5:
        if command.data == -2:
            if count % 10 == 0:
                my_os.operation_system.add_process(command.turn_in_pump_off)
            if count / 10 > 3:
                print("time out turn in pump off")
                if task.area == "1":
                    my_os.operation_system.add_process(command.select_area_1)
                elif task.area == "2":
                    my_os.operation_system.add_process(command.select_area_2)
                elif task.area == "3":
                    my_os.operation_system.add_process(command.select_area_3)
                state = my_parameters.ST_SELECTOR
                count = 0
        elif command.data != -2:
            if task.area == "1":
                my_os.operation_system.add_process(command.select_area_1)
            elif task.area == "2":
                my_os.operation_system.add_process(command.select_area_2)
            elif task.area == "3":
                my_os.operation_system.add_process(command.select_area_3)
            state = my_parameters.ST_SELECTOR
            count = 0
    
    elif state == my_parameters.ST_SELECTOR:
        if command.data == -2 and command.flag == 0:
            if count % 10 == 0:
                if task.area == "1":
                    my_os.operation_system.add_process(command.select_area_1)
                elif task.area == "2":
                    my_os.operation_system.add_process(command.select_area_2)
                elif task.area == "3":
                    my_os.operation_system.add_process(command.select_area_3)
            if count / 10 > 3:
                print("time out5")
                print("state pump out")
                my_os.operation_system.add_process(command.turn_out_pump_on)
                count = 0
                state = my_parameters.ST_PUMP_OUT
        elif command.data != -2:
            command.flag = 1
            command.count = 0
        else:
            my_os.operation_system.add_process(command.turn_out_pump_on)
            count = 0
            state = my_parameters.ST_PUMP_OUT
            command.flag = 0
            print("state pump out")
    
    elif state == my_parameters.ST_PUMP_OUT:
        if command.data == -2 and command.flag == 0:
            if count % 10 == 0:
                my_os.operation_system.add_process(command.turn_out_pump_on)
            if count / 10 > 3:
                print("time out6")
                my_os.operation_system.add_process(command.turn_out_pump_off)
                count = 0
                state = my_parameters.ST_MID_6_7
        elif command.data != -2:
            command.flag = 1
            command.count = 0
        else:
            if count >= 20 * 10:
                my_os.operation_system.add_process(command.turn_out_pump_off)
                count = 0
                state = my_parameters.ST_MID_6_7
                command.flag = 0
                task.cycle_num -= 1
    
    elif state == my_parameters.ST_MID_6_7:
        if command.data == -2:
            if count % 10 == 0:
                my_os.operation_system.add_process(command.turn_out_pump_off)
            if count / 10 > 3:
                print("time out turn out pump off")
                if task.area == "1":
                    my_os.operation_system.add_process(command.unselect_area_1)
                elif task.area == "2":
                    my_os.operation_system.add_process(command.unselect_area_2)
                elif task.area == "3":
                    my_os.operation_system.add_process(command.unselect_area_3)
                state = my_parameters.ST_END_STATE
                count = 0
        elif command.data != -2:
            if task.area == "1":
                my_os.operation_system.add_process(command.unselect_area_1)
            elif task.area == "2":
                my_os.operation_system.add_process(command.unselect_area_2)
            elif task.area == "3":
                my_os.operation_system.add_process(command.unselect_area_3)
            state = my_parameters.ST_END_STATE
            count = 0
    
    elif state == my_parameters.ST_END_STATE:
        if command.data == -2 and command.flag == 0:
            if count % 10 == 0:
                if task.area == "1":
                    my_os.operation_system.add_process(command.unselect_area_1)
                elif task.area == "2":
                    my_os.operation_system.add_process(command.unselect_area_2)
                elif task.area == "3":
                    my_os.operation_system.add_process(command.unselect_area_3)
            if count / 10 > 3:
                print("time out7")
                my_parameters.status = my_parameters.DONE
                task.cycle_num -= 1
                count = 0
                flag = False
        elif command.data != -2:
            my_parameters.status = my_parameters.DONE
            task.cycle_num -= 1
            count = 0
    
    count += 1
    return state, task, command, count, flag


class FSM:
    def __init__(self, fsm, task, command, flag=True, count=0) -> None:
        self.state = my_parameters.ST_IDLE
        self.count = count
        self.fsm = fsm
        self.task = task
        self.command = command
        self.flag = flag
        # self.status = status

    def run_fsm(self):
        self.state, self.task, self.command, self.count, self.flag = self.fsm(
            self.state, self.task, self.command, self.count, self.flag)

    def add(self):
        # global operation_system
        my_os.operation_system.add_process(self.run_fsm, 0, 1)

    def rmv(self):
        # global operation_system
        my_os.operation_system.remove_process(self.run_fsm)

    def check(self):
        # global operation_system
        if self.flag == False:
            my_os.operation_system.remove_process(self.run_fsm)

# for testing
# tao file moi de test
# from time import sleep
# from my_mini_task import *
# from my_fsm import *
# from my_task import Task
# from my_mini_task import miniTask

# os = OS()
# task1 = Task("1", 5, [20, 35, 10], "2", "18:30")
# childTask = miniTask(task1)
# print(childTask.area)
# print(childTask.mixer)
# # class_fsm = FSM(my_fsm, childTask.mixer, childTask.area)
# # os.add_process(class_fsm.add)
# # os.add_process(class_fsm.check,0,1)
# os.add_process(childTask.run_task)
# while True:
#     os.dispatch_process()
#     # print(task1.cycle_num)
#     # print(class_fsm.flag)
#     sleep(0.1)
