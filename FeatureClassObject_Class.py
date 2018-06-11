from collections import namedtuple

class FeatureClassObject():
    """
    #TODO
    """
    # Class to hold feature class objects from the arcpy.Describe functionality
    Variable = namedtuple("Variable", "value")  # named tuple definition
    FC_HEADERS_LIST = Variable(value=("FC_NAME", "FC_DATATYPE", "FC_SHAPETYPE", "FC_TOTALCOLUMNCOUNT",
                                             "FC_FEATURECOUNT", "FC_TOTALVALUECOUNT", "FC_TOTALNULLVALUECOUNT",
                                             "FC_PERCENTNULL", "FC_SPATIALREFNAME", "FD_NAME", "FC_ID",
                                             "DATE", "ROW_ID"))

    def __init__(self, fc_ID, feature_dataset_name, feature_class_name, date_export, row_id):
        self.data_type = "ERROR"
        self.date_export = date_export
        self.fc_name = feature_class_name
        self.fc_ID = fc_ID
        self.fd_name = feature_dataset_name
        self.percent_null = -9999
        self.row_id = row_id
        self.shape_type = "ERROR"
        self.spatial_ref_name = "ERROR"
        self.total_field_count = -9999
        self.total_null_value_count = -9999
        self.total_record_count = -9999
        self.total_value_count = -9999

    def generate_feature_class_properties_string(self):
        object_features_list = [self.fc_name, self.data_type, self.shape_type, self.total_field_count,
                                self.total_record_count, self.total_value_count, self.total_null_value_count,
                                self.percent_null, self.spatial_ref_name, self.fd_name, self.fc_ID,
                                self.date_export, self.row_id]
        string_list = list(map(str, object_features_list))
        return ",".join(string_list)

class FeatureClassFieldDetails():
    """
    #TODO
    """
    # Class to hold the details on the feature class fields using the arpy.Describe fields info
    Variable = namedtuple("Variable", "value")  # named tuple definition
    FIELD_HEADERS_LIST = Variable(value=("FLD_ALIAS", "FLD_NAME", "FLD_TOTALNULLVALUECOUNT", "FLD_TOTALVALUECOUNT",
                                         "FLD_PERCENTNULL", "FLD_TYPE", "FLD_DEF_VAL", "FLD_DOMAIN", "FLD_ISNULLABLE",
                                         "FLD_LENGTH", "FLD_MAXCHARLEN", "FLD_PRECISION", "FLD_SCALE", "FLD_REQUIRED",
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
        elif len(str(value)) == 0:
            self.__field_domain = "None"
        elif len(value.strip()) == 0:
            self.__field_domain = "None"
        else:
            pass
        return

    def generate_feature_class_field_properties_string(self):
        object_features_list = [self.field_alias, self.field_name, self.total_null_value_count, self.total_record_count, self.percent_field_null,
                                self.field_type, self.field_def_value, self.field_domain, self.field_is_nullable,
                                self.field_length, self.field_max_chars_used, self.field_precision, self.field_scale,
                                self.field_required, self.field_id, self.fc_ID, self.date_export, self.row_id]
        string_list = list(map(str, object_features_list))
        return ",".join(string_list)


