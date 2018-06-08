from UtilityClass import UtilityClassFunctionality as myutil

class GeodatabaseDomains(object):
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

    def generate_domain_properties_string(self):
        domain_ID = myutil.generate_id_from_args(self.environment_name, self.name)
        record_values_list = [self.name, self.description, self.domain_type, self.data_type,
                              self.domain_object.codedValues.keys(), self.domain_object.codedValues.values(),
                              self.range, domain_ID, self.date, self.row_id]
        # Handle pre-existing commas in the domain information/data/etc
        record_values_list = myutil.replace_character_in_list_of_strings(values_list=record_values_list)
        return ",".join(record_values_list)
