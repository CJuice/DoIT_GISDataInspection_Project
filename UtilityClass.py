class UtilityClassFunctionality(object):
    """
    Utility methods for use in scripts or modules.
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
    def build_csv_file_name_with_date(today_date_string, filename):
        """
        Build a string, ending in .csv, that contains todays date and the provided file name and return string

        :param today_date_string: Intended to be the date the file will be created
        :param filename: Name of the file
        :return: string that is 'date_filename.csv'
        """
        return "{}_{}.csv".format(today_date_string, filename)

    @staticmethod
    def build_today_date_string():
        """
        Build a string representing todays date and return string

        :return: string representing date formatted as Year Month Day. Formatted to meet Socrata accepted style
        """
        from datetime import date
        return "{:%Y-%m-%d}".format(date.today())

    @staticmethod
    def calculate_percent(numerator, denominator):
        """
        Calculate the percent of all possible data values, not rows or columns, and return float

        :param numerator: Total number of values
        :param denominator: Denominator in division to calculate percent. Total records, total data values, etc.
        :return: Percent value as a float, rounded to two decimal places
        """
        if denominator == 0:
            return 0.0
        else:
            percent_full_float = float(numerator / denominator) * 100.0
            return round(percent_full_float, 2)

    @staticmethod
    def calculate_total_number_of_null_values_per_dataset(null_counts_list):
        """
        Calculate the total number of null/empty values in a list and return integer sum.

        :param null_counts_list: List of numeric values representing null counts per column in dataset
        :return: Integer value representing total
        """
        return sum(null_counts_list)

    @staticmethod
    def calculate_total_number_of_values_in_dataset(total_records_processed, number_of_fields_in_dataset, database_flag):
        """
        Calculate the total number of values in a dataset from the number of records and columns/fields and return float or database flag

        :param total_records_processed: Total number or records processed
        :param number_of_fields_in_dataset: Total number of columns in the dataset
        :param database_flag: flag used to identify erroneous result
        :return:
        """
        if total_records_processed == database_flag or number_of_fields_in_dataset == database_flag:
            return database_flag
        else:
            return float(total_records_processed * number_of_fields_in_dataset)

    @staticmethod
    def capture_and_print_geoprocessing_errors(func):
        """
        Wrap a function with try and except and return resulting value. Decorator.

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
        Check for path existence and return boolean.

        :param path: The path of interest
        :return: boolean
        """
        import os.path
        if os.path.exists(path):
            return True
        else:
            return False

    @staticmethod
    def create_output_results_file_handler(output_filename):
        """
        Create a file handler and return it.

        If exception occurs, log and exit
        :param output_filename: name of the output file
        :return: handler for opened file
        """
        try:
            fhand = open(output_filename, "a")
        except Exception as e:
            UtilityClassFunctionality.print_and_log(message="File did not open. {}. {}".format(output_filename, e),
                                 log_level=UtilityClassFunctionality.ERROR_LEVEL)
            exit()
        else:
            return fhand

    @staticmethod
    def create_socrata_client(username, password, app_token, maryland_domain):
        """
        Create and return a Socrata connection client.

        Depends on import of sodapy and Socrata from that module
        NOTE: I couldn't pip sodapy to esri python, so i copied folders from python 3.7 installation and
         put in C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\Lib\site-packages
        NOTE: Due to occasional timeout errors, randomly encountered during visualcron runs of the process, the
         timeout value was upped from a default of 10 seconds to a new value of 30 seconds (20180719, CJuice)
        :param username: socrata account username for dataset access
        :param password: socrata account password for dataset access
        :param app_token: token created in socrata for api access
        :param maryland_domain: data.maryland.gov at time of creation
        :return: Socrata connection client
        """
        from sodapy import Socrata
        return Socrata(domain=maryland_domain, app_token=app_token, username=username, password=password, timeout=30)

    @staticmethod
    def get_date_time_for_logging_and_printing():
        """
        Generate a pre-formatted date and time string for logging and printing purposes and return string.

        :return: String Year/Month/Day Hour:Minute:Second usable in logging, and printing statements if desired
        """
        import datetime
        return '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

    @staticmethod
    def generate_id_from_args(*args, separator="."):
        """
        Create a string from args, separated by separator value, and return string.

        :param args: Any number of arguements to be used
        :param separator: Character to separate the args
        :return: String value of args separated by separator
        """
        sep = str(separator)
        arg_stringified_list = [str(arg) for arg in args]
        return sep.join(arg_stringified_list)

    @staticmethod
    def inspect_record_for_null_values(field_null_count_dict, record_dictionary, database_flag):
        """
        Inspect the record for the number of null/empty values and increment the dictionary value but return nothing.

        To avoid false zero values in counter dictionaries the value is initially set to database flag. This function
         checks for database flag value and resets to zero on first time through.
        :param field_null_count_dict: dictionary that counts the nulls for each field in the dataset
        :param record_dictionary: the data record to be evaluated
        :param database_flag: value set in dictionary initialization that is non-zero to avoid false zero in output.
        :return: nothing
        """
        for field_name, value in record_dictionary.items():
            if field_null_count_dict[field_name] == database_flag:
                field_null_count_dict[field_name] = 0
            if value is None:
                field_null_count_dict[field_name] += 1
            elif len(str(value).strip()) == 0:
                field_null_count_dict[field_name] += 1
            elif str(value).strip() == 0:
                field_null_count_dict[field_name] += 1
            else:
                pass
        return

    @staticmethod
    def inspect_string_fields_for_char_usage(field_char_count_dict, record_dictionary, field_name_to_field_object_dictionary):
        """
        Inspect string type fields and track the max character size of all data values in each field but return nothing

        :param field_char_count_dict: keys are field names, values are char count
        :param record_dictionary: record to be evaluated, in dictionary form
        :return: nothing
        """
        for field_name, value in record_dictionary.items():
            field_data_type = field_name_to_field_object_dictionary[field_name].type
            if field_data_type.lower() == "string" and value is not None:
                char_len = len(value)
                if char_len > field_char_count_dict[field_name]:
                    field_char_count_dict[field_name] = char_len
        return

    @staticmethod
    def make_dict_zipper(first_list, second_list):
        """
        Zip headers and data values, typically, and return a dictionary

        :param first_list: List of headers for dataset, often
        :param second_list: List of values in the record, often
        :return: dictionary of zip results
        """
        return dict(zip(first_list, second_list))

    @staticmethod
    def prevent_SQL_error(field_names_list, field_objects_list):
        """
        Prevent a sql error by removing problematic fields and objects from lists.

        Was getting a sql error "Attribute column not found [42S22:[Microsoft][ODBC Driver 13 for SQL Server][SQL
        Server]Invalid column name 'AREA'.]" Needed to remove the problematic fields.
        :param field_names_list: list of fields in feature class
        :param field_objects_list: field objects in list from feature class
        :return:
        """
        remove_these_fields = ["shape", "area", "len", "starea()", "stlength()"]
        field_names_list_for_mod = [name for name in field_names_list]
        for field_name in field_names_list_for_mod:
            if field_name.lower() in remove_these_fields:
                index = field_names_list.index(field_name)
                del field_names_list[index]
                del field_objects_list[index]
        return (field_names_list, field_objects_list)

    @staticmethod
    def print_and_log(message, log_level):
        """
        Print and log any provided message based on the indicated logging level but return nothing.

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
    def process_user_entry_YesNo(user_entry):
        """
        Evaluate the users response to a raw_input for yes or no and pass or return exit()

        Static method in UtilityClass
        :param user_entry: Users entry
        :return: No return, or return exit on fail
        """
        if user_entry.lower() == "y":
            pass
        else:
            return exit()

    @staticmethod
    def replace_character_in_list_of_strings(values_list, character=",", replacement="|"):
        """
        Replace a character in any item in a list of strings and return amended list of strings

        :param values_list: list of string values
        :param character: the character to be replaced
        :param replacement: the replacement character
        :return: list of revised string values
        """
        for i in range(len(values_list)):
            values_list[i] = (str(values_list[i])).replace(character, replacement)
        return values_list

    @staticmethod
    def upsert_to_socrata(client, dataset_identifier, zipper):
        """
        Upsert data to Socrata dataset but return nothing

        Python dictionary is seen as json.
        :param client: Socrata connection client
        :param dataset_identifier: Unique Socrata dataset identifier. Not the data page identifier but the primary page id.
        :param zipper: dictionary of zipped results (headers and data values).
        :return: None
        """
        client.upsert(dataset_identifier=dataset_identifier, payload=zipper, content_type='json')
        return

