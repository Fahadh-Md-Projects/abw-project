import os
import sys
import time
import datetime
import serial
import serial.tools.list_ports
import re
import json
import queue
import shutil
import paho.mqtt.client as mqtt_client
from pathlib import Path

from PyQt6.QtCore import pyqtSignal, QObject, QThread
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from Execution_of_Geoloc_Timing import Geoloc_Timing   # import class Geoloc_Timing
from Execution_of_Payload import Payload               # import class Payload 
from Execution_of_Uplink_MQTT import Uplink_MQTT       # import class Uplink_MQTT   
from Execution_of_Downlink_MQTT import Downlink_MQTT   # import class Downlink_MQTT


# current dir
global current_dir 
current_dir = os.getcwd()

if sys.platform == "win32":
    forbiden_dir = "\PyQT_GUI\pyqt6"
else:
    forbiden_dir = "/PyQT_GUI/pyqt6"

if(current_dir.find(forbiden_dir)):
    current_dir = current_dir.replace(forbiden_dir,'/')

#  Create a worker class
class Worker(QObject):
    finished = pyqtSignal()                # finished thread signal
    progress = pyqtSignal(str)             # progress thread signal
    stop_signal = pyqtSignal()             # stop thread signal
    trace = pyqtSignal(str)                # trace thread signal
    progress_percentage = pyqtSignal(int)  # progress thread signal
    total_tests_completed = pyqtSignal(int) # total_tests_completed thread signal
    Qmessage_box_error_signal = pyqtSignal(str) # Qmessage box error signal
    final_output_signal = pyqtSignal(dict)      # final output signal 

    def __init__(self, list_controller, w, setup_window_main):
        super().__init__()
        self.list_controller = list_controller
        self.w = w
        self.setup_window_main = setup_window_main
        self._is_running = True
        self.stop_signal.connect(self.stop)

    def run(self):

        current_final_output = {}

        test_types = ["Payload", "Geoloc_Timing", "Uplink_MQTT", "Downlink_MQTT", "Lora_Link_Check"]   # all the test groups

        counters = {                                                                      # its to store the test results
            "Total_tests": 0,
            "Total_test_type": {test_type: 0 for test_type in test_types},
            "Failed_tests": {test_type: 0 for test_type in test_types},
            "Timeout_fail_tests": {test_type: 0 for test_type in test_types},
            "Loop_error_tests": {test_type: 0 for test_type in test_types},
            "Total_failed_tests_count": 0,
            "Total_timeout_fail_count": 0,
            "Total_loop_error_count": 0
        }
        

        print("hello")
        print("----------------- State Machine Started ------------------")
        self.trace.emit("=======> hello")
        self.trace.emit("=======> State machine started")    

        Tests = self.list_controller.x  # list file contains all the selected test cases
        Total_time_every_test_start = time.time()

        for i in range(len(Tests)):
            
            
            if not self._is_running:                     # to stop the test, it checks is_running - true or false
                    break

            ser = self.ser_join()

            if not self._is_running:                     # to stop the test, it checks is_running - true or false
                    break
            
            try:
                self.lora_join(ser)
            except serial.SerialException:               # if it gets the serial exception error, shutdown state machine and show message box 
                error_message_serial = "Unable to perform the test. Please close the serial terminal on your PC."
                self.trace.emit(f"=======> Serial connection error")
                self.Qmessage_box_error_signal.emit(error_message_serial)
                break


            if not self._is_running:                     # to stop the test, it checks is_running - true or false
                    break

            with open(current_dir + "/PyQT_GUI/json_all/" + Tests[i]) as f:
                Geoloc_Test = json.load(f)

            log_file_name = Path(Tests[i]).stem

           
            print("-----------------------------------------------------------------")
            print(f"Running test: -----------------{log_file_name}------------------")
            print("-----------------------------------------------------------------")

            
            self.trace.emit("===========================================================================================================")
            self.trace.emit(f"=======> Running test: {log_file_name}")
            self.trace.emit("===========================================================================================================")

            self.w.running_test_label.setText(f"Running Test : {log_file_name}")             # set the running tests as current log_file_name
 
            
            if self.setup_window_main.checkBox_devEUI.isChecked() == True:
                DevEUI = "20635FACAB000144"
            else:
                DevEUI = self.setup_window_main.lineEdit_devEUI.text()   
            #MQTT execution
            # Define the MQTT broker and port
            broker = 'broker.preview.thingpark.com'
            port = 8883
            username = 'Actility'
            password = 'Tpx2023Forever!'
            topic = f'fahadh/{DevEUI}/uplink'
            msgQueue = queue.LifoQueue()


            def connect_mqtt() -> mqtt_client.Client:
                def on_connect(client, userdata, flags, rc):
                    if rc == 0:
                        print("MQTT Connected successfully")
                        self.trace.emit("=======> MQTT Connected successfully")
                    else:
                        print(f"MQTT Connection failed with code {rc}")

                # Create the MQTT client instance
                client = mqtt_client.Client()
                client.username_pw_set(username, password)
                client.on_connect = on_connect

                # Set TLS parameters and disable SSL certificate verification (for testing only)
                client.tls_set(cert_reqs=mqtt_client.ssl.CERT_NONE)
                client.tls_insecure_set(True)

                client.connect(broker, port)
                return client

            def subscribe(client: mqtt_client.Client):
                def on_message(client, userdata, msg):
                    # print(f"[Info] Received `{msg.payload.decode()}` from `{msg.topic}` topic")
                    msgQueue.put(msg)

                client.subscribe(topic)
                client.on_message = on_message

            def publish(client, downlink_topic, downlink_msg):

                client.publish(downlink_topic, downlink_msg)


            try:
                client = connect_mqtt()
            except TimeoutError:                               # if it gets the Timeout error, shutdown state machine and show message box
                error_message_MQTT = "Unable to connect to MQTT. Please ensure the VPN is enabled on your PC."
                self.trace.emit(f"=======> MQTT connection error")
                self.Qmessage_box_error_signal.emit(error_message_MQTT)
                break
                    
            subscribe(client)

            client.loop_start()

            msgQueue.get()
            msgQueue.queue.clear()          # clear lora join payload

            global Expected_outcome, Received_outcome, Result

            for title in Geoloc_Test["Config"]:
                if Geoloc_Test["Config"][title].startswith("sleep"):
                    time.sleep(int(Geoloc_Test["Config"][title].split(" ").pop()))
                else:
                    ser.write(Geoloc_Test["Config"][title].encode() + b'\r\n')

            dir_logs, directory_result_log, directory_terminal_log = "PyQT_GUI/logs_SM2", "Result_logs_SM2", "Terminal_logs_SM2"

            # get current date and time
            current_datetime = datetime.datetime.now().strftime("_%Y-%m-%d_%H-%M-%S")
            result_logs_file_name = log_file_name + str(current_datetime) + ".txt"

            
            result_log_file_path = current_dir + "/" + dir_logs + "/" + directory_result_log + "/" + result_logs_file_name
            result_log_file = open(result_log_file_path, 'w', encoding="UTF-8")

            result_line = "{:<3}\n {:<0}\n\n".format("Description of the test:", Geoloc_Test["Description"]["Test_description"])
            result_log_file.write(result_line)

            result_line = "{:<8} {:<25} {:<10} {:<45} {:<45} {:<10}\n\n\n".format("Step", "State", "Time(s)", "Expected_outcome", "Received_outcome", "Result")
            result_log_file.write(result_line)


            terminal_log_file_path = current_dir + "/" + dir_logs + "/" + directory_terminal_log + "/" + result_logs_file_name
            terminal_log_file = open(terminal_log_file_path, "w")

            Step = 1

            
            Total_start_time = time.time()
            result_flag = True
            result_timeout_flag = True
            result_looperror_flag = True

            while Geoloc_Test[str(Step)]["State"] != "END":

                if not self._is_running:                    # to stop the test, it checks is_running - true or false
                    break

                line = ser.readline()

                str_line = line.decode()

                sys.stdout.write(str_line)
                terminal_log_file.write(str_line)
                self.trace.emit(line[:-2].decode())

                State = Geoloc_Test[str(Step)]["State"]

                progress_value = int((Step / (len(Geoloc_Test.keys())-2)) * 100)   # calculation of progress bar value
                self.progress_percentage.emit(progress_value)                      # sending progress bar value

                if Geoloc_Test[str(Step)]["Action"] != None:

                    if Geoloc_Test[str(Step)]["Action"].startswith("sleep"):
                        ser.write(b'\r\n')
                        start_time = time.time()
                        time.sleep(int(Geoloc_Test[str(Step)]["Action"].split(" ").pop()))
                        ser.write(b'\r\n')
                    elif Geoloc_Test[str(Step)]["Action"].startswith("publish"):
                        start_time = time.time()
                        downlink_payload = Geoloc_Test[str(Step)]["Action"].split(" ").pop()
                        downlink_msg = {
                                        "DevEUI_downlink": {
                                            "Time": "2029-07-10T15:38:46.882+02:00",
                                            "DevEUI": DevEUI,
                                            "FPort": 3,
                                            "payload_hex": downlink_payload
                                        }
                                    }
                        downlink_topic = f'fahadh/{DevEUI}/downlink'
                        publish(client, downlink_topic, json.dumps(downlink_msg))
                        print(f"Published downlink payload : {downlink_payload}")
                        ser.write(b'\r\n')
                    else:
                        ser.write(b'\r\n')
                        ser.write(Geoloc_Test[str(Step)]["Action"].encode() + b'\r\n')
                        ser.write(b'\r\n')
                        start_time = time.time()
                    Geoloc_Test[str(Step)]["Action"] = None


                else:

                    if not self._is_running:                        # to stop the test, it checks is_running - true or false
                        break

                    stop_time = time.time() - start_time
                    Time = "{:.2f}".format(stop_time)
                    if  Geoloc_Test[str(Step)]["Condition"] == True or  re.compile(Geoloc_Test[str(Step)]['Condition'].encode()).search(line):
                        start_time = time.time()

                        if stop_time <= Geoloc_Test[str(Step)]["Timeout"]:
                            print(f'----- STATE - {Step} {Geoloc_Test[str(Step)]["State"]} DONE -----')
                            self.trace.emit(f"=======> STATE - {Step} {Geoloc_Test[str(Step)]['State']} DONE")
                            if Geoloc_Test[str(Step)]["Result"] == "to check":

                                if Geoloc_Test["Description"]["Test_callback_function"] == "Geoloc_Timing" or Geoloc_Test["Description"]["Test_callback_function"] == "Lora_Link_Check":
                                    Expected_outcome, Received_outcome, Result = Geoloc_Timing.Geoloc_Timing(str_line, stop_time, Geoloc_Test, Step)
                                elif Geoloc_Test["Description"]["Test_callback_function"] == "Payload":
                                    Expected_outcome, Received_outcome, Result = Payload.Payload(str_line, stop_time, Geoloc_Test, Step)
                                elif Geoloc_Test["Description"]["Test_callback_function"] == "Uplink_MQTT":
                                    message = msgQueue.get()  # Blocking call, will wait until a message is available
                                    mqtt_data = message.payload.decode()
                                    Expected_outcome, Received_outcome, Result = Uplink_MQTT.Uplink_MQTT(str_line, stop_time, Geoloc_Test, Step, mqtt_data)
                                    result_log_file.write(mqtt_data + "\n\n")
                                elif Geoloc_Test["Description"]["Test_callback_function"] == "Downlink_MQTT":
                                    Expected_outcome, Received_outcome, Result = Downlink_MQTT.Downlink_MQTT(str_line, stop_time, Geoloc_Test, Step)


                                result_line = "{:<8} {:<25} {:<10} {:<45} {:<45} {:<10}\n\n\n".format(Step, State, Time, Expected_outcome, Received_outcome, Result)

                                if Result.strip() == "Fail":

                                    result_flag, state_fail = False, Step
                            else:
                                Expected_outcome, Received_outcome, Result = "N/A","N/A"," "
                                result_line = "{:<8} {:<25} {:<10} {:<45} {:<45} {:<10}\n\n\n".format(Step, State, Time, Expected_outcome, Received_outcome, Result)

                            Step += 1
                            ser.write(b'\r\n')    

                        else:

                            if Geoloc_Test[str(Step)]["Expected_value"] != None:
                                Expected_outcome, Received_outcome = Geoloc_Test[str(Step)]["Expected_value"], " "
                            else:
                                Expected_outcome, Received_outcome = "N/A", "N/A"
                            Result = "Timeout_fail"
                            result_timeout_flag, state_timeout_fail = False, Step
                            print(f'----- PHASE - TIMEOUT FAIL - {Time} -----')
                            self.trace.emit(f"=======> PHASE - TIMEOUT FAIL - {Time}")
                            result_line = "{:<8} {:<25} {:<10} {:<45} {:<45} {:<10} - {} sec\n\n\n".format(Step, State, Time, str(Expected_outcome), Received_outcome, Result, "{:.2f}".format(stop_time))
                            Step = len(Geoloc_Test.keys()) - 2
                            ser.write(b'\r\n')

                        result_log_file.write(result_line)

                    else:
                        # 300 --> 5 min
                        if stop_time >= 300:
                            if Geoloc_Test[str(Step)]["Result"] == "to check":
                                Expected_outcome = Geoloc_Test[str(Step)]["Expected_value"]
                            else:
                                Expected_outcome = "N/A"

                            Received_outcome, Result =" ", "Loop_error"
                            result_looperror_flag, state_looperror_fail = False, Step
                            print(f'----- PHASE - LOOP ERROR - {Time} -----')
                            self.trace.emit(f"=======> PHASE - LOOP ERROR - {Time}")
                            result_line = "{:<8} {:<25} {:<10} {:<45} {:<45} {:<10} - {} sec\n\n\n".format(Step, State, Time, str(Expected_outcome), Received_outcome, Result, "{:.2f}".format(stop_time))
                            result_log_file.write(result_line)

                            Step = len(Geoloc_Test.keys()) - 2
                            ser.write(b'\r\n')    

            print(f'----- STATE - {Step} END DONE -----')
            self.trace.emit(f"=======> STATE - {Step} END DONE")
            State = Geoloc_Test[str(Step)]["State"]

            Total_stop_time = time.time() - Total_start_time

            result_line = "{:<8} {:<25}\n\n\n".format(Step, State)
            result_log_file.write(result_line)


            if result_timeout_flag == False :
                    result_tests = "Timeout"
                    result_log_file.write(f"Test Result : {result_tests} at State {state_timeout_fail}\n")
            elif result_looperror_flag == False :
                    result_tests = "Loop Error"
                    result_log_file.write(f"Test Result : {result_tests} at State {state_looperror_fail}\n")
            elif result_flag == False :
                    result_tests = "Fail"
                    result_log_file.write(f"Test Result : {result_tests} at State {state_fail}\n")
            elif result_flag == True :
                    result_tests = "Pass"
                    result_log_file.write(f"Test Result : {result_tests}\n")       

            result_log_file.write(f"Total Test Time : {int(Total_stop_time)} sec")

            result_log_file.close() 

            ser.write(b'sys res\r\n')
            time.sleep(3)
            ser.close()
            terminal_log_file.close()

            client.loop_stop()
            client.disconnect()  # Disconnect the client
            print("MQTT client disconnected")
            self.trace.emit("=======> MQTT client disconnected")
            self.progress_percentage.emit(100)                      # sending progress bar value into 100
            self.progress_percentage.emit(0)                        # return progress bar value into 0
            self.total_tests_completed.emit(i+1)                    # sending total_tests_completed value


            dir_failed_test = os.path.join(current_dir, "PyQT_GUI", "logs_SM2", "Fail_logs")
            dir_all_logs = os.path.join(current_dir, "PyQT_GUI", "logs_SM2", "Result_logs_SM2")

            summary_log_name = "Summary_Log.txt"
            summary_log_path = os.path.join(current_dir, "PyQT_GUI", "logs_SM2", summary_log_name)

            

            counters["Total_tests"] += 1
            test_callback_function = Geoloc_Test["Description"]["Test_callback_function"]
            
            if test_callback_function in test_types:
                counters["Total_test_type"][test_callback_function] += 1

            #result_tests = "Pass"
            Path_test_files = os.path.join(dir_all_logs, result_logs_file_name)
            print(Path_test_files)
            
            with open(Path_test_files, 'r') as Test_case:
                for line in Test_case:
                    if re.search("Fail", line):
                        #result_tests = "Fail"
                        shutil.copy(Path_test_files, dir_failed_test)
                        counters["Failed_tests"][test_callback_function] += 1
                        counters["Total_failed_tests_count"] += 1
                        break
                    elif re.search("Timeout_fail", line):
                        #result_tests = "Timeout"
                        shutil.copy(Path_test_files, dir_failed_test)
                        counters["Timeout_fail_tests"][test_callback_function] += 1
                        counters["Total_timeout_fail_count"] += 1
                        break
                    elif re.search("Loop_error", line):
                        #result_tests = "Loop Error"
                        shutil.copy(Path_test_files, dir_failed_test)
                        counters["Loop_error_tests"][test_callback_function] += 1
                        counters["Total_loop_error_count"] += 1
                        break 

            with open(summary_log_path, "w", encoding="UTF-8") as summary_result:
                summary_result.write("\n----------------- SUMMARY QA AT3 -----------------\n\n")
                summary_result.write(f"TOTAL TEST - {counters['Total_tests']} \n\n")
                summary_result.write(
                    f"TOTAL TEST PASSED : {(counters['Total_tests'] - (counters['Total_failed_tests_count'] + counters['Total_timeout_fail_count'] + counters['Total_loop_error_count']))}\n\n")
                summary_result.write(
                    f"TOTAL TEST FAILED : {counters['Total_failed_tests_count'] + counters['Total_timeout_fail_count'] + counters['Total_loop_error_count']}\n\n\n")
                
                summary_result.write("{:<20} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20}\n\n\n".format("    ", "TOTAL_TEST", "TOTAL_PASS",
                                                                                                "TOTAL_FAIL", "RESULT_FAIL",
                                                                                                "TIMEOUT_FAIL", "LOOP_ERROR"))
                
                for test_type in test_types:
                    total_tests = counters["Total_test_type"][test_type]
                    failed_tests = counters["Failed_tests"][test_type]
                    timeout_tests = counters["Timeout_fail_tests"][test_type]
                    loop_error_tests = counters["Loop_error_tests"][test_type]
                    total_failed = failed_tests + timeout_tests + loop_error_tests
                    total_pass = total_tests - total_failed
                    
                    summary_result.write("{:<23} {:<22} {:<21} {:<20} {:<19} {:<18} {:<17}\n\n\n".format(
                        f"{test_type}_TEST", total_tests, total_pass, total_failed, failed_tests, timeout_tests, loop_error_tests))
                    
                self.w.passed_test_label.setText(f"Passed Test : {(counters['Total_tests'] - (counters['Total_failed_tests_count'] + counters['Total_timeout_fail_count'] + counters['Total_loop_error_count']))}") # update passed tests and failed tests in the main window 
                self.w.failed_test_label.setText(f"Failed Test : {counters['Total_failed_tests_count'] + counters['Total_timeout_fail_count'] + counters['Total_loop_error_count']}") 

            current_final_output[Path(result_logs_file_name).stem] = result_tests + " - " + str(int(Total_stop_time)) + " sec"  # storing final output

            self.final_output_signal.emit(current_final_output)      # emitting final ouput

        Total_time_every_test_stop = time.time() - Total_time_every_test_start
        self.progress.emit("----------------- State Machine Terminated ----------------")            # progress signal emitted from here  
        self.trace.emit("=======> Total time taken to complete all the tests : " + str(datetime.timedelta(seconds=int(Total_time_every_test_stop))))
        self.trace.emit("=======> State machine shutdown successfully")            # progress signal emitted from here  
        self.finished.emit()

    def stop(self):
        self._is_running = False
        self.trace.emit("=======> State machine - Shutdown requested")
        self.trace.emit("=======> Please wait...")


    def ser_join(self):

        mData = None  # Initialize mData to None
        
        try:
            ports = list(serial.tools.list_ports.comports())
            print("[ + ] INFORMATION CARTE")
            print("      Description : ")
            for p in ports:
                print("         - ", p.description)
                if "STM" in p.description:
                    mData = serial.Serial(p.device, 57600)
            if mData and mData.is_open:
                print("      Carte connectée : ", mData.is_open)
                print("      Port : ", mData.name)
                self.trace.emit(f"=======> STM device connected to the Port : {mData.name}")
                return mData
            else:
                raise Exception("STM device not found")
        except Exception as e:                     # if it gets the port error, shutdown state machine and show message box
            print(f"Error: {str(e)}")
            error_message_port = "STM device not found. Please check if the device is connected to the USB port."
            self._is_running = False
            self.trace.emit(f"=======> {str(e)}")
            self.Qmessage_box_error_signal.emit(error_message_port)
            

    def lora_join(self, ser):
        ser.write(b'456\r\n')
        ser.write(b'sys res\r\n')
        time.sleep(5)
        pattern = re.compile(b'TX success')
        print("Waiting for lora connection")
        self.trace.emit(f"=======> Waiting for lora connection")

        while True:
             
            line = ser.readline()
            print(line)

            if not self._is_running:
                break

            if pattern.search(line):
                print("----- PHASE - LORA_JOIN --> Got Lora Join success -----")
                self.trace.emit(f"=======> Lora connected successfully")
                break
        ser.write(b'456\r\n')
        ser.write(b'conf erase\r\n')
        time.sleep(5)

        


