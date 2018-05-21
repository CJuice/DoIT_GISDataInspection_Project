"""
Access an sde geodatabase and inventory the feature classes and inspect the data.
TODO Output results to sql database instead of csv (confer with Pat)
Inputs:  User defined folder choice (integer)
Outputs:  sql database
Compatibility: Revised on 20180118 for Python 3.6 (ESRI ArcPro python version)
Author:  CJuice
Date:  05/17/2018
Revised:  Forked from EnterpriseGDBIntentory project. Tailored to DoIT needs for GIS data inspection.
Modifications:
"""

#_______________________________________________________________________________________________________________________
# IMPORTS
from collections import namedtuple
from UtilityClass import UtilityClassFunctionality as myutil
import FeatureClassObject_Class
import GeodatabaseDomain_Class
import logging
import os

#_______________________________________________________________________________________________________________________
# VARIABLES
    #non-constants
date_parts = myutil.get_date_parts()
date_today = date_parts[0] #Original date format
date_today_database_field = "{}/{}/{}".format(date_parts[2], date_parts[3], date_parts[1]) #redesigned date format to meet Access database format for Date TODO - assess this
domain_objects_list = None
feature_classes_list = None
feature_dataset_ADMs_list = []
feature_datasets_list = None
feature_dataset_names_list = []
feature_dataset_parts_dict = {}
output_file_directory = None
round_count = 0

    #CONSTANTS
Variable = namedtuple("Variable", "value") # named tuple definition
DOMAIN_HEADERS_LIST = Variable(value=("DOMAIN_ID", "DOM_NAME", "DOM_OWNER", "DOM_DESC", "DOM_DOMAINTYPE",
                       "DOM_TYPE", "DOM_CODEDVALKEYS", "DOM_CODEDVALVALUES", "DOM_RANGE", "DOM_DATEEXPORT"))
FEATURE_CLASS_HEADERS_LIST = Variable(value=("FC_ID", "ADM_ID", "FC_FDNAME", "FC_NAME", "FC_DATATYPE", "FC_SHAPETYPE",
                              "FC_SPATIALREFNAME", "FC_FEATURECOUNT", "FC_DATEEXPORT"))
FIELD_HEADERS_LIST = Variable(value=("FIELD_ID", "FC_ID", "FLD_ALIAS", "FLD_NAME", "FLD_TYPE", "FLD_DEF_VAL", "FLD_DOMAIN",
                      "FLD_ISNULLABLE", "FLD_LENGTH", "FLD_PRECISION", "FLD_SCALE", "FLD_REQUIRED"))
LOG_FILE_NAME = Variable(value="EnterpriseGDBInventory_LOG.log")
OUTPUT_FILE_NAMES = Variable(value=("{}_FeatureClassInventory.csv".format(date_today),
                                    "{}_FeatureClassFIELDSInventory.csv".format(date_today),
                                    "{}_GeodatabaseDomainsInventory.csv".format(date_today)))

#_______________________________________________________________________________________________________________________
# LOGGING setup
logging.basicConfig(filename=LOG_FILE_NAME.value, level=logging.INFO)
myutil.print_and_log(
    message=" {} - {} Initiated".format(myutil.get_date_time_for_logging_and_printing(), os.path.basename(__file__)),
    log_level=myutil.INFO_LEVEL)

#_______________________________________________________________________________________________________________________
# FUNCTIONS
def create_output_results_files(output_filename):
    try:
        fhand = open(output_filename, "a")
    except Exception as e:
        myutil.print_and_log(message="File did not open. {}. {}".format(output_filename, e),
                             log_level=myutil.ERROR_LEVEL)
        exit()
    else:
        return fhand

def get_input(message):
    input_value = myutil.raw_input_basic_checks(raw_input_prompt_sentence="\n{}\n>>".format(message))
    if myutil.check_path_exists(path=input_value):
        return input_value
    else:
        myutil.print_and_log(message="Path does not exist.\n{}".format(input_value), log_level=myutil.ERROR_LEVEL)
        exit()

