###################################
# Script:  InventoryGISDataInSDEGDB.py
# Author:  CJuice on GitHub
# Date Created:  05/02/2017
# Revised: 01/2018
# Compatibility: Revised on 20180118 for Python 3.6.2
# Purpose:  Run through a folder containing a(n) .sde connection file inventory the feature classes.
# Inputs:  User defined folder choice (integer)
# Outputs:  Text csv file
# Modifications:    Originated as V1. That script examined any ADM connection file. We realized the master SDE connection file sees all so we
#                    switched to just examine that file. When the switch was made the functionality to look into the Feature Datasets was broken.
#                    A redesign was done. A glitch exists with examining Feature Datasets. From any sde connection file you can see feature datasets
#                    in other ADMs despite them being protected behind login and passwords to protect the compartments of data for different program areas.
#                    For example, if you call a list of feature datasets while looking at MSW_ADM you can see the feature datasets in the GW_ADM. By moving to 
#                    examining just the master SDE connection for an environment all of the Feature Datasets and Feature Classes are visible and accessible. 
#                    This allowed a redesign so that the script could step into the Feature Datasets to get the Feature Classes, which aren't visible from the
#                    root gdb. The script arcpy.env.workspace has to change to the Feature Dataset to access/see the Feature Classes within.
###################################
# IMPORTS
import os, sys
import FeatureClassObject_Class
import GeodatabaseDomain_Class
import logging
from UtilityClass import UtilityClassFunctionality
import arcpy

# VARIABLES
    # Logging setup
log_file_name = "EnterpriseGDBInventory_LOG.log"
logging.basicConfig(filename=log_file_name, level=logging.INFO)
UtilityClassFunctionality.print_and_log(
    message=" {} - InventoryGISDataInSDEGDB.py Initiated".format(
        UtilityClassFunctionality.get_date_time_for_logging_and_printing()),
    log_level=UtilityClassFunctionality.INFO_LEVEL)

    # Inputs:
        # Get the users choice of environments to examine. Check validity.
sde_files_path = None
user_SDE_file_path_choice = UtilityClassFunctionality.raw_input_basic_checks(
    raw_input_prompt_sentence="\nPaste the path to the .sde connection file you wish to use\n>>")
if UtilityClassFunctionality.check_path_exists(path=user_SDE_file_path_choice):
    sde_files_path = user_SDE_file_path_choice
else:
    UtilityClassFunctionality.print_and_log(
        message="Path does not exist.\n{}".format(user_SDE_file_path_choice),
        log_level=UtilityClassFunctionality.ERROR_LEVEL)
    exit()

        # Get the output directory location. Check validity.
output_file_directory = None
users_output_file_directory_choice = UtilityClassFunctionality.raw_input_basic_checks(
    raw_input_prompt_sentence="\nPaste the path to the directory where new output files will be created.\n>>")
if UtilityClassFunctionality.check_path_exists(path=users_output_file_directory_choice):
    output_file_directory = users_output_file_directory_choice
else:
    UtilityClassFunctionality.print_and_log(
        message="Path does not exist.\n{}".format(output_file_directory),
        log_level=UtilityClassFunctionality.ERROR_LEVEL)
    exit()

date_parts = UtilityClassFunctionality.get_date_parts()
date_today = date_parts[0] #Original date format
date_today_database_field = "{}/{}/{}".format(
    date_parts[2], date_parts[3], date_parts[1]) #redesigned date format to meet Access database format for Date

output_feature_class_file = os.path.join(output_file_directory, "{}_{}__FeatureClassInventory.csv".format(
    date_today, os.path.basename(sde_files_path)))
output_fields_file = os.path.join(output_file_directory, "{}_{}__FeatureClassFIELDSInventory.csv".format(
    date_today, os.path.basename(sde_files_path)))
output_domains_file = os.path.join(output_file_directory, "{}_{}__GeodatabaseDomainsInventory.csv".format(
    date_today, os.path.basename(sde_files_path)))

feature_class_headers_list = ["FC_ID", "ADM_ID", "FC_FDNAME", "FC_NAME", "FC_DATATYPE", "FC_SHAPETYPE",
                              "FC_SPATIALREFNAME", "FC_FEATURECOUNT", "FC_DATEEXPORT"]
