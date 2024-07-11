import json

class Uplink_MQTT:

    @staticmethod
    def Uplink_MQTT(str_line, stop_time, Geoloc_Test, Step, mqtt_data):
        
        global Received_payload_not_modified_x
        Expected_outcome = Geoloc_Test[str(Step)]["Expected_value"]

        Expected_payload = Expected_outcome["payload_hex"]
        Expected_payload = ("").join(Expected_payload.split(" "))
        Expected_payload_length = len(Expected_payload)


        # converting str into dictionary
        Received_payload = json.loads(mqtt_data)
        #print(f"Received payload: {Received_payload}")

        print("Received data from LORA : ", Received_payload)

        Extracted_data = {}
        for i in Expected_outcome.keys():
            if i == "payload_hex":
                # received payload data from mqtt with reduced length of expected payload ex: "123456789"
                Received_payload_trim = Received_payload["DevEUI_uplink"][i][:Expected_payload_length]

                # creating list to store the received payload, ex: [1,2,3,4,5,6,7,8,9]
                Received_payload_list = []
                for i in Received_payload_trim:
                    Received_payload_list.append(i)

                print(Received_payload_list)
                # converting with space of received payload, ex: "12 34 56 78 9"
                Received_payload_not_modified_x = " ".join([Received_payload_trim[i:i + 2] for i in range(0, len(Received_payload_trim), 2)])

                if Expected_payload_length == len(Received_payload_list):
                    # check if the value of expected payload = "x", change the value of received payload = "x"
                    for i in range(Expected_payload_length):
                        if Expected_payload[i] == "x":
                            Received_payload_list[i] = "x"

                # converting the received payload into string, ex : "12xxxx789"
                Received_payload_modified_x = ("").join(Received_payload_list)
                # converting with space of received payload
                Extracted_data["payload_hex"] = " ".join([Received_payload_modified_x[i:i + 2] for i in range(0, len(Received_payload_list), 2)])
            else:
                Extracted_data[i] = int(Received_payload["DevEUI_uplink"][i])


        for i in Expected_outcome.keys():
            # also checks value of the key(payload_hex) : "12 xx xx 56 78 9", is equal to received payload converting into x : "12 xx xx 78 9"
            if Expected_outcome[i] == Extracted_data[i]:
                pass
            else:
                result = "Fail"
                # change into original payload of received payload : "12 34 56 78 9"
                Extracted_data["payload_hex"] = Received_payload_not_modified_x
                return f"\n\n     Expected outcome : \n     {Expected_outcome}\n\n", f"    Received outcome : \n     {Extracted_data}", f"     {result}"
        result = "Pass"
        Extracted_data["payload_hex"] = Received_payload_not_modified_x
        return f"\n\n     Expected outcome : \n     {Expected_outcome}\n\n", f"    Received outcome : \n     {Extracted_data}", f"     {result}"








                    
        


    

       
