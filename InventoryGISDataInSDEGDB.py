"""
Access an ESRI SDE geodatabase per the SDE connection file provided by the user; Inventory the domains, the feature
 datasets, the feature classes and inspect all data within.

For Domains, inventory the name, description, domain type, data type, coded value keys, coded value values, range, and
 create database fields for domain ID, date, and row ID.
For Feature Classes, inventory the name, data type, shape type, total column count, total record count, total value
 count, total null value count, percent null, spatial reference name, feature dataset name, and create database fields
 for feature class ID, date, and row ID.
For Feature Class Fields, inventory the alias, name, total null value count, total value count, percent null, type,
 default value, domain, is nullable, length, max charater length found, precision, scale, required, and create
 database fields for field ID, feature class ID, date, and row ID.
The essential pieces for the script to run are a config file containing the credentials for accessing Socrata and the
 datasets to which results are written. If csv files of the results are being written then the output file names must be
 provided. A log file name must be provided as the process logs its progress and issues to a log file. An output folder
 name must be provided for the csv output, if written.
There are two optional boolean parameters the user can alter. They control whether the results are written to csv files
 and if the results are upserted to Socrata.
There are four python files necessary for the process to run. These are this file, a UtilityClass.py module, a
 GeodatabaseDomain_Class.py module, and a FeatureClassObjects_Class.py module. This file is the main script to perform
 the process. The Utility Class contains static methods for use anywhere within the process parts. The Geodatabase
 Domain Class contains the structure for the domains objects. The Feature Class Objects Class contains the structure
 for two objects. These objects are a Feature Class and a Feature Class Field. These items were grouped into one file
 since a feature class and its fields are connected. Domains apply to the entire geodatabase so they were viewed to be
 separate.
COMPATIBILITY: Revised on 20180118 for Python 3.6 (ESRI ArcPro python version)
REVISED:  Forked from CJuice's EnterpriseGDBIntentory project, originally designed for another employer environment.
 It has been tailored to Maryland DoIT needs for GIS data inspection.
MODIFICATIONS: 20180719, Completed functionality for upserting to Socrata. Revised default timeout for Socrata client
to 30 seconds, from 10 seconds, to address periodic timeout failures.
20180720, CJuice: Added try/except around Socrata upserting. Was encountering occasional timeout errors.
AUTHOR:  CJuice
DATE:  05/17/2018 fork origin
"""
def main():

    # IMPORTS
    from collections import namedtuple
    from datetime import date
    from UtilityClass import UtilityClassFunctionality as myutil
    import configparser
    import FeatureClassObjects_Class
    import GeodatabaseDomain_Class
    import logging
    import os
    import time

    # VARIABLES
    CONSTANT = namedtuple("CONSTANT", "value")

        # CONSTANTS
    _ROOT_PATH_FOR_PROJECT = CONSTANT(value=os.path.dirname(__file__))
    CREDENTIALS_PATH = CONSTANT(r"Docs\credentials.cfg")
    DATABASE_FLAG_NUMERIC = CONSTANT(value=-9999)
    DOMAINS_INVENTORY_FILE_NAME = CONSTANT(value="GeodatabaseDomainsInventory")
    FILE_NAME_FC_INVENTORY = CONSTANT(value="FeatureClassInventory")
    FILE_NAME_FIELD_INVENTORY = CONSTANT(value="FeatureClassFIELDSInventory")
    LOG_FILE = CONSTANT(value=os.path.join(_ROOT_PATH_FOR_PROJECT.value, "EnterpriseGDBInventory_LOG.log"))
    PATH_FOR_CSV_OUTPUT = CONSTANT(value=os.path.join(_ROOT_PATH_FOR_PROJECT.value, "OUTPUT_CSVs"))
    TURN_ON_UPSERT_OUTPUT_TO_SOCRATA = CONSTANT(value=True)                                         # OPTION
    TURN_ON_WRITE_OUTPUT_TO_CSV = CONSTANT(value=True)                                              # OPTION

        # OTHER
    domain_objects_list = None
    feature_datasets_list = None
    output_file_names_tuple = (myutil.build_csv_file_name_with_date( myutil.build_today_date_string(),
                                                                     FILE_NAME_FC_INVENTORY.value),
                               myutil.build_csv_file_name_with_date(myutil.build_today_date_string(),
                                                                    FILE_NAME_FIELD_INVENTORY.value),
                               myutil.build_csv_file_name_with_date(myutil.build_today_date_string(),
                                                                    DOMAINS_INVENTORY_FILE_NAME.value))
    SDE_file_path = os.path.join(_ROOT_PATH_FOR_PROJECT.value,
                                 r"SDE_CONNECTION_FILE\Production as sde on gis-ags-imap01p.mdgov.maryland.gov.sde")

        # Credentials: need from config file
    config = configparser.ConfigParser()
    config.read(filenames=CREDENTIALS_PATH.value)
    domainlevel_app_id = config['domainlevel']["app_id"]
    domainlevel_app_token = config['domainlevel']["app_token"]
    featureclasslevel_app_id = config['featureclasslevel']["app_id"]
    featureclasslevel_app_token = config['featureclasslevel']["app_token"]
    fieldlevel_app_id = config['fieldlevel']["app_id"]
    fieldlevel_app_token = config['fieldlevel']["app_token"]
    socrata_maryland_domain = config['DEFAULT']["maryland_domain"]
    socrata_password = config['DEFAULT']["password"]
    socrata_username = config['DEFAULT']["username"]


    # LOGGING
    logging.basicConfig(filename=LOG_FILE.value, level=logging.INFO)
    myutil.print_and_log(
        message=" {} - {} Initiated".format(myutil.get_date_time_for_logging_and_printing(), os.path.basename(__file__)),
        log_level=myutil.INFO_LEVEL)


    # FUNCTIONS
    @myutil.capture_and_print_geoprocessing_errors
    def run_ESRI_GP_tool(func, *args, **kwargs):
        """Pass ESRI geoprocessing function and arguments through Decorator containing error handling functionality"""
        return func(*args, **kwargs)


    # FUNCTIONALITY
    import arcpy  # delayed arcpy import for performance

    if TURN_ON_WRITE_OUTPUT_TO_CSV.value:
        myutil.print_and_log(message="Writing to csv (TURN_ON_WRITE_OUTPUT_TO_CSV.value = True)",
                             log_level=myutil.INFO_LEVEL)
    if TURN_ON_UPSERT_OUTPUT_TO_SOCRATA.value:
        myutil.print_and_log(message="Upserting to Socrata (TURN_ON_UPSERT_OUTPUT_TO_SOCRATA.value = True)",
                             log_level=myutil.INFO_LEVEL)


    # OUTPUT FILES: Create the new output files, for the feature class inventory, with headers. Streamline and loop.
    output_feature_class_file, output_fields_file, output_domains_file = [os.path.join(PATH_FOR_CSV_OUTPUT.value, item) for
                                                                          item in output_file_names_tuple]

        # need pairing of path and headers
    file_and_headers_pairing = [(output_feature_class_file, FeatureClassObjects_Class.FeatureClassObject.FC_HEADERS_LIST.value),
                                (output_fields_file, FeatureClassObjects_Class.FeatureClassFieldDetails.FIELD_HEADERS_LIST.value),
                                (output_domains_file, GeodatabaseDomain_Class.GeodatabaseDomains.DOMAIN_HEADERS_LIST.value)]
    for pairing in file_and_headers_pairing:
        file_element, header_element = pairing
        try:
            with open(file_element, "w") as fhand_file:
                fhand_file.write("{}\n".format(",".join(header_element)))
        except Exception as e:
            myutil.print_and_log(message="Problem creating or checking existence of {} file. {}".format(file_element, e),
                log_level=myutil.ERROR_LEVEL)
            exit()

    # ESTABLISH SDE CONNECTION
    try:
        arcpy.env.workspace = SDE_file_path
    except Exception as e:
        myutil.print_and_log(message="Problem establishing workspace: {}. {}".format(SDE_file_path, e),
            log_level=myutil.ERROR_LEVEL)
        exit()
    else:
        myutil.print_and_log(message="Accessing {}\n".format(arcpy.env.workspace), log_level=myutil.INFO_LEVEL)

    # Domains are processed first as they are at the highest level and apply to the entire geodatabase.
    # The next level is to inventory all feature datasets and step into each feature dataset to inventory the
    # feature classes within. After the feature classes have been processed at the dataset level each feature
    # class is analyzed at the field level.

    # DOMAINS: make a list of domains for the geodatabase workspace environment.
    if TURN_ON_WRITE_OUTPUT_TO_CSV.value:
        fhand_domains_file_handler = myutil.create_output_results_file_handler(output_filename=output_domains_file)
    if TURN_ON_UPSERT_OUTPUT_TO_SOCRATA.value:
        socrata_domains_client = myutil.create_socrata_client(username=socrata_username,
                                                              password=socrata_password,
                                                              app_token=domainlevel_app_token,
                                                              maryland_domain=socrata_maryland_domain)
    try:
        domain_objects_list = run_ESRI_GP_tool(arcpy.da.ListDomains)
    except Exception as e:
        myutil.print_and_log(message="arcpy.da.ListDomains() failed. {}".format(e),log_level=myutil.ERROR_LEVEL)
        exit()
    else:
        sde_environment_filename = os.path.basename(SDE_file_path)

        for domain_object in domain_objects_list:
            gdb_domain_obj = GeodatabaseDomain_Class.GeodatabaseDomains(environment_name=sde_environment_filename,
                                                                        domain_object=domain_object,
                                                                        date=myutil.build_today_date_string())
            domain_object_feature_list = gdb_domain_obj.create_object_feature_list()
            domain_object_feature_list_str = gdb_domain_obj.create_object_feature_list_str(
                domain_object_feature_list=domain_object_feature_list)
            if TURN_ON_WRITE_OUTPUT_TO_CSV.value:
                try:
                    fhand_domains_file_handler.write("{}\n".format(gdb_domain_obj.create_CSV_domain_properties_string(
                        object_feature_list_str=domain_object_feature_list_str)))
                except Exception as e:
                    myutil.print_and_log(message="Did not write domains properties to file: {}. {}".format(domain_object.name, e),
                        log_level=myutil.WARNING_LEVEL)
            if TURN_ON_UPSERT_OUTPUT_TO_SOCRATA.value:
                try:
                    myutil.upsert_to_socrata(client=socrata_domains_client,
                                             dataset_identifier=domainlevel_app_id,
                                             zipper=myutil.make_dict_zipper(
                                                 first_list=GeodatabaseDomain_Class.GeodatabaseDomains.DOMAIN_HEADERS_LIST.value,
                                                 second_list=domain_object_feature_list_str))
                    myutil.print_and_log("Upserted: {}".format(gdb_domain_obj.name), myutil.INFO_LEVEL)
                except Exception as e:
                    myutil.print_and_log(
                        message="Rrror upserting to Socrata: {}. {}".format(gdb_domain_obj.name, e),
                        log_level=myutil.WARNING_LEVEL)
    finally:
        if TURN_ON_WRITE_OUTPUT_TO_CSV.value:
            fhand_domains_file_handler.close()
        if TURN_ON_UPSERT_OUTPUT_TO_SOCRATA.value:
            socrata_domains_client.close()

    # FEATURE DATASETS: make a list of FD's present.
    try:
        feature_datasets_list = run_ESRI_GP_tool(arcpy.ListDatasets)
    except Exception as e:
        myutil.print_and_log(message="arcpy.ListDatasets did not run properly. {}".format(e), log_level=myutil.ERROR_LEVEL)
        exit()

    """Inspect each FD, then all FC's within, then fields of each FC. Assumption: DoIT naming is a three part 
    convention. Environment_Name.SDE.Entity_Data_Name for example Production.SDE.Transportation_Mile_Markers_etc;
    Coded is designed to this."""
    feature_datasets_list.sort()
    for fd in feature_datasets_list:
        myutil.print_and_log(message="Examining FD: {}".format(fd),log_level=myutil.INFO_LEVEL)
        production_fd, sde_fd_ID, feature_dataset_name = fd.split(".") # first two vars are not used

        # __________________________________
        # FEATURE DATASET ISOLATION - TESTING
        # if feature_dataset_name != "PlanningCadastre_MD_LandUseLandCover":
        #     continue
        # __________________________________

        # Step into each feature dataset by altering the workspace
        arcpy.env.workspace = os.path.join(SDE_file_path, fd)
        feature_classes_list = None
        try:
            feature_classes_list = run_ESRI_GP_tool(arcpy.ListFeatureClasses)
        except Exception as e:
            myutil.print_and_log(message="Error creating list of FC's inside FD. FD contents not processed: {}. {}".format(fd, e),
                                 log_level=myutil.WARNING_LEVEL)
            continue

        if TURN_ON_WRITE_OUTPUT_TO_CSV.value:
            fhand_featureclass_file_handler = myutil.create_output_results_file_handler(output_filename=output_feature_class_file)
            fhand_fields_file_handler = myutil.create_output_results_file_handler(output_filename=output_fields_file)

        if TURN_ON_UPSERT_OUTPUT_TO_SOCRATA.value:
            socrata_featureclass_client = myutil.create_socrata_client(username=socrata_username,
                                                                       password=socrata_password,
                                                                       app_token=featureclasslevel_app_token,
                                                                       maryland_domain=socrata_maryland_domain)
            socrata_featureclass_fields_client = myutil.create_socrata_client(username=socrata_username,
                                                                              password=socrata_password,
                                                                              app_token=fieldlevel_app_token,
                                                                              maryland_domain=socrata_maryland_domain)

        # Feature Classes Inspection
        print("\tFC List: {}".format(feature_classes_list))
        try:
            for fc in feature_classes_list:
                myutil.print_and_log(message="\tExamining FC: {}".format(fc), log_level=myutil.INFO_LEVEL)
                production_fc, sde_fc_ID, feature_class_name = fc.split(".") # first two vars are not used

                #__________________________________
                # FEATURE CLASS ISOLATION - TESTING
                # if feature_class_name not in ["PLAN_CountyLandUseLandCover2010_MDP", "PLAN_LandUseLandCover2010_MDP"]:
                #     continue
                #__________________________________


                fc_id = myutil.generate_id_from_args(fd, feature_class_name)
                fc_row_id = myutil.generate_id_from_args(fc_id, myutil.build_today_date_string())
                number_of_fc_features = DATABASE_FLAG_NUMERIC.value

                # Instantiate object. Set the other, finicky parameters as they become available. Write out at end.
                fc_obj = FeatureClassObjects_Class.FeatureClassObject(fc_ID=fc_id,
                                                                      feature_dataset_name=feature_dataset_name,
                                                                      feature_class_name=feature_class_name,
                                                                      date_export=myutil.build_today_date_string(),
                                                                      row_id=fc_row_id)
                # Get the feature count
                try:
                    feature_count_result = run_ESRI_GP_tool(arcpy.GetCount_management, fc)
                except Exception as e:
                    myutil.print_and_log(message="Error getting FC feature count: {}. {}".format(fc, e),
                                         log_level=myutil.WARNING_LEVEL)
                else:
                    number_of_fc_features = int(feature_count_result.getOutput(0))
                    fc_obj.total_record_count = number_of_fc_features

                # Get the arcpy.Describe object for each FC. Many elements are dependent on the Describe object
                try:
                    fc_desc = run_ESRI_GP_tool(arcpy.Describe, fc)
                except Exception as e:
                    # If the desribe object is unavailable, write the defaults and move on as nothing more can be done
                    if TURN_ON_WRITE_OUTPUT_TO_CSV.value:
                        fc_object_features_list = fc_obj.create_object_feature_list()
                        fhand_featureclass_file_handler.write(
                            "{}\n".format(fc_obj.create_CSV_feature_class_properties_string(
                                object_features_list_str=fc_object_features_list)))
                    if TURN_ON_UPSERT_OUTPUT_TO_SOCRATA.value:
                        fc_object_features_list = fc_obj.create_object_feature_list()
                        fc_object_features_list_str = fc_obj.create_object_feature_list_str(
                            object_features_list=fc_object_features_list)
                        try:
                            myutil.upsert_to_socrata(client=socrata_featureclass_client,
                                                     dataset_identifier=featureclasslevel_app_id,
                                                     zipper=myutil.make_dict_zipper(
                                                         first_list=FeatureClassObjects_Class.FeatureClassObject.FC_HEADERS_LIST.value,
                                                         second_list=fc_object_features_list_str))
                            myutil.print_and_log("Upserted Generic: {}".format(fc_obj.fc_name), myutil.INFO_LEVEL)
                        except Exception as e:
                            myutil.print_and_log(
                                message="Error upserting to Socrata: {}. {}".format(fc_obj.fc_name, e),
                                log_level=myutil.WARNING_LEVEL)
                    myutil.print_and_log(
                        message="{}. {}".format(
                            "Error generating Describe Object. Basic FC object record written. Fields object skipped.",
                            e),
                        log_level=myutil.ERROR_LEVEL)
                    continue
                else:
                    # If successful Describe object returned, proceed with next stage of analysis
                    fc_field_objects_list = fc_desc.fields
                    fc_field_names_list = [field_obj.baseName for field_obj in fc_field_objects_list]
                    fc_obj.data_type = fc_desc.dataType
                    fc_obj.shape_type = fc_desc.shapeType
                    fc_obj.spatial_ref_name = fc_desc.spatialReference.name

                    #NOTE: Due to a SQL error, needed to create prevent_SQL_error() function
                    #ERROR: "Attribute column not found [42S22:[Microsoft][ODBC Driver 13 for SQL Server][SQL Server]Invalid column name 'AREA'.]"
                    fc_field_names_list, fc_field_objects_list = myutil.prevent_SQL_error(fc_field_names_list, fc_field_objects_list)
                    fc_field_name_to_obj_dict = myutil.make_dict_zipper(first_list=fc_field_names_list,
                                                                        second_list=fc_field_objects_list)
                    total_field_count = len(fc_field_objects_list)
                    fc_obj.total_field_count = total_field_count
                    total_value_count = myutil.calculate_total_number_of_values_in_dataset(
                        total_records_processed=number_of_fc_features,
                        number_of_fields_in_dataset=total_field_count,
                        database_flag=DATABASE_FLAG_NUMERIC.value)
                    fc_obj.total_value_count = total_value_count

                    # Initialize to -9999. Change to zero when field is encountered in null count process. Avoid false zero
                    fc_fields_null_value_tracker_dict = {field_obj.name : DATABASE_FLAG_NUMERIC.value
                                                         for field_obj in fc_field_objects_list}
                    max_chars_used = DATABASE_FLAG_NUMERIC.value
                    string_fields_character_tracker_dict = {field_obj.name : max_chars_used for field_obj in fc_field_objects_list if field_obj.type.lower() == "string"}

                    # Access data values and analyze
                    try:
                        with arcpy.da.SearchCursor(fc, fc_field_names_list) as feature_class_cursor:
                            for row in feature_class_cursor:
                                row_dictionary = myutil.make_dict_zipper(first_list=fc_field_names_list,
                                                                         second_list=row)

                                # Evaluate data and inventory the null/empty data values
                                myutil.inspect_record_for_null_values(field_null_count_dict=fc_fields_null_value_tracker_dict,
                                                                      record_dictionary=row_dictionary,
                                                                      database_flag=DATABASE_FLAG_NUMERIC.value)
                                myutil.inspect_string_fields_for_char_usage(field_char_count_dict=string_fields_character_tracker_dict,
                                                                            record_dictionary=row_dictionary,
                                                                            field_name_to_field_object_dictionary=fc_field_name_to_obj_dict)
                    except Exception as e:
                        myutil.print_and_log(message="Error in cursor for FC: {}.\n\t{}".format(fc, e),
                                             log_level=myutil.WARNING_LEVEL)

                    # Calculate stats
                    fc_total_null_value_count = myutil.calculate_total_number_of_null_values_per_dataset(
                        null_counts_list=fc_fields_null_value_tracker_dict.values())
                    fc_obj.total_null_value_count = fc_total_null_value_count
                    fc_percent_null = myutil.calculate_percent(numerator=fc_total_null_value_count,
                                                               denominator=total_value_count)
                    fc_obj.percent_null = fc_percent_null

                    # Before launching into field level analysis, write the feature class data to file.
                    fc_object_features_list = fc_obj.create_object_feature_list()
                    fc_object_features_list_str = fc_obj.create_object_feature_list_str(
                        object_features_list=fc_object_features_list)
                    if TURN_ON_WRITE_OUTPUT_TO_CSV.value:
                        try:
                            fhand_featureclass_file_handler.write("{}\n".format(fc_obj.create_CSV_feature_class_properties_string(
                                object_features_list_str=fc_object_features_list_str)))
                        except Exception as e:
                            myutil.print_and_log(message="Did not write FC properties to file: {}. {}".format(fc, e),
                                                 log_level=myutil.WARNING_LEVEL)
                    if TURN_ON_UPSERT_OUTPUT_TO_SOCRATA.value:
                        try:
                            myutil.upsert_to_socrata(client=socrata_featureclass_client,
                                                     dataset_identifier=featureclasslevel_app_id,
                                                     zipper=myutil.make_dict_zipper(
                                                         first_list=FeatureClassObjects_Class.FeatureClassObject.FC_HEADERS_LIST.value,
                                                         second_list=fc_object_features_list_str))
                            myutil.print_and_log("\tUpserted FC: {}".format(fc_obj.fc_name), myutil.INFO_LEVEL)
                        except Exception as e:
                            myutil.print_and_log(
                                message="Rrror upserting to Socrata: {}. {}".format(fc_obj.fc_name, e),
                                log_level=myutil.WARNING_LEVEL)

                    # FC's Fields Metadata Inspection
                    myutil.print_and_log("\t\tProcessing Fields - FC: {}".format(fc_obj.fc_name), myutil.INFO_LEVEL)
                    for field_object in fc_field_objects_list:
                        field_id = myutil.generate_id_from_args(fc_id, field_object.name)
                        field_row_id = myutil.generate_id_from_args(field_id, myutil.build_today_date_string())
                        field_total_null_value_count = fc_fields_null_value_tracker_dict[field_object.name]
                        field_percent_null = myutil.calculate_percent(field_total_null_value_count, number_of_fc_features)

                        # Instantiate the FC field details object
                        fc_field_details_obj = FeatureClassObjects_Class.FeatureClassFieldDetails(field_id=field_id,
                                                                                                  fc_id=fc_id,
                                                                                                  field_object=field_object,
                                                                                                  total_record_count=number_of_fc_features,
                                                                                                  total_null_value_count=field_total_null_value_count,
                                                                                                  percent_null=field_percent_null,
                                                                                                  date_export=myutil.build_today_date_string(),
                                                                                                  row_id=field_row_id)
                        if field_object.name in string_fields_character_tracker_dict.keys():
                            fc_field_details_obj.field_max_chars_used = string_fields_character_tracker_dict[fc_field_details_obj.field_name]

                        # Write the field details object to file
                        field_object_feature_list = fc_field_details_obj.create_object_field_feature_list()
                        field_object_feature_list_str = fc_field_details_obj.create_object_field_feature_list_str(
                            object_field_feature_list=field_object_feature_list)
                        if TURN_ON_WRITE_OUTPUT_TO_CSV.value:
                            try:
                                fhand_fields_file_handler.write("{}\n".format(
                                    fc_field_details_obj.create_CSV_feature_class_field_properties_string(
                                        object_field_features_list_str=field_object_feature_list_str)))
                            except Exception as e:
                                # For fc field details that don't process this records their presence so not undocumented.
                                myutil.print_and_log(message="Did not write FC field details to file: {}{}".format(
                                    fc_field_details_obj.row_id, e),
                                    log_level=myutil.WARNING_LEVEL)
                        if TURN_ON_UPSERT_OUTPUT_TO_SOCRATA.value:
                            try:
                                myutil.upsert_to_socrata(client=socrata_featureclass_fields_client,
                                                         dataset_identifier=fieldlevel_app_id,
                                                         zipper=myutil.make_dict_zipper(
                                                             first_list=FeatureClassObjects_Class.FeatureClassFieldDetails.FIELD_HEADERS_LIST.value,
                                                             second_list=field_object_feature_list_str))
                            except Exception as e:
                                myutil.print_and_log(
                                    message="Error upserting to Socrata: {}. {}. {}".format(fd, fc, e),
                                    log_level=myutil.WARNING_LEVEL)
        except Exception as e:
            myutil.print_and_log(
                message="Problem iterating through FC's within FD: {}. {}".format(fd, e),log_level=myutil.WARNING_LEVEL)
        finally:
            if TURN_ON_WRITE_OUTPUT_TO_CSV.value:
                fhand_featureclass_file_handler.close()
                fhand_fields_file_handler.close()
            if TURN_ON_UPSERT_OUTPUT_TO_SOCRATA.value:
                socrata_featureclass_client.close()
                socrata_featureclass_fields_client.close()

    myutil.print_and_log(
        message=" {} Script Completed".format(myutil.get_date_time_for_logging_and_printing()),
        log_level=myutil.INFO_LEVEL)
    return

if __name__ == "__main__":
    main()