field_headers_list = ["FIELD_ID", "FC_ID", "FLD_ALIAS", "FLD_NAME", "FLD_TYPE", "FLD_DEF_VAL", "FLD_DOMAIN",
                      "FLD_ISNULLABLE", "FLD_LENGTH", "FLD_PRECISION", "FLD_SCALE", "FLD_REQUIRED"]
domain_headers_list = ["DOMAIN_ID", "ENV_ID", "DOM_NAME", "DOM_OWNER", "DOM_DESC", "DOM_DOMAINTYPE",
                       "DOM_TYPE", "DOM_CODEDVALKEYS", "DOM_CODEDVALVALUES", "DOM_RANGE", "DOM_DATEEXPORT"]

feature_dataset_ADMs_list = []
feature_dataset_names_list = []
feature_dataset_parts_dict = {}
round_count = 0

# METHODS
@UtilityClassFunctionality.capture_and_print_geoprocessing_errors
def run_ESRI_GP_tool(func, *args, **kwargs):
    """Pass ESRI geoprocessing function and arguments through Decorator containing error handling functionality"""

    return func(*args, **kwargs)

# FUNCTIONALITY
arcpy.env.workspace = sde_files_path

# Create the new output file for the feature class inventory with headers
try:
    with open(output_feature_class_file, "w") as fhand:
        fhand.write(",".join(feature_class_headers_list) + "\n")
        fhand.close()
except:
    UtilityClassFunctionality.print_and_log(
        message="Problem creating or checking existence of {} file.\n".format(output_feature_class_file),
        log_level=UtilityClassFunctionality.ERROR_LEVEL)
    exit()

# Create the new output file for the feature class fields inventory with headers
try:
     with open(output_fields_file, "w") as fhand_fields_file:
         fhand_fields_file.write(",".join(field_headers_list) + "\n")
         fhand_fields_file.close()
except:
    UtilityClassFunctionality.print_and_log(
        message="Problem creating or checking existence of {} file.\n".format(output_fields_file),
        log_level=UtilityClassFunctionality.ERROR_LEVEL)
    exit()

# Create the new output file for the Domains inventory with headers
try:
     with open(output_domains_file, "w") as fhand_domains_file:
         fhand_domains_file.write(",".join(domain_headers_list) + "\n")
         fhand_domains_file.close()
except:
    UtilityClassFunctionality.print_and_log(
        message="Problem creating or checking existence of {} file.\n".format(output_domains_file),
        log_level=UtilityClassFunctionality.ERROR_LEVEL)
    exit()

#   Due to a glitch (at employer where script originally designed. Not sure if pervasive through all SDE) in SDE
#       where all Feature Datasets are visible from any SDE connection file, the script first looks at all
#       uncontained/loose Feature Classes sitting in the root geodatabase. After inventorying all of those it then
#       lists the Feature Datasets and proceeds to step into each dataset by altering the arcpy.env.workspace to
#       the dataset so that the ListFeatureClasses() function returns with results. The feature classes within a
#       feature dataset are not visible unless the workspace is the dataset itself.

sde_environment_filename = os.path.basename(sde_files_path)
feature_classes_list = None
feature_datasets_list = None
domain_objects_list = None
sde_filename_parts_list = sde_environment_filename.split(".")


# Need the ENVIRONMENT name to create the unique ID's for the inventory database table records. This comes from the
#   sde file name, not an environment property. So, if the filename is wrong, this is wrong.
env_name = sde_filename_parts_list[0]

# Open/Create the output files for results to be appended.
try:
    fhand = open(output_feature_class_file, "a")
except:
    UtilityClassFunctionality.print_and_log(
        message="Feature Class File did not open. Iteration: {}\n".format(sde_environment_filename),
        log_level=UtilityClassFunctionality.ERROR_LEVEL)
    exit()
try:
    fhand_fields_file = open(output_fields_file, "a")
except:
    UtilityClassFunctionality.print_and_log(
        message="Fields File did not open. Iteration: {}\n".format(sde_environment_filename),
        log_level=UtilityClassFunctionality.ERROR_LEVEL)
    exit()
try:
    fhand_domains_file = open(output_domains_file, "a")
