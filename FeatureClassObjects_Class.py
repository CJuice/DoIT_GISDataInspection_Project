from collections import namedtuple

class FeatureClassObject():
    """
    Create an object for ESRI Feature Class objects generated from arcpy.Describe functionality plus custom values,
    and make available in csv string form for socrata upsert.

    The instance variables are all items to be upserted to Socrata for the Domains dataset. The row_id is generated
    from other attributes and values and serves as the unique ID. All values are not available intitially so default
    values are established on instantiation. Those objects that fail to be calculated in main script thereby have
    values that can be written to output rather than failing due to non existence. The value of -9999 is a database
    flag value. Error value self explanatory.
    """
    Variable = namedtuple("Variable", "value")
    FC_HEADERS_LIST = Variable(value=("Name", "Data Type", "Shape Type", "Total Column Count",
                                             "Total Record Count", "Total Value Count", "Total Null Value Count",
                                             "Percent Null", "Spatial Reference Name", "FD_NAME", "FC_ID",
                                             "DATE", "ROW_ID"))

    def __init__(self, fc_ID, feature_dataset_name, feature_class_name, date_export, row_id):
        self.date_export = date_export
        self.data_type = "ERROR"
        self.fc_ID = fc_ID
        self.fc_name = feature_class_name
        self.fd_name = feature_dataset_name
        self.percent_null = -9999
        self.row_id = row_id
        self.shape_type = "ERROR"
        self.spatial_ref_name = "ERROR"
        self.total_field_count = -9999
        self.total_null_value_count = -9999
        self.total_record_count = -9999
        self.total_value_count = -9999

    def create_CSV_feature_class_properties_string(self, object_features_list_str):
        """
        Join with commas all values in the list of object attributes of interest and return csv string.
        :param object_features_list_str: list of string values
        :return: string of values separated by commas
        """
        return ",".join(object_features_list_str)

    def create_object_feature_list(self):
        """
        Create a list of attributes from instance of class, unformatted to string, and return list
        :return: list of attributes, not formatted to string
        """
        return [self.fc_name, self.data_type, self.shape_type, self.total_field_count,
                                self.total_record_count, self.total_value_count, self.total_null_value_count,
                                self.percent_null, self.spatial_ref_name, self.fd_name, self.fc_ID,
                                self.date_export, self.row_id]

    def create_object_feature_list_str(self, object_features_list):
        """
        Convert objects in list to string if not already of that type and return the list.

        :param object_features_list: list of attributes from instance
        :return: list of string values
        """
        return list(map(str, object_features_list))


class FeatureClassFieldDetails():
    """
    Create an object for ESRI Feature Class Field objects generated from arcpy.Describe fields functionality
    plus custom values, and make available in csv string form for socrata upsert.

    The instance variables are all items to be upserted to Socrata for the Domains dataset. The row_id is generated
    from other attributes and values and serves as the unique ID. The value of -9999 is a database flag value.
    """
    Variable = namedtuple("Variable", "value")
    FIELD_HEADERS_LIST = Variable(value=("Alias", "Name", "Total Null Value Count", "Total Value Count",
                                         "Percent Null", "Type", "Default Value", "Domain", "Is Nullable",
                                         "Length", "Max Character Length Found", "Precision", "Scale", "Required",
                                         "FLD_ID", "FC_ID", "DATE", "ROW_ID"))

    def __init__(self, field_id, fc_id, field_object, total_record_count, total_null_value_count, percent_null,
                 date_export, row_id):
        self.date_export = date_export
        self.fc_ID = fc_id
        self.field_alias = field_object.aliasName.strip()
        self.field_def_value = field_object.defaultValue
        self.field_domain = field_object.domain
        self.field_id = field_id
        self.field_is_nullable = field_object.isNullable
        self.field_length = field_object.length
        self.field_max_chars_used = -9999
        self.field_name = field_object.name.strip()
        self.field_precision = field_object.precision
        self.field_required = field_object.required
        self.field_scale = field_object.scale
        self.field_type = field_object.type
        self.percent_field_null = percent_null
        self.row_id = row_id
        self.total_null_value_count = total_null_value_count
        self.total_record_count = total_record_count

    @property
    def field_domain(self):
        return self.__field_domain

    @field_domain.setter
    def field_domain(self, value):
        if value is None:
            self.__field_domain = "None"
        elif len(str(value).strip()) == 0:
            self.__field_domain = "None"
        elif len(value.strip()) == 0:
            self.__field_domain = "None"
        else:
            self.__field_domain = value
        return

    def create_CSV_feature_class_field_properties_string(self, object_field_features_list_str):
        """
        Join with commas all values in the list of object attributes of interest and return csv string.
        :param object_field_features_list_str: list of string values
        :return: string of values separated by commas
        """
        return ",".join(object_field_features_list_str)

    def create_object_field_feature_list(self):
        """
        Create a list of attributes from instance of class, unformatted to string, and return list
        :return: list of attributes, not formatted to string
        :return:
        """
        return [self.field_alias, self.field_name, self.total_null_value_count, self.total_record_count,
                                self.percent_field_null,
                                self.field_type, self.field_def_value, self.field_domain, self.field_is_nullable,
                                self.field_length, self.field_max_chars_used, self.field_precision, self.field_scale,
                                self.field_required, self.field_id, self.fc_ID, self.date_export, self.row_id]

    def create_object_field_feature_list_str(self, object_field_feature_list):
        """
        Convert objects in list to string if not already of that type and return the list.
        :param object_field_feature_list: list of attributes from instance
        :return: list of string values
        """
        return list(map(str, object_field_feature_list))