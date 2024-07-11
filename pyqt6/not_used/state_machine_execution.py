
import queue
import paho.mqtt.client as mqtt_client
from datetime import datetime
import time
import sys, os
import json
import re
from Execution_of_Geoloc_Timing import Geoloc_Timing   # import class Geoloc_Timing
from Execution_of_Payload import Payload               # import class Payload 
from Execution_of_Uplink_MQTT import Uplink_MQTT       # import class Uplink_MQTT   
from Execution_of_Downlink_MQTT import Downlink_MQTT   # import class Downlink_MQTT


   


def start_machine_combine(self, Geoloc_Test, ser, log_file_name):
    print("hello")

    DevEUI = "20635FACAB000144"
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


    client = connect_mqtt()
    subscribe(client)

    client.loop_start()

    msgQueue.queue.clear()          # clear lora join payload

    global Expected_outcome, Received_outcome, Result

    for title in Geoloc_Test["Config"]:
        if Geoloc_Test["Config"][title].startswith("sleep"):
            time.sleep(int(Geoloc_Test["Config"][title].split(" ").pop()))
        else:
            ser.write(Geoloc_Test["Config"][title].encode() + b'\r\n')

    dir_logs, directory_result_log, directory_terminal_log = "PyQT_GUI/logs_SM2", "Result_logs_SM2", "Terminal_logs_SM2"

    # get current date and time
    current_datetime = datetime.now().strftime("_%Y-%m-%d_%H-%M-%S")
    result_logs_file_name = log_file_name + str(current_datetime) + ".txt"

    current_dir = os.getcwd()
    result_log_file_path = current_dir + "/" + dir_logs + "/" + directory_result_log + "/" + result_logs_file_name
    result_log_file = open(result_log_file_path, 'w', encoding="UTF-8")

    result_line = "{:<3}\n {:<0}\n\n".format("Description of the test:", Geoloc_Test["Description"]["Test_description"])
    result_log_file.write(result_line)

    result_line = "{:<8} {:<25} {:<10} {:<45} {:<45} {:<10}\n\n\n".format("Step", "State", "Time(s)", "Expected_outcome", "Received_outcome", "Result")
    result_log_file.write(result_line)


    terminal_log_file_path = current_dir + "/" + dir_logs + "/" + directory_terminal_log + "/" + result_logs_file_name
    terminal_log_file = open(terminal_log_file_path, "w")

    Step = 1

    while Geoloc_Test[str(Step)]["State"] != "END":
        line = ser.readline()
        str_line = line.decode()

        sys.stdout.write(str_line)
        terminal_log_file.write(str(str_line))

        State = Geoloc_Test[str(Step)]["State"]

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
            stop_time = time.time() - start_time
            Time = "{:.2f}".format(stop_time)
            if  Geoloc_Test[str(Step)]["Condition"] == True or  re.compile(Geoloc_Test[str(Step)]['Condition'].encode()).search(line):
                start_time = time.time()

                if stop_time <= Geoloc_Test[str(Step)]["Timeout"]:
                    print(f'----- STATE - {Step} {Geoloc_Test[str(Step)]["State"]} DONE -----')
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
                            Expected_outcome, Received_outcome, Result = Downlink_MQTT(str_line, stop_time, Geoloc_Test, Step)


                        result_line = "{:<8} {:<25} {:<10} {:<45} {:<45} {:<10}\n\n\n".format(Step, State, Time, Expected_outcome, Received_outcome, Result)
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
                    Result = "Timeout_Fail"
                    print(f'----- PHASE - TIMEOUT FAIL - {Time} -----')
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
                    print(f'----- PHASE - Loop error - {Time} -----')
                    result_line = "{:<8} {:<25} {:<10} {:<45} {:<45} {:<10} - {} sec\n\n\n".format(Step, State, Time, str(Expected_outcome), Received_outcome, Result, "{:.2f}".format(stop_time))
                    result_log_file.write(result_line)

                    Step = len(Geoloc_Test.keys()) - 2
                    ser.write(b'\r\n')    

    print(f'----- STATE - {Step} END DONE -----')
    State = Geoloc_Test[str(Step)]["State"]
    result_line = "{:<8} {:<25}\n\n\n".format(Step, State)
    result_log_file.write(result_line)

    ser.write(b'sys res\r\n')
    time.sleep(3)
    ser.close()
    result_log_file.close()
    terminal_log_file.close()

    client.loop_stop()
    client.disconnect()  # Disconnect the client
    print("MQTT client disconnected")

    return result_logs_file_name    