except:
    UtilityClassFunctionality.print_and_log(
        message="Domains File did not open. Iteration: {}\n".format(sde_environment_filename),
        log_level=UtilityClassFunctionality.ERROR_LEVEL)
    exit()
try:
    arcpy.env.workspace = sde_files_path
except:
    UtilityClassFunctionality.print_and_log(
        message="Problem establishing workspace: {}\n".format(sde_files_path),
        log_level=UtilityClassFunctionality.ERROR_LEVEL)
    exit()
UtilityClassFunctionality.print_and_log(
    message="Accessing {}\n".format(arcpy.env.workspace), log_level=UtilityClassFunctionality.INFO_LEVEL)

# make a list of domains for the geodatabase workspace environment. If multiple sde files are examined for
#   an environment, to prevent duplicates in file, the environment name is checked for previous use/examination.
try:
    domain_objects_list = run_ESRI_GP_tool(arcpy.da.ListDomains)
except:
    UtilityClassFunctionality.print_and_log(
        message="arcpy.da.ListDomains() failed",
        log_level=UtilityClassFunctionality.ERROR_LEVEL)
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
    UtilityClassFunctionality.print_and_log(
        message="Error creating list of feature classes outside of feature datasets",
        log_level=UtilityClassFunctionality.ERROR_LEVEL)
    exit()

try:
    if feature_classes_list != None and len(feature_classes_list) > 0:
        UtilityClassFunctionality.print_and_log(
            message="Looking for feature classes in {}\n".format(arcpy.env.workspace),
            log_level=UtilityClassFunctionality.INFO_LEVEL)
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
                    UtilityClassFunctionality.print_and_log(
                        message="FeatureClassObject didn't instantiate: {}".format(fc),
                        log_level=UtilityClassFunctionality.WARNING_LEVEL)
                try:

                    # Get the feature count
                    fc_obj.fc_feature_count = int(arcpy.GetCount_management(fc).getOutput(0))
                except:
                    UtilityClassFunctionality.print_and_log(
                        message="Error getting feature class feature count: {}".format(fc),
                        log_level=UtilityClassFunctionality.WARNING_LEVEL)
                try:
                    fhand.write("{}\n".format(fc_obj.writeFeatureClassProperties()))
                except:
                    UtilityClassFunctionality.print_and_log(
                        message="Did not write FC properties to file: {}".format(fc),
                        log_level=UtilityClassFunctionality.WARNING_LEVEL)
            except:
                # For feature classes that don't process correctly this records their presence so don't go undocumented.
                fhand.write("{},{},{},{},ERROR,ERROR,ERROR,{},{}\n".format(feature_class_ID, adm_ID,
                                                                           feature_dataset_name,
                                                                           feature_class_name,
                                                                           fc_obj.fc_feature_count,
                                                                           date_today_database_field))
                UtilityClassFunctionality.print_and_log(
                    message="{},{},{},{},ERROR,ERROR,ERROR,{},{}".format(feature_class_ID, adm_ID, feature_dataset_name,
                                                                 feature_class_name, fc_obj.fc_feature_count,
                                                                 date_today_database_field),
                    log_level=UtilityClassFunctionality.ERROR_LEVEL)

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
                        UtilityClassFunctionality.print_and_log(
                            message="FeatureClassFieldDetailsObject didn't instantiate: {}".format(field_ID),
                            log_level=UtilityClassFunctionality.WARNING_LEVEL)
                    try:
                        fhand_fields_file.write("{}\n".format(
                            feature_class_field_details.write_feature_class_field_properties()))
                    except:
                        UtilityClassFunctionality.print_and_log(
                            message="Did not write fcFieldDetails properties to file: {}".format(field_ID),
                            log_level=UtilityClassFunctionality.WARNING_LEVEL)
            except:
                # For fc field details that don't process correctly this records their presence so don't go undocumented.
                fhand_fields_file.write("{},{},ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR\n".format(
                    field_ID, feature_class_ID))
                UtilityClassFunctionality.print_and_log(
                    message="Error with writing field details for {}".format(field_ID),
                    log_level=UtilityClassFunctionality.ERROR_LEVEL)
    else:
        pass
except:
    UtilityClassFunctionality.print_and_log(
        message="Problem iterating through feature classes", log_level=UtilityClassFunctionality.ERROR_LEVEL)
    exit()

