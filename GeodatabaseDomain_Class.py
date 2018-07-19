from collections import namedtuple
from UtilityClass import UtilityClassFunctionality as myutil

class GeodatabaseDomains():
    """
    Create an object for ESRI geodatabase domain values and make available in csv string form for socrata upsert.

    The instance variables are all items to be upserted to Socrata for the Domains dataset. The row_id is generated
    from other attributes and values and serves as the unique ID.
    """
    Variable = namedtuple("Variable", "value")  # named tuple definition
    DOMAIN_HEADERS_LIST = Variable(value=("Name", "Description", "Domain Type", "Data Type", "Coded Value Keys",
                                          "Coded Value Values", "Range", "DOM_ID", "DATE", "ROW_ID"))

    def __init__(self, environment_name, domain_object, date):
        self.coded_values = domain_object.codedValues
        self.date = date
        self.data_type = domain_object.type
        self.description = domain_object.description
        self.domain_object = domain_object
        self.domain_type = domain_object.domainType
        self.environment_name = environment_name
        self.name = domain_object.name
        self.owner = domain_object.owner
        self.range = domain_object.range
        self.row_id = None

    @property
    def row_id(self):
        return self.__row_id
    @row_id.setter
    def row_id(self, value):
        self.__row_id = myutil.generate_id_from_args(self.name, self.date)
        return

    def create_CSV_domain_properties_string(self, object_feature_list_str):
        """
        Join with commas all values in the list of object attributes of interest and return csv string.
        :param: object_feature_list_str: list of string values
        :return: string of values separated by commas
        """
        return ",".join(object_feature_list_str)

    def create_object_feature_list(self):
        """
        Create a list of attributes from instance of class, unformatted to string, and return list
        :return: list of attributes, not formatted to string
        """
        domain_ID = myutil.generate_id_from_args(self.environment_name, self.name)
        return [self.name, self.description, self.domain_type, self.data_type,
                              self.domain_object.codedValues.keys(), self.domain_object.codedValues.values(),
                              self.range, domain_ID, self.date, self.row_id]

    def create_object_feature_list_str(self, domain_object_feature_list):
        """
        Convert objects in list to string if not already of that type, replace any commas in string with default
        replacement value of util function, and return the list.

        :param domain_object_feature_list: list of attributes from instance
        :return: list of string values
        """
        return myutil.replace_character_in_list_of_strings(values_list=domain_object_feature_list)