class initiate_statemachine:

    def __init__(self, w, list_controller, log_window_list_controller, Logs_window_main, setup_window_main):
        self.w = w
        self.list_controller = list_controller
        self.log_window_list_controller = log_window_list_controller
        self.Logs_window_main = Logs_window_main
        self.setup_window_main = setup_window_main
        self.current_final_output = {}    # created dictionary to store the tests results
        self.setup_startbutton()

    def setup_startbutton(self):
        self.w.Start_Test.clicked.connect(self.initiate)               # initiate the state machine
        self.w.Stop_Test.clicked.connect(self.terminate)               # terminate the state machine
        self.w.clear_trace.clicked.connect(self.clear_all_traces)      # clear all traces
        self.Logs_window_main.comboBox_select_tests.currentTextChanged.connect(self.update_final_output_manual_to_current_listwidget) # update the final output to list, when combo box is changed into "Current Tests" 
        self.Logs_window_main.Search_test_button.clicked.connect(self.filter_tests)  # filter the files based on the search
        self.Logs_window_main.checkBox_show_only_failed_tests.stateChanged.connect(self.show_only_failed_tests) # if checkbox changed, show only failed tests.

    def initiate(self):
        self.w.Start_Test.setEnabled(False)                            # after initiate restrict access to start button 
        self.w.my_test_lists.setEnabled(False)                         # after initiate restrict access to test lists
        self.w.Stop_Test.setEnabled(True)                              # after initiate allow access to stop button
        self.w.Select_all.setEnabled(False)                            # after initiate restrict access to select all button
        self.w.Clear_all.setEnabled(False)                             # after initiate restrict access to clear all button
        self.w.comboBox_test_group.setEnabled(False)                   # after initiate restrict access to combo box test group
        self.w.clear_trace.setEnabled(False)                           # after initiate restrict access to clear trace button
        self.w.total_test_completed_label.setText(f"Total number of test completed : 0 of {len(self.list_controller.x)}") # after initiate set total test number 
        self.Logs_window_main.total_test_completed_label_log.setText(f"Total number of test completed : 0 of {len(self.list_controller.x)}") # after initiate set total test number 
        self.w.Setup_button.setEnabled(False)                          # disable the setupe button after initiate

        
        self.thread = QThread()                         # Create a QThread object
        self.worker = Worker(self.list_controller, self.w, self.setup_window_main)      # Create a worker object
        self.worker.moveToThread(self.thread)           # Move worker to the thread
        # Connect signals and slots
        self.thread.started.connect(self.worker.run)    
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.report_progress)
        self.worker.Qmessage_box_error_signal.connect(self.qmessage_box_error)
        self.worker.trace.connect(self.update_trace)
        self.worker.total_tests_completed.connect(self.update_total_test_completed)
        self.worker.progress_percentage.connect(self.update_progress_bar)
        self.worker.final_output_signal.connect(self.update_final_output_automatic_to_current_listwidget)   # update the result listwidget automatically when the combo box named "Current Tests"
        self.thread.finished.connect(self.after_finish_configure)

        self.thread.start()                             # Start the thread

    def report_progress(self, message):
        print(message)  # Or update a GUI element
        
           
    def terminate(self):                                
        self.worker.stop_signal.emit()                  # send stop signal after stop button is clicked
        self.w.Stop_Test.setEnabled(False)              # disable stop button when state machine terminated
        

    def after_finish_configure(self):
        self.w.Start_Test.setEnabled(True)              # enable start button when state machine terminted 
        self.w.Stop_Test.setEnabled(False)              # disable stop button when state machine terminated
        self.w.my_test_lists.setEnabled(True)           # enable test lists when state machine terminated  
        self.w.Select_all.setEnabled(True)              # enable select all button when state machine terminated     
        self.w.Clear_all.setEnabled(True)               # enable clear all button when state machine terminated
        self.w.clear_trace.setEnabled(True)             # enable clear trace button when state machine terminated
        self.w.comboBox_test_group.setEnabled(True)     # enable combo box test group when state machine terminated 
        self.w.running_test_label.setText(f"Running Test : None")  # change the running label into None
        self.w.Setup_button.setEnabled(True)            # enable setup button after state machine terminated
        
 
    def update_trace(self, trace_output):
        self.w.textEdit_trace.append(trace_output)      # showcasing traces in the trace_editor

    def clear_all_traces(self):
        self.w.textEdit_trace.clear()                   # clearing the traces in the trace_editor

    def update_progress_bar(self, progress_output):
        self.w.progressBar.setValue(progress_output)    # updating progress bar

    def update_total_test_completed(self, total_test_completed_output):
        self.w.total_test_completed_label.setText(f"Total number of test completed : {total_test_completed_output} of {len(self.list_controller.x)}")  # updating total test 
        self.Logs_window_main.total_test_completed_label_log.setText(f"Total number of test completed : {total_test_completed_output} of {len(self.list_controller.x)}") 

    def qmessage_box_error(self, message):              # message box to show the problem 
        dlg = QtWidgets.QMessageBox()
        dlg.setWindowTitle("Connection Error")
        dlg.setText(message)
        dlg.setIcon(QtWidgets.QMessageBox.Icon.Question)
        dlg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        button = dlg.exec()

        if button == QtWidgets.QMessageBox.StandardButton.Ok:
            print("OK!")

    def update_final_output_automatic_to_current_listwidget(self, current_final_output):  # update the result listwidget automatically when the combo box named "Current Tests"

        self.current_final_output = current_final_output                                  # store the results
        if self.Logs_window_main.comboBox_select_tests.currentText() == "Current Tests" :
            
            self.Logs_window_main.checkBox_show_only_failed_tests.setCheckState(Qt.CheckState.Unchecked)

            self.log_window_list_controller.update_current_and_previous_tests(self.current_final_output, self.Logs_window_main.listWidget_current_test)

    def update_final_output_manual_to_current_listwidget(self, group_name):   # update the current tests results when combo box changed into "Current Tests"
        if group_name == "Current Tests":
            self.log_window_list_controller.update_current_and_previous_tests(self.current_final_output, self.Logs_window_main.listWidget_current_test)



    def filter_tests(self):
        filter_dict = {}
        filter_test_name = self.Logs_window_main.lineEdit_search_test_file.text()  # get the text of line_edit

        if self.Logs_window_main.comboBox_select_tests.currentText() == "Current Tests":  # if combo box == "Current Tests", only use final output
            tests_results = self.current_final_output
        else:
            tests_results = self.log_window_list_controller.previous_tests()            # if the combo box == "Previous Tests", get the previous results
         
        for test_name, results in tests_results.items():
            if self.Logs_window_main.checkBox_show_only_failed_tests.isChecked():
                if test_name.startswith(filter_test_name) and not results.startswith("Pass"):  # if show only failed tests checkbox is checked, show only failed result
                    filter_dict.update({test_name:results})
            else:
                if test_name.startswith(filter_test_name):
                    filter_dict.update({test_name:results})        
            
        self.log_window_list_controller.update_current_and_previous_tests(filter_dict, self.Logs_window_main.listWidget_current_test)     


    def show_only_failed_tests(self, s):
        store_only_failed_tests_dict = {}

        if s ==  Qt.CheckState.Checked.value:
            if self.Logs_window_main.comboBox_select_tests.currentText() == "Previous Tests":   # if show only failed tests checkbox is checked, get the requird output
                tests_results = self.log_window_list_controller.previous_tests()
            else:    
                tests_results = self.current_final_output

            for test_name, results in tests_results.items():         # only list failed files
                if not results.startswith("Pass"):
                    store_only_failed_tests_dict.update({test_name:results})
                
            self.log_window_list_controller.update_current_and_previous_tests(store_only_failed_tests_dict, self.Logs_window_main.listWidget_current_test)

        elif self.Logs_window_main.comboBox_select_tests.currentText() == "Previous Tests":  # if its unchecked and combo box is "Previous Tests", show all previous
            old_tests_results = self.log_window_list_controller.previous_tests()                                                                   # call previous_tests() function to update the previous completed tests                                                                     
            self.log_window_list_controller.update_current_and_previous_tests(old_tests_results, self.Logs_window_main.listWidget_current_test)

        elif self.Logs_window_main.comboBox_select_tests.currentText() == "Current Tests":  # if its unchecked and combo box is "current Tests", show current output results  
            self.log_window_list_controller.update_current_and_previous_tests(self.current_final_output, self.Logs_window_main.listWidget_current_test)       





        
            
            
            
        