# make a list of feature datasets present.
try:
    feature_datasets_list = run_ESRI_GP_tool(arcpy.ListDatasets)
except:
    UtilityClassFunctionality.print_and_log(
        message="arcpy.ListDatasets did not run properly", log_level=UtilityClassFunctionality.ERROR_LEVEL)
    exit()

feature_dataset_name = "" # resetting from above because it is used below.
if len(feature_datasets_list) > 0:
    for fd in feature_datasets_list:
        UtilityClassFunctionality.print_and_log(message="Examining feature dataset: {}".format(fd),
                                                log_level=UtilityClassFunctionality.INFO_LEVEL)

        # For purposes of building the FC_ID and documenting the feature dataset name without the ADM name
        #   (ADM_Name.FD_Name) we need to isolate the feature dataset name
        feature_dataset_parts_list = fd.split(".", 1)
        feature_dataset_name = feature_dataset_parts_list[1]

        # Step into each feature dataset by altering the workspace
        arcpy.env.workspace = os.path.join(sde_files_path, fd)

        try:
            feature_classes_list = run_ESRI_GP_tool(arcpy.ListFeatureClasses)
        except:
            UtilityClassFunctionality.print_and_log(
                message="Error creating list of feature classes inside of feature dataset: {}".format(fd),
                log_level=UtilityClassFunctionality.WARNING_LEVEL)
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
                        UtilityClassFunctionality.print_and_log(
                            message="FeatureClassObject didn't instantiate".format(fc),
                            log_level=UtilityClassFunctionality.WARNING_LEVEL)
                    try:

                        # Get the feature count
                        fc_obj.fc_feature_count = int(arcpy.GetCount_management(fc).getOutput(0))
                    except:
                        UtilityClassFunctionality.print_and_log(
                            message="Error getting feature class feature count: {}".format(fc),
                            log_level=UtilityClassFunctionality.WARNING_LEVEL)
                    try:
                        fhand.write("{}\n".format(fc_obj.writeFeatureClassProperties()))
                    except:
                        UtilityClassFunctionality.print_and_log(
                            message="Did not write FC properties to file: {}".format(fc),
                            log_level=UtilityClassFunctionality.WARNING_LEVEL)
                except:
                    # For fc that don't process correctly this records their presence so don't go undocumented.
                    fhand.write("{},{},{},{},ERROR,ERROR,ERROR,{},{}\n".format(
                        feature_class_ID, adm_ID, feature_dataset_name, feature_class_name,
                        fc_obj.fc_feature_count, date_today_database_field))
                    UtilityClassFunctionality.print_and_log(
                        message="{},{},{},{},ERROR,ERROR,ERROR,{},{}".format(feature_class_ID,
                                                                             adm_ID,
                                                                             feature_dataset_name,
                                                                             feature_class_name,
                                                                             fc_obj.fc_feature_count,
                                                                             date_today_database_field),
                        log_level=UtilityClassFunctionality.ERROR_LEVEL)

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
                            UtilityClassFunctionality.print_and_log(
                                message="FeatureClassFieldDetailsObject didn't instantiate: {}".format(fc),
                                log_level=UtilityClassFunctionality.WARNING_LEVEL)
                        try:
                            fhand_fields_file.write(
                                feature_class_field_details.write_feature_class_field_properties() + "\n")
                        except:
                            UtilityClassFunctionality.print_and_log(
                                message="Did not write fcFieldDetails properties to file: {}".format(
                                    feature_class_field_details),
                                log_level=UtilityClassFunctionality.WARNING_LEVEL)
                            print("")
                except:


                    # For fc field details that don't process correctly this records their presence so don't go undocumented.
                    fhand_fields_file.write(
                        "{},{},ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR\n".format(
                            field_ID, feature_class_ID))
                    UtilityClassFunctionality.print_and_log(
                        message="Error with writing field details for {}\n".format(field_ID),
                        log_level=UtilityClassFunctionality.ERROR_LEVEL)
        except:
            UtilityClassFunctionality.print_and_log(
                message="Problem iterating through feature classes within feature dataset: {}".format(fd),
                log_level=UtilityClassFunctionality.WARNING_LEVEL)
else:
    pass

fhand.close()
fhand_fields_file.close()
fhand_domains_file.close()
print("\nScript completed.")
