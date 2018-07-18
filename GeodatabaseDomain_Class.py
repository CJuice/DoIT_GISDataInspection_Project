from UtilityClass import UtilityClassFunctionality as myutil
from collections import namedtuple

class GeodatabaseDomains():
    """
    TODO: documentation
    """
    Variable = namedtuple("Variable", "value")  # named tuple definition
    DOMAIN_HEADERS_LIST = Variable(value=("DOM_NAME", "DOM_DESC", "DOM_DOMTYPE", "DOM_DATATYPE", "DOM_CODEDVALKEYS",
                                          "DOM_CODEDVALVALUES", "DOM_RANGE", "DOM_ID", "DATE", "ROW_ID"))
    def __init__(self, environment_name, domain_object, date):
        self.environment_name = environment_name
        self.domain_object = domain_object
        self.date = date
        self.name = domain_object.name
        self.owner = domain_object.owner
        self.description = domain_object.description
        self.domain_type = domain_object.domainType
        self.data_type = domain_object.type
        self.coded_values = domain_object.codedValues
        self.range = domain_object.range
        self.row_id = None

    @property
    def row_id(self):
        return self.__row_id
    @row_id.setter
    def row_id(self, value):
        self.__row_id = myutil.generate_id_from_args(self.name, self.date)
        return

    def create_object_feature_list(self):
        """
        TODO: documentation
        :return:
        """
        domain_ID = myutil.generate_id_from_args(self.environment_name, self.name)
        return [self.name, self.description, self.domain_type, self.data_type,
                              self.domain_object.codedValues.keys(), self.domain_object.codedValues.values(),
                              self.range, domain_ID, self.date, self.row_id]

    def create_object_feature_list_str(self, domain_object_feature_list):
        """
        TODO: documentation
        :param domain_object_feature_list:
        :return:
        """
        return myutil.replace_character_in_list_of_strings(values_list=domain_object_feature_list)

    def create_CSV_domain_properties_string(self, object_feature_list_str):
        """
        TODO: documentation
        :return:
        """
        # domain_ID = myutil.generate_id_from_args(self.environment_name, self.name)
        # record_values_list = [self.name, self.description, self.domain_type, self.data_type,
        #                       self.domain_object.codedValues.keys(), self.domain_object.codedValues.values(),
        #                       self.range, domain_ID, self.date, self.row_id]
        # Handle pre-existing commas in the domain information/data/etc
        # record_values_list = myutil.replace_character_in_list_of_strings(values_list=record_values_list)
        return ",".join(object_feature_list_str)

    def create_zipper(self, headers_list, data_list):
        """
        #TODO: documentation
        :param headers_list:
        :param data_list:
        :return:
        """
        return zip(headers_list, data_list)