@myutil.capture_and_print_geoprocessing_errors
def run_ESRI_GP_tool(func, *args, **kwargs):
    """Pass ESRI geoprocessing function and arguments through Decorator containing error handling functionality"""
    return func(*args, **kwargs)

#_______________________________________________________________________________________________________________________
# INPUTS
    # Get the users choice of environments to examine. Check validity.
user_SDE_file_path_choice = get_input("Paste the path to the .sde connection file you wish to use")

    # Get the output directory location. Check validity.
users_output_file_directory_choice = get_input("Paste the path to the directory where new output files will be created.")
output_feature_class_file, output_fields_file, output_domains_file = tuple(
    [os.path.join(users_output_file_directory_choice, item) for item in OUTPUT_FILE_NAMES.value])

#_______________________________________________________________________________________________________________________
# FUNCTIONALITY
import arcpy # delayed arcpy import for performance
arcpy.env.workspace = user_SDE_file_path_choice

# Create the new output files for the feature class inventory with headers
file_and_headers_pairing = [(output_feature_class_file,FEATURE_CLASS_HEADERS_LIST.value),
                            (output_fields_file, FIELD_HEADERS_LIST.value),
                            (output_domains_file, DOMAIN_HEADERS_LIST.value)]
for pairing in file_and_headers_pairing:
    file_element, header_element = pairing
    try:
        with open(file_element, "w") as fhand_file:
            fhand_file.write(",".join(header_element) + "\n")
    except Exception as e:
        myutil.print_and_log(message="Problem creating or checking existence of {} file.\n{}".format(file_element, e),
            log_level=myutil.ERROR_LEVEL)
        exit()

try:
    arcpy.env.workspace = user_SDE_file_path_choice
except Exception as e:
    myutil.print_and_log(message="Problem establishing workspace: {}\n".format(user_SDE_file_path_choice, e),
        log_level=myutil.ERROR_LEVEL)
    exit()
else:
    myutil.print_and_log(message="Accessing {}\n".format(arcpy.env.workspace), log_level=myutil.INFO_LEVEL)

# make a list of domains for the geodatabase workspace environment.
sde_environment_filename = os.path.basename(user_SDE_file_path_choice)

fhand_domains_file = create_output_results_files(output_filename=output_domains_file)
try:
    domain_objects_list = run_ESRI_GP_tool(arcpy.da.ListDomains)
except Exception as e:
    myutil.print_and_log(message="arcpy.da.ListDomains() failed. {}".format(e),log_level=myutil.ERROR_LEVEL)
    exit()
for domain_object in domain_objects_list:
    gdb_domain = GeodatabaseDomain_Class.GeodatabaseDomains(environment_name=sde_environment_filename,
                                                            domain_object=domain_object,
                                                            date=date_today_database_field)
    try:
        fhand_domains_file.write("{}\n".format(gdb_domain.generate_domain_properties_string()))
    except Exception as e:
        myutil.print_and_log(message="Did not write domains properties to file: {}. {}".format(domain_object.name, e),
            log_level=myutil.WARNING_LEVEL)
fhand_domains_file.close()

# make a list of FD's present.
try:
    feature_datasets_list = run_ESRI_GP_tool(arcpy.ListDatasets)
except Exception as e:
    myutil.print_and_log(message="arcpy.ListDatasets did not run properly. {}".format(e), log_level=myutil.ERROR_LEVEL)
    exit()

