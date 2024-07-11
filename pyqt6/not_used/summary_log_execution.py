
import os
import re
import shutil


# current dir
current_dir = os.getcwd()

def summary_log(self, Final_file, Geoloc_Test):

    dir_failed_test = current_dir + "/PyQT_GUI/logs_SM2/Fail_logs"
    dir_all_logs = current_dir + "/PyQT_GUI/logs_SM2/Result_logs_SM2"


    summary_log_name = "Summary_Log.txt"
    summary_log_path = current_dir + "/PyQT_GUI/logs_SM2/" + summary_log_name

    Total_tests = 0
    Total_test_payload = 0
    Total_test_geoloc = 0
    Total_test_uplink_MQTT = 0
    Total_test_downlink_MQTT = 0
    Total_test_lora_link_check = 0

    Total_failed_tests_count = 0
    Total_timeout_fail_count = 0
    Total_loop_error_count = 0

    Failed_payload_tests = 0
    Failed_geoloc_tests = 0
    Failed_uplink_MQTT = 0
    Failed_downlink_MQTT = 0
    Failed_Lora_Link_Check = 0

    Timeout_fail_payload_tests = 0
    Timeout_fail_geoloc_tests = 0
    Timeout_fail_uplink_MQTT = 0
    Timeout_fail_downlink_MQTT = 0
    Timeout_fail_Lora_Link_Check = 0

    Loop_error_payload_tests = 0
    Loop_error_geoloc_tests = 0
    Loop_error_uplink_MQTT = 0
    Loop_error_downlink_MQTT = 0
    Loop_error_Lora_Link_Check = 0

    Total_tests += 1
    if Geoloc_Test["Description"]["Test_callback_function"] == "Payload":
        Total_test_payload += 1
    elif Geoloc_Test["Description"]["Test_callback_function"] == "Geoloc_Timing":
        Total_test_geoloc += 1
    elif Geoloc_Test["Description"]["Test_callback_function"] == "Uplink_MQTT":
        Total_test_uplink_MQTT += 1
    elif Geoloc_Test["Description"]["Test_callback_function"] == "Downlink_MQTT":
        Total_test_downlink_MQTT += 1
    elif Geoloc_Test["Description"]["Test_callback_function"] == "Lora_Link_Check":
        Total_test_lora_link_check += 1

    result_tests = "Pass"
    Path_test_files = dir_all_logs + "/" + Final_file
    Test_case = open(Path_test_files, 'r')    

    while True:
        line = Test_case.readline()
        if not line:
            break
        if re.compile("Fail").search(line):
            result_tests = "Fail"
            shutil.copy(Path_test_files, dir_failed_test)
            if Geoloc_Test["Description"]["Test_callback_function"] == "Payload":
                Failed_payload_tests += 1
            elif Geoloc_Test["Description"]["Test_callback_function"] == "Geoloc_Timing":
                Failed_geoloc_tests += 1
            elif Geoloc_Test["Description"]["Test_callback_function"] == "Uplink_MQTT":
                Failed_uplink_MQTT += 1
            elif Geoloc_Test["Description"]["Test_callback_function"] == "Downlink_MQTT":
                Failed_downlink_MQTT += 1
            elif Geoloc_Test["Description"]["Test_callback_function"] == "Lora_Link_Check":
                Failed_Lora_Link_Check += 1
            Total_failed_tests_count += 1
            break

        elif re.compile("Timeout_fail").search(line):
            result_tests = "Timeout Fail"
            shutil.copy(Path_test_files, dir_failed_test)
            if Geoloc_Test["Description"]["Test_callback_function"] == "Payload":
                Timeout_fail_payload_tests += 1
            elif Geoloc_Test["Description"]["Test_callback_function"] == "Geoloc_Timing":
                Timeout_fail_geoloc_tests += 1
            elif Geoloc_Test["Description"]["Test_callback_function"] == "Uplink_MQTT":
                Timeout_fail_uplink_MQTT += 1
            elif Geoloc_Test["Description"]["Test_callback_function"] == "Downlink_MQTT":
                Timeout_fail_downlink_MQTT += 1
            elif Geoloc_Test["Description"]["Test_callback_function"] == "Lora_Link_Check":
                Timeout_fail_Lora_Link_Check += 1
            Total_timeout_fail_count += 1
            break

        elif re.compile("Loop_error").search(line):
            result_tests = "Loop Error"
            shutil.copy(Path_test_files, dir_failed_test)
            if Geoloc_Test["Description"]["Test_callback_function"] == "Payload":
                Loop_error_payload_tests += 1
            elif Geoloc_Test["Description"]["Test_callback_function"] == "Geoloc_Timing":
                Loop_error_geoloc_tests += 1
            elif Geoloc_Test["Description"]["Test_callback_function"] == "uplink_MQTT":
                Loop_error_uplink_MQTT += 1
            elif Geoloc_Test["Description"]["Test_callback_function"] == "Downlink_MQTT":
                Loop_error_downlink_MQTT += 1
            elif Geoloc_Test["Description"]["Test_callback_function"] == "Lora_Link_Check":
                Loop_error_Lora_Link_Check += 1
            Total_loop_error_count += 1
            break

    Test_case.close()

    summary_result = open(summary_log_path, "w", encoding="UTF-8")

    summary_result.write("\n----------------- SUMMARY QA AT3 -----------------\n\n")
    summary_result.write(f"TOTAL TEST - {Total_tests} \n\n")
    summary_result.write(
        f"TOTAL TEST PASSED : {(Total_tests - (Total_failed_tests_count + Total_timeout_fail_count + Total_loop_error_count))}\n\n")
    summary_result.write(
        f"TOTAL TEST FAILED : {Total_failed_tests_count + Total_timeout_fail_count + Total_loop_error_count}\n\n\n")

    summary_result.write("{:<20} {:<20} {:<20} {:<20} {:<20} {:<20} {:<20}\n\n\n".format("    ", "TOTAL_TEST", "TOTAL_PASS",
                                                                        "TOTAL_FAIL", "RESULT_FAIL",
                                                                        "TIMEOUT_FAIL", "LOOP_ERROR"))

    summary_result.write("{:<23} {:<22} {:<21} {:<20} {:<19} {:<18} {:<17}\n\n\n".format("GEOLOC_TEST", Total_test_geoloc, (Total_test_geoloc - (Failed_geoloc_tests + Timeout_fail_geoloc_tests + Loop_error_geoloc_tests)),
                                                                                        (Failed_geoloc_tests + Timeout_fail_geoloc_tests + Loop_error_geoloc_tests), Failed_geoloc_tests,
                                                                                        Timeout_fail_geoloc_tests, Loop_error_geoloc_tests))

    summary_result.write("{:<23} {:<22} {:<21} {:<20} {:<19} {:<18} {:<17}\n\n\n".format("PAYLOAD_TEST",Total_test_payload, (
                Total_test_payload - (Failed_payload_tests + Timeout_fail_payload_tests + Loop_error_payload_tests)),
                                                                                        (
                                                                                                    Failed_payload_tests + Timeout_fail_payload_tests + Loop_error_payload_tests),
                                                                                        Failed_payload_tests,
                                                                                        Timeout_fail_payload_tests,
                                                                                        Loop_error_payload_tests))

    summary_result.write("{:<23} {:<22} {:<21} {:<20} {:<19} {:<18} {:<17}\n\n\n".format("UPLINK_MQTT",Total_test_uplink_MQTT, (
            Total_test_uplink_MQTT - (Failed_uplink_MQTT + Timeout_fail_uplink_MQTT + Loop_error_uplink_MQTT)),
                                                                                        (
                                                                                                Failed_uplink_MQTT + Timeout_fail_uplink_MQTT + Loop_error_uplink_MQTT),
                                                                                        Failed_uplink_MQTT,
                                                                                        Timeout_fail_uplink_MQTT,
                                                                                        Loop_error_uplink_MQTT))

    summary_result.write("{:<23} {:<22} {:<21} {:<20} {:<19} {:<18} {:<17}\n\n\n".format("DOWNLINK_MQTT",Total_test_downlink_MQTT, (
            Total_test_downlink_MQTT - (Failed_downlink_MQTT + Timeout_fail_downlink_MQTT + Loop_error_downlink_MQTT)),
                                                                                        (
                                                                                                Failed_downlink_MQTT + Timeout_fail_downlink_MQTT + Loop_error_downlink_MQTT),
                                                                                        Failed_downlink_MQTT,
                                                                                        Timeout_fail_downlink_MQTT,
                                                                                        Loop_error_downlink_MQTT))

    summary_result.write(
        "{:<23} {:<22} {:<21} {:<20} {:<19} {:<18} {:<17}\n\n\n".format("LORA_LINK_CHECK", Total_test_lora_link_check, (
                Total_test_lora_link_check - (
                    Failed_Lora_Link_Check + Timeout_fail_Lora_Link_Check + Loop_error_Lora_Link_Check)),
                                                                        (
                                                                                Failed_Lora_Link_Check + Timeout_fail_Lora_Link_Check + Loop_error_Lora_Link_Check),
                                                                        Failed_Lora_Link_Check,
                                                                        Timeout_fail_Lora_Link_Check,
                                                                        Loop_error_Lora_Link_Check))

    summary_result.close()
    
    return result_tests
    