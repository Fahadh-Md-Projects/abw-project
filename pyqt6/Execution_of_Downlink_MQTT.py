import re

class Downlink_MQTT:

    @staticmethod
    def Downlink_MQTT(str_line, stop_time, Geoloc_Test, Step):

        Expected_outcome = Geoloc_Test[str(Step)]["Expected_value"]

        if re.compile("TX#1").search(str_line):

            data_after_tx = str_line.split("TX#1): ")[-1]
            data = ("").join(data_after_tx.split(" "))

            Expected_payload = ("").join(Expected_outcome.split(" "))
            Expected_payload_length = len(Expected_payload)

            Received_payload = data[:Expected_payload_length]

            for i in range(Expected_payload_length):
                if Expected_payload[i] == Received_payload[i]:
                    pass
                elif Expected_payload[i] == "x":
                    pass
                else:
                    Received_outcome_str = " ".join([Received_payload[i:i + 2] for i in range(0, len(Received_payload), 2)])
                    result = "Fail"
                    return f"\n\n     Expected outcome : \n     {Expected_outcome}\n\n", f"    Received outcome : \n     {Received_outcome_str}",  f"     {result}"

            Received_outcome_str = " ".join([Received_payload[i:i + 2] for i in range(0, len(Received_payload), 2)])
            result = "Pass"
            return f"\n\n     Expected outcome : \n     {Expected_outcome}\n\n", f"    Received outcome : \n     {Received_outcome_str}",  f"     {result}"





        else:
            # getting the parameter value
            Extracting_parameter = ("").join(str_line.split(" "))
            left_index = Extracting_parameter.find("=")
            right_index = Extracting_parameter.find("(")

            if right_index == -1:
                Received_parameter = Extracting_parameter[left_index + 1:len(Extracting_parameter)-4] + "}"
            else:
                Received_parameter = Extracting_parameter[left_index + 1:right_index]

        if str(Received_parameter) == str(Expected_outcome):
            return Expected_outcome, Received_parameter, "Pass"
        else:
            return Expected_outcome, Received_parameter, "Fail"     
        

