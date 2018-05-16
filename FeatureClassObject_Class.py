class FeatureClassObject(object):
    # Class to hold feature class objects from the arcpy.Describe functionality
    def __init__(self, fc_ID, ADM_ID, feature_dataset, feature_class_name, arcpy_describe_object, date_export):
        self.fc_ID = fc_ID
        self.ADM_ID = ADM_ID
        self.feature_dataset = feature_dataset
        self.fc_name = feature_class_name
        self.fc_feature_count = -9999
        self.arcpy_describe_object = arcpy_describe_object
        self.data_type = arcpy_describe_object.dataType
        self.shape_type = arcpy_describe_object.shapeType
        self.spatial_ref_name = arcpy_describe_object.spatialReference.name
        self.date_export = date_export

        
    def writeFeatureClassProperties(self):
        object_features_list = [self.fc_ID, self.ADM_ID, self.feature_dataset, self.fc_name, self.data_type,
                                self.shape_type, self.spatial_ref_name, self.fc_feature_count, self.date_export]
        for i in range(len(object_features_list)):
            object_features_list[i] = str(object_features_list[i])
        return ",".join(object_features_list)
    

class FeatureClassFieldDetails(object):
    # Class to hold the details on the feature class object fields using the arpy.Describe fields info
    def __init__(self, feature_class_fields_list, field_ID, feature_class_ID, field):
        self.feature_class_fields_list = feature_class_fields_list
        self.field_ID = field_ID
        self.fc_ID = feature_class_ID
        self.field_alias = field.aliasName.strip()
        self.field_name = field.name.strip()
        self.field_type = field.type
        self.field_def_value = field.defaultValue
        self.field_domain = field.domain
        self.field_is_nullable = field.isNullable
        self.field_length = field.length
        self.field_precision = field.precision
        self.field_scale = field.scale
        self.field_required = field.required
        
    def write_feature_class_field_properties(self):
        object_features_list = [self.field_ID, self.fc_ID, self.field_alias, self.field_name, self.field_type,
                                self.field_def_value, self.field_domain,
                            self.field_is_nullable, self.field_length, self.field_precision, self.field_scale,
                                self.field_required]
        for i in range(len(object_features_list)):
            object_features_list[i] = str(object_features_list[i])
        return ",".join(object_features_list)

