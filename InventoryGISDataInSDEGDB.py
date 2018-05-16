"""
Access an sde geodatabase and inventory the feature classes and inspect the data. Output results to sql database.
Inputs:  User defined folder choice (integer)
Outputs:  Text csv file
Compatibility: Revised on 20180118 for Python 3.5 (ESRI ArcPro python version)
Author:  CJuice on GitHub
Date Created:  05/02/2017
Revised:  Forked from EnterpriseGDBIntentory project. Tailored to DoIT needs for GIS data inspection.
Modifications:
"""

# IMPORTS
import FeatureClassObject_Class
import GeodatabaseDomain_Class
import logging
from collections import namedtuple
import os
from UtilityClass import UtilityClassFunctionality as myutil

# VARIABLES
    #named tuple definition
Variable = namedtuple("Variable", "value")
    #non-constants
domain_objects_list = None
feature_classes_list = None
feature_dataset_ADMs_list = []
feature_datasets_list = None
feature_dataset_names_list = []
feature_dataset_parts_dict = {}
output_file_directory = None
round_count = 0
sde_files_path = None
    #constants
FEATURE_CLASS_HEADERS_LIST = Variable(value=("FC_ID", "ADM_ID", "FC_FDNAME", "FC_NAME", "FC_DATATYPE", "FC_SHAPETYPE",
                              "FC_SPATIALREFNAME", "FC_FEATURECOUNT", "FC_DATEEXPORT"))
FIELD_HEADERS_LIST = Variable(value=("FIELD_ID", "FC_ID", "FLD_ALIAS", "FLD_NAME", "FLD_TYPE", "FLD_DEF_VAL", "FLD_DOMAIN",
                      "FLD_ISNULLABLE", "FLD_LENGTH", "FLD_PRECISION", "FLD_SCALE", "FLD_REQUIRED"))
DOMAIN_HEADERS_LIST = Variable(value=("DOMAIN_ID", "ENV_ID", "DOM_NAME", "DOM_OWNER", "DOM_DESC", "DOM_DOMAINTYPE",
                       "DOM_TYPE", "DOM_CODEDVALKEYS", "DOM_CODEDVALVALUES", "DOM_RANGE", "DOM_DATEEXPORT"))
LOG_FILE_NAME = Variable(value="EnterpriseGDBInventory_LOG.log")

    # Logging setup
logging.basicConfig(filename=LOG_FILE_NAME.value, level=logging.INFO)
myutil.print_and_log(
    message=" {} - {} Initiated".format(myutil.get_date_time_for_logging_and_printing(), os.path.basename(__file__)),
    log_level=myutil.INFO_LEVEL)

    # Inputs:
        # Get the users choice of environments to examine. Check validity.
user_SDE_file_path_choice = myutil.raw_input_basic_checks(
    raw_input_prompt_sentence="\nPaste the path to the .sde connection file you wish to use\n>>")
if myutil.check_path_exists(path=user_SDE_file_path_choice):
    sde_files_path = user_SDE_file_path_choice
else:
    myutil.print_and_log(
        message="Path does not exist.\n{}".format(user_SDE_file_path_choice),
        log_level=myutil.ERROR_LEVEL)
    exit()

        # Get the output directory location. Check validity.
users_output_file_directory_choice = myutil.raw_input_basic_checks(
    raw_input_prompt_sentence="\nPaste the path to the directory where new output files will be created.\n>>")
if myutil.check_path_exists(path=users_output_file_directory_choice):
    output_file_directory = users_output_file_directory_choice
else:
    myutil.print_and_log(
        message="Path does not exist.\n{}".format(output_file_directory),
        log_level=myutil.ERROR_LEVEL)
    exit()

date_parts = myutil.get_date_parts()
date_today = date_parts[0] #Original date format
date_today_database_field = "{}/{}/{}".format(
    date_parts[2], date_parts[3], date_parts[1]) #redesigned date format to meet Access database format for Date TODO - assess this

#TODO: condense below repetition
output_feature_class_file = os.path.join(output_file_directory, "{}_{}__FeatureClassInventory.csv".format(
    date_today, os.path.basename(sde_files_path)))
output_fields_file = os.path.join(output_file_directory, "{}_{}__FeatureClassFIELDSInventory.csv".format(
    date_today, os.path.basename(sde_files_path)))
output_domains_file = os.path.join(output_file_directory, "{}_{}__GeodatabaseDomainsInventory.csv".format(
    date_today, os.path.basename(sde_files_path)))