# inspect each FD, then all FC's within, then fields of each FC
if len(feature_datasets_list) > 0:
    # FD Inspection
    for fd in feature_datasets_list:
        myutil.print_and_log(message="Examining FD: {}".format(fd),log_level=myutil.INFO_LEVEL)
        production_sde, feature_dataset_name = fd.split(".")

        # Step into each feature dataset by altering the workspace
        arcpy.env.workspace = os.path.join(user_SDE_file_path_choice, fd)
        try:
            feature_classes_list = run_ESRI_GP_tool(arcpy.ListFeatureClasses)
        except Exception as e:
            myutil.print_and_log(
                message="Error creating list of FC's inside of FD: {}. {}".format(fd, e),
                log_level=myutil.WARNING_LEVEL)

        fhand_featureclass_file = create_output_results_files(output_filename=output_feature_class_file)
        fhand_fields_file = create_output_results_files(output_filename=output_fields_file)

        # FC's Inspection
        try:
            print("\tFC List: {}".format(feature_classes_list))
            for fc in feature_classes_list:

                # Instead of using Describe objects basename, which is ADMName.FeatureClassName, grab just the
                #   FC name for use
                adm_ID, feature_class_name = fc.split(".") # adm_ID is the same value as production_sde above
                feature_class_ID = "{}.{}".format(fd, feature_class_name)
                try:

                    # Get the arcpy.Describe object for each FC
                    fc_desc = arcpy.Describe(fc)
                    try:

                        # Build the FC object
                        fc_obj = FeatureClassObject_Class.FeatureClassObject(fc_ID=feature_class_ID, ADM_ID=adm_ID,
                                                                             feature_dataset=feature_dataset_name,
                                                                             feature_class_name=feature_class_name,
                                                                             arcpy_describe_object=fc_desc,
                                                                             date_export=date_today_database_field)
                    except Exception as e:
                        myutil.print_and_log(message="FeatureClassObject didn't instantiate. {}".format(fc, e),
                            log_level=myutil.WARNING_LEVEL)
                    try:

                        # Get the feature count
                        fc_obj.fc_feature_count = int(arcpy.GetCount_management(fc).getOutput(0))
                    except Exception as e:
                        myutil.print_and_log(message="Error getting FC feature count: {}. {}".format(fc, e),
                            log_level=myutil.WARNING_LEVEL)
                    try:
                        fhand_featureclass_file.write("{}\n".format(fc_obj.generate_feature_class_properties_string()))
                    except Exception as e:
                        myutil.print_and_log(message="Did not write FC properties to file: {}. {}".format(fc, e),
                            log_level=myutil.WARNING_LEVEL)
                except Exception as e:
                    # For FC's that don't process correctly this records their presence so don't go undocumented.
                    fc_error_msg = "{},{},{},{},ERROR,ERROR,ERROR,{},{}\n".format(feature_class_ID, adm_ID,
                                                                                  feature_dataset_name,
                                                                                  feature_class_name,
                                                                                  fc_obj.fc_feature_count,
                                                                                  date_today_database_field)
                    fhand_featureclass_file.write(fc_error_msg)
                    myutil.print_and_log(message="{}\n{}".format(fc_error_msg, e), log_level=myutil.ERROR_LEVEL)

                # FC's Fields Inspection
                try:
                    feature_class_fields_list = fc_desc.fields
                    for field in feature_class_fields_list:
                        field_ID = "{}.{}".format(feature_class_ID, field.name)
                        try:

                            # Build the FC field details object
                            feature_class_field_details = FeatureClassObject_Class.FeatureClassFieldDetails(
                                feature_class_fields_list=feature_class_fields_list,
                                field_ID=field_ID,
                                feature_class_ID=feature_class_ID,
                                field=field)
                        except Exception as e:
                            myutil.print_and_log(
                                message="FeatureClassFieldDetails object didn't instantiate: {}. {}".format(fc, e),
                                log_level=myutil.WARNING_LEVEL)
                        try:
                            fhand_fields_file.write("{}\n".format(
                                feature_class_field_details.generate_feature_class_field_properties_string()))
                        except Exception as e:
                            myutil.print_and_log(
                                message="Did not write FC field details to file: {}. {}".format(
                                    feature_class_field_details, e),
                                log_level=myutil.WARNING_LEVEL)
                            print("")
                except Exception as e:

                    # For fc field details that don't process this records their presence so not undocumented.
                    fhand_fields_file.write(
                        "{},{},ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR\n".format(
                            field_ID, feature_class_ID))
                    myutil.print_and_log(message="Error with writing field details for {}. {}".format(field_ID, e),
                        log_level=myutil.ERROR_LEVEL)
        except Exception as e:
            myutil.print_and_log(
                message="Problem iterating through FC's within FD: {}. {}".format(fd, e),log_level=myutil.WARNING_LEVEL)
        finally:
            fhand_featureclass_file.close()
            fhand_fields_file.close()
else:
    pass

print("\nScript completed.")
