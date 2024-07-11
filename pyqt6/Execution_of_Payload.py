class Payload:

    @staticmethod
    def Payload(str_line, stop_time, Geoloc_Test, Step):
        Expected_outcome = Geoloc_Test[str(Step)]["Expected_value"]

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
                return Expected_outcome, " ".join(
                    [Received_payload[i:i + 2] for i in range(0, len(Received_payload), 2)]), "Fail"

        return Expected_outcome, " ".join([Received_payload[i:i + 2] for i in range(0, len(Received_payload), 2)]), "Pass"   