# METHODS
@myutil.capture_and_print_geoprocessing_errors
def run_ESRI_GP_tool(func, *args, **kwargs):
    """Pass ESRI geoprocessing function and arguments through Decorator containing error handling functionality"""

    return func(*args, **kwargs)

# FUNCTIONALITY
    #delayed arcpy import for performance
import arcpy
arcpy.env.workspace = sde_files_path

# Create the new output files for the feature class inventory with headers
file_and_headers_pairing = [(output_feature_class_file,FEATURE_CLASS_HEADERS_LIST.value),
                            (output_fields_file, FIELD_HEADERS_LIST.value),
                            (output_domains_file, DOMAIN_HEADERS_LIST.value)]
for pairing in file_and_headers_pairing:
    file_element, header_element = pairing
    try:
        with open(file_element, "w") as fhand:
            fhand.write(",".join(header_element) + "\n")
    except:
        myutil.print_and_log(
            message="Problem creating or checking existence of {} file.\n".format(file_element),
            log_level=myutil.ERROR_LEVEL)
        exit()

# TODO: Assess necessity of this statement and the resulting design
#   Due to a glitch (at employer where script originally designed. Not sure if pervasive through all SDE) in SDE
#       where all Feature Datasets are visible from any SDE connection file, the script first looks at all
#       uncontained/loose Feature Classes sitting in the root geodatabase. After inventorying all of those it then
#       lists the Feature Datasets and proceeds to step into each dataset by altering the arcpy.env.workspace to
#       the dataset so that the ListFeatureClasses() function returns with results. The feature classes within a
#       feature dataset are not visible unless the workspace is the dataset itself.

sde_environment_filename = os.path.basename(sde_files_path)
sde_filename_parts_list = sde_environment_filename.split(".")

# Need the ENVIRONMENT name to create the unique ID's for the inventory database table records. This comes from the
#   sde file name, not an environment property. So, if the filename is wrong, this is wrong.
env_name = sde_filename_parts_list[0]

# Open/Create the output files for results to be appended.
try:
    fhand = open(output_feature_class_file, "a")
except:
    myutil.print_and_log(
        message="Feature Class File did not open. Iteration: {}\n".format(sde_environment_filename),
        log_level=myutil.ERROR_LEVEL)
    exit()
try:
    fhand_fields_file = open(output_fields_file, "a")
except:
    myutil.print_and_log(
        message="Fields File did not open. Iteration: {}\n".format(sde_environment_filename),
        log_level=myutil.ERROR_LEVEL)
    exit()
try:
    fhand_domains_file = open(output_domains_file, "a")
except:
    myutil.print_and_log(
        message="Domains File did not open. Iteration: {}\n".format(sde_environment_filename),
        log_level=myutil.ERROR_LEVEL)
    exit()
try:
    arcpy.env.workspace = sde_files_path
except:
    myutil.print_and_log(
        message="Problem establishing workspace: {}\n".format(sde_files_path),
        log_level=myutil.ERROR_LEVEL)
    exit()
myutil.print_and_log(
    message="Accessing {}\n".format(arcpy.env.workspace), log_level=myutil.INFO_LEVEL)

# make a list of domains for the geodatabase workspace environment. If multiple sde files are examined for
#   an environment, to prevent duplicates in file, the environment name is checked for previous use/examination.
try:
    domain_objects_list = run_ESRI_GP_tool(arcpy.da.ListDomains)
except:
    myutil.print_and_log(
        message="arcpy.da.ListDomains() failed",
        log_level=myutil.ERROR_LEVEL)
    exit()

for domain_object in domain_objects_list:
    gdb_domain = GeodatabaseDomain_Class.GeodatabaseDomains(environment_name=sde_environment_filename,
                                                            domain_object=domain_object,
                                                            date=date_today_database_field)
    fhand_domains_file.write("{}\n".format(gdb_domain.generate_database_entry_text()))
else:
    pass

# make a list of feature classes present, outside of Feature Datasets
try:
    feature_classes_list = run_ESRI_GP_tool(arcpy.ListFeatureClasses)
except:
    myutil.print_and_log(
        message="Error creating list of feature classes outside of feature datasets",
        log_level=myutil.ERROR_LEVEL)
    exit()

