class GeodatabaseDomains(object):
    def __init__(self, environment_name, domain_object, date):
        self.environment_name = environment_name
        self.int_env_ID = 0
        self.domain_object = domain_object
        self.date = date
        self.name = domain_object.name
        self.owner = domain_object.owner
        self.description = domain_object.description
        self.domain_type = domain_object.domainType
        self.type = domain_object.type
        self.coded_values = domain_object.codedValues
        self.range = domain_object.range
    
    def generate_database_entry_text(self):
        coded_values_keys_list = []
        coded_values_values_list = []
        domain_ID = "{}.{}".format(self.environment_name, self.name)
        try:
            coded_values_keys_list = self.domain_object.codedValues.keys()
        except:
            pass
        try:
            coded_values_values_list = self.domain_object.codedValues.values()
        except:
            pass
        record_values_list = [domain_ID, self.int_env_ID, self.name, self.owner, self.description,
                              self.domain_type, self.type, coded_values_keys_list,
                              coded_values_values_list, self.range, self.date]
        for i in range(len(record_values_list)):
            strTemp = str(record_values_list[i])
            record_values_list[i] = strTemp.replace(",", "|")
        return ",".join(record_values_list)