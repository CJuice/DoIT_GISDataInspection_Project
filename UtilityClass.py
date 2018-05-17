class UtilityClassFunctionality(object):
    """
    Utility methods for use in scripts.
    """

    INFO_LEVEL = "info"
    WARNING_LEVEL = "warning"
    ERROR_LEVEL = "error"

    def __init__(self):
        """
        Initialize UtilityClassFunctionality object

        As of 20171109 all custom methods were static.
        """
        return

    @staticmethod
    def raw_input_basic_checks(raw_input_prompt_sentence):
        """
        Prompt user for input and check for empty entry.

        Static method in UtilityClass
        :param raw_input_prompt_sentence: The prompting language to help user
        :return: String
        """
        import sys
        user_input = None
        while True:
            version = sys.version
            user_input = None
            if version.startswith("2.7."):
                user_input = raw_input(raw_input_prompt_sentence)
            elif version.startswith("3."):
                user_input = input(raw_input_prompt_sentence)
            else:
                exit()
            if user_input == None or len(user_input) == 0:
                pass
            else:
                break
        return user_input

    @staticmethod
    def process_user_entry_YesNo(user_entry):
        """
        Evaluate the users response to a raw_input for yes or no.

        Static method in UtilityClass
        :param user_entry: Users entry
        :return: No return, or return exit on fail
        """
        if user_entry.lower() == "y":
            pass
        else:
            return exit()

    @staticmethod
    def capture_and_print_geoprocessing_errors(func):
        """
        Wrap a function with try and except. Decorator.

        :param func: The ESRI geoprocessing function object
        :return: The resulting value from the tool on successful run, or exit on fail.
        """
        from arcpy import ExecuteError, GetMessages
        def f(*args, **kwargs):

            try:
                result_value = func(*args, **kwargs)
            except ExecuteError:
                UtilityClassFunctionality.print_and_log(
                    message="UtilityClass.captureAndPrintGeoprocessingErrors: Geoprocessing Error.\n{}".format(
                        GetMessages(2)),
                    log_level=UtilityClassFunctionality.ERROR_LEVEL)
                return exit()
            except Exception as e:
                UtilityClassFunctionality.print_and_log(
                    message="UtilityClass.captureAndPrintGeoprocessingErrors: {}".format(e),
                    log_level=UtilityClassFunctionality.ERROR_LEVEL)
                return exit()
            return result_value
        return f

    @staticmethod
    def check_path_exists(path):
        """
        Check for path existence.

        :param path: The path of interest
        :return: No return, or exit on fail
        """
        import os.path
        if os.path.exists(path):
            return True
        else:
            return False

    @staticmethod
    def print_and_log(message, log_level):
        """
        Print and log any provided message based on the indicated logging level.

        :param message:
        :param log_level:
        :return:
        """
        import logging
        message = str(message).rstrip("\n")
        if log_level is UtilityClassFunctionality.INFO_LEVEL:
            logging.info(message)
        elif log_level is UtilityClassFunctionality.WARNING_LEVEL:
            logging.warning(message)
        elif log_level is UtilityClassFunctionality.ERROR_LEVEL:
            logging.error(message)
        print(message)
        return

    @staticmethod
    def get_date_time_for_logging_and_printing():
        """
        Generate a preformatted date and time string for logging and printing purposes.

        :return: String {}/{}/{} UTC[{}:{}:{}] usable in logging, and printing statements if desired
        """
        import datetime
        today_date_time_tuple = datetime.datetime.utcnow().timetuple()
        today_date_time_for_logging = "{}/{}/{} UTC[{}:{}:{}]".format(today_date_time_tuple[0]
                                                                     , today_date_time_tuple[1]
                                                                     , today_date_time_tuple[2]
                                                                     , today_date_time_tuple[3]
                                                                     , today_date_time_tuple[4]
                                                                     , today_date_time_tuple[5])
        return today_date_time_for_logging

    @staticmethod
    def get_date_parts():
        import datetime
        def handle_under_ten(value):
            if value < 10:
                return "0" + str(value)
            else:
                return str(value)
        date_today = datetime.date.today()
        day = handle_under_ten(date_today.day)
        month = handle_under_ten(date_today.month)
        year = str(date_today.year)
        full_date = year + month + day
        date_parts_list = [full_date, year, month, day]
        return date_parts_list