try:
    if feature_classes_list != None and len(feature_classes_list) > 0:
        myutil.print_and_log(
            message="Looking for feature classes in {}\n".format(arcpy.env.workspace),
            log_level=myutil.INFO_LEVEL)
        for fc in feature_classes_list:

            # For building the FC_ID consistent with the portion of the script that iterates through feature datasets
            feature_dataset_name = "_"
            adm_name = None
            feature_class_name = None
            if "." in fc:
                feature_class_parts_list = fc.split(".", 1)
                adm_name = feature_class_parts_list[0]
                feature_class_name = feature_class_parts_list[1]
            else:
                adm_name = "_"
                feature_class_name = fc

            adm_ID = "{}.{}".format(env_name, adm_name)
            feature_class_ID = "{}.{}.{}".format(adm_ID, feature_dataset_name, feature_class_name)

            try:

                # Get the arcpy.Describe object for each feature class
                fc_desc = arcpy.Describe(fc)
                basename_parts_list = fc_desc.baseName.split(".", 1)

                try:

                    # Build the feature class object
                    fc_obj = FeatureClassObject_Class.FeatureClassObject(fc_ID=feature_class_ID, ADM_ID=adm_ID,
                                                                         feature_dataset=feature_dataset_name,
                                                                         feature_class_name=feature_class_name,
                                                                         arcpy_describe_object=fc_desc,
                                                                         date_export=date_today_database_field)
                except:
                    myutil.print_and_log(
                        message="FeatureClassObject didn't instantiate: {}".format(fc),
                        log_level=myutil.WARNING_LEVEL)
                try:

                    # Get the feature count
                    fc_obj.fc_feature_count = int(arcpy.GetCount_management(fc).getOutput(0))
                except:
                    myutil.print_and_log(
                        message="Error getting feature class feature count: {}".format(fc),
                        log_level=myutil.WARNING_LEVEL)
                try:
                    fhand.write("{}\n".format(fc_obj.write_feature_class_properties()))
                except:
                    myutil.print_and_log(
                        message="Did not write FC properties to file: {}".format(fc),
                        log_level=myutil.WARNING_LEVEL)
            except:
                # For feature classes that don't process correctly this records their presence so don't go undocumented.
                fhand.write("{},{},{},{},ERROR,ERROR,ERROR,{},{}\n".format(feature_class_ID, adm_ID,
                                                                           feature_dataset_name,
                                                                           feature_class_name,
                                                                           fc_obj.fc_feature_count,
                                                                           date_today_database_field))
                myutil.print_and_log(
                    message="{},{},{},{},ERROR,ERROR,ERROR,{},{}".format(feature_class_ID, adm_ID, feature_dataset_name,
                                                                 feature_class_name, fc_obj.fc_feature_count,
                                                                 date_today_database_field),
                    log_level=myutil.ERROR_LEVEL)

            try:

                # Get the fields in each feature class
                feature_class_fields_list = fc_desc.fields
                for field in feature_class_fields_list:
                    field_ID = "{}.{}".format(feature_class_ID, field.name)
                    try:

                        # Build the feature class field details object
                        feature_class_field_details = FeatureClassObject_Class.FeatureClassFieldDetails(
                            feature_class_fields_list=feature_class_fields_list,
                            field_ID=field_ID, feature_class_ID=feature_class_ID, field=field)
                    except:
                        myutil.print_and_log(
                            message="FeatureClassFieldDetailsObject didn't instantiate: {}".format(field_ID),
                            log_level=myutil.WARNING_LEVEL)
                    try:
                        fhand_fields_file.write("{}\n".format(
                            feature_class_field_details.write_feature_class_field_properties()))
                    except:
                        myutil.print_and_log(
                            message="Did not write fcFieldDetails properties to file: {}".format(field_ID),
                            log_level=myutil.WARNING_LEVEL)
            except:
                # For fc field details that don't process correctly this records their presence so don't go undocumented.
                fhand_fields_file.write("{},{},ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR\n".format(
                    field_ID, feature_class_ID))
                myutil.print_and_log(
                    message="Error with writing field details for {}".format(field_ID),
                    log_level=myutil.ERROR_LEVEL)
    else:
        pass
except:
    myutil.print_and_log(
        message="Problem iterating through feature classes", log_level=myutil.ERROR_LEVEL)
    exit()

# make a list of feature datasets present.
try:
    feature_datasets_list = run_ESRI_GP_tool(arcpy.ListDatasets)
except:
    myutil.print_and_log(
        message="arcpy.ListDatasets did not run properly", log_level=myutil.ERROR_LEVEL)
    exit()

