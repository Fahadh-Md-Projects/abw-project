class Geoloc_Timing:

    @staticmethod
    def Geoloc_Timing(str_line, stop_time, Geoloc_Test, Step):
        Expected_outcome = Geoloc_Test[str(Step)]["Expected_value"]

        if int(stop_time) in range((Expected_outcome - 2), (Expected_outcome + 2)):
            result = "Pass"
        else:
            result = "Fail"
        return Expected_outcome, "{:.2f}".format(stop_time), result