feature_dataset_name = "" # resetting from above because it is used below.
if len(feature_datasets_list) > 0:
    for fd in feature_datasets_list:
        myutil.print_and_log(message="Examining feature dataset: {}".format(fd),
                                                log_level=myutil.INFO_LEVEL)

        # For purposes of building the FC_ID and documenting the feature dataset name without the ADM name
        #   (ADM_Name.FD_Name) we need to isolate the feature dataset name
        feature_dataset_parts_list = fd.split(".", 1)
        feature_dataset_name = feature_dataset_parts_list[1]

        # Step into each feature dataset by altering the workspace
        arcpy.env.workspace = os.path.join(sde_files_path, fd)

        try:
            feature_classes_list = run_ESRI_GP_tool(arcpy.ListFeatureClasses)
        except:
            myutil.print_and_log(
                message="Error creating list of feature classes inside of feature dataset: {}".format(fd),
                log_level=myutil.WARNING_LEVEL)
        try:
            for fc in feature_classes_list:

                # Instead of using Describe objects basename, which is ADMName.FeatureClassName, grab just the
                #   feature class name for use
                feature_class_parts_list = fc.split(".", 1)
                adm_name = feature_class_parts_list[0]
                feature_class_name = feature_class_parts_list[1]
                adm_ID = "{}.{}".format(env_name, adm_name)
                feature_class_ID = "{}.{}.{}".format(adm_ID, feature_dataset_name, feature_class_name)

                try:

                    # Get the arcpy.Desribe object for each feature class
                    fc_desc = arcpy.Describe(fc)
                    basename_parts_list = fc_desc.baseName.split(".", 1)
                    try:

                        # Build the feature class object
                        fc_obj = FeatureClassObject_Class.FeatureClassObject(fc_ID=feature_class_ID, ADM_ID=adm_ID,
                                                                             feature_dataset=feature_dataset_name,
                                                                             feature_class_name=feature_class_name,
                                                                             arcpy_describe_object=fc_desc,
                                                                             date_export=date_today_database_field)
                    except:
                        myutil.print_and_log(
                            message="FeatureClassObject didn't instantiate".format(fc),
                            log_level=myutil.WARNING_LEVEL)
                    try:

                        # Get the feature count
                        fc_obj.fc_feature_count = int(arcpy.GetCount_management(fc).getOutput(0))
                    except:
                        myutil.print_and_log(
                            message="Error getting feature class feature count: {}".format(fc),
                            log_level=myutil.WARNING_LEVEL)
                    try:
                        fhand.write("{}\n".format(fc_obj.write_feature_class_properties()))
                    except:
                        myutil.print_and_log(
                            message="Did not write FC properties to file: {}".format(fc),
                            log_level=myutil.WARNING_LEVEL)
                except:
                    # For fc that don't process correctly this records their presence so don't go undocumented.
                    fhand.write("{},{},{},{},ERROR,ERROR,ERROR,{},{}\n".format(
                        feature_class_ID, adm_ID, feature_dataset_name, feature_class_name,
                        fc_obj.fc_feature_count, date_today_database_field))
                    myutil.print_and_log(
                        message="{},{},{},{},ERROR,ERROR,ERROR,{},{}".format(feature_class_ID,
                                                                             adm_ID,
                                                                             feature_dataset_name,
                                                                             feature_class_name,
                                                                             fc_obj.fc_feature_count,
                                                                             date_today_database_field),
                        log_level=myutil.ERROR_LEVEL)

                try:

                    # Get the fields in each feature class
                    feature_class_fields_list = fc_desc.fields
                    for field in feature_class_fields_list:
                        field_ID = "{}.{}".format(feature_class_ID, field.name)
                        try:

                            # Build the feature class field details object
                            feature_class_field_details = FeatureClassObject_Class.FeatureClassFieldDetails(
                                feature_class_fields_list=feature_class_fields_list, field_ID=field_ID,
                                feature_class_ID=feature_class_ID, field=field)
                        except:
                            myutil.print_and_log(
                                message="FeatureClassFieldDetailsObject didn't instantiate: {}".format(fc),
                                log_level=myutil.WARNING_LEVEL)
                        try:
                            fhand_fields_file.write(
                                feature_class_field_details.write_feature_class_field_properties() + "\n")
                        except:
                            myutil.print_and_log(
                                message="Did not write fcFieldDetails properties to file: {}".format(
                                    feature_class_field_details),
                                log_level=myutil.WARNING_LEVEL)
                            print("")
                except:


                    # For fc field details that don't process correctly this records their presence so don't go undocumented.
                    fhand_fields_file.write(
                        "{},{},ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR\n".format(
                            field_ID, feature_class_ID))
                    myutil.print_and_log(
                        message="Error with writing field details for {}\n".format(field_ID),
                        log_level=myutil.ERROR_LEVEL)
        except:
            myutil.print_and_log(
                message="Problem iterating through feature classes within feature dataset: {}".format(fd),
                log_level=myutil.WARNING_LEVEL)
else:
    pass

fhand.close()
fhand_fields_file.close()
fhand_domains_file.close()
print("\nScript completed.")
