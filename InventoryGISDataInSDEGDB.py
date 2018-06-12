"""
Access an sde geodatabase and inventory the feature classes and inspect the data.
TODO Upsert results to Socrata dataset
Inputs:  User defined folder choice (integer)
Outputs:
Compatibility: Revised on 20180118 for Python 3.6 (ESRI ArcPro python version)
Author:  CJuice
Date:  05/17/2018
Revised:  Forked from EnterpriseGDBIntentory project. Tailored to DoIT needs for GIS data inspection.
Modifications:
"""
# TODO: To avoid false zero values in counter dictionaries may need to set initial value to database flag and add functionality to check for flag and reset to zero on first time through
#_______________________________________________________________________________________________________________________
# IMPORTS
from collections import namedtuple
from datetime import date
from UtilityClass import UtilityClassFunctionality as myutil
import FeatureClassObjects_Class
import GeodatabaseDomain_Class
import logging
import os
import time

#_______________________________________________________________________________________________________________________
# VARIABLES
    #CONSTANTS
Variable = namedtuple("Variable", "value") # named tuple definition
DATABASE_FLAG_NUMERIC = Variable(value=-9999)
DOMAINS_INVENTORY_FILE_NAME = Variable(value="GeodatabaseDomainsInventory")
FC_INVENTORY_FILE_NAME = Variable(value="FeatureClassInventory")
FIELD_INVENTORY_FILE_NAME = Variable(value="FeatureClassFIELDSInventory")
LOG_FILE_NAME = Variable(value="EnterpriseGDBInventory_LOG.log")
ROOT_PATH_FOR_CSV_OUTPUT = Variable(value=r"E:\DoIT_GISDataInspection_Project\OUTPUT_CSVs")
ROOT_URL_FOR_DATASET_ACCESS = Variable(value=r"https://data.maryland.gov/resource/")
# SOCRATA_CREDENTIALS_JSON_FILE = Variable(value="")  #TODO

    #non-constants
domain_objects_list = None
feature_classes_list = None
feature_dataset_ADMs_list = []
feature_datasets_list = None
feature_dataset_names_list = []
feature_dataset_parts_dict = {}
output_file_directory = r"E:\DoIT_GISDataInspection_Project\OUTPUT_CSVs"       #TESTING
output_file_names_tuple = (myutil.build_csv_file_name_with_date( myutil.build_today_date_string(), FC_INVENTORY_FILE_NAME.value),
                           myutil.build_csv_file_name_with_date(myutil.build_today_date_string(), FIELD_INVENTORY_FILE_NAME.value),
                           myutil.build_csv_file_name_with_date(myutil.build_today_date_string(), DOMAINS_INVENTORY_FILE_NAME.value))
round_count = 0
SDE_file_path = r"E:\DoIT_GISDataInspection_Project\SDE_CONNECTION_FILE\Production as sde on gis-ags-imap01p.mdgov.maryland.gov.sde"    #TESTING

def main():
    #_______________________________________________________________________________________________________________________
    # LOGGING setup
    logging.basicConfig(filename=LOG_FILE_NAME.value, level=logging.INFO)
    myutil.print_and_log(
        message=" {} - {} Initiated".format(myutil.get_date_time_for_logging_and_printing(), os.path.basename(__file__)),
        log_level=myutil.INFO_LEVEL)

    #_______________________________________________________________________________________________________________________
    # FUNCTIONS
    def create_output_results_file_handler(output_filename):
        try:
            fhand = open(output_filename, "a")
        except Exception as e:
            myutil.print_and_log(message="File did not open. {}. {}".format(output_filename, e),
                                 log_level=myutil.ERROR_LEVEL)
            exit()
        else:
            return fhand

    @myutil.capture_and_print_geoprocessing_errors
    def run_ESRI_GP_tool(func, *args, **kwargs):
        """Pass ESRI geoprocessing function and arguments through Decorator containing error handling functionality"""
        return func(*args, **kwargs)

    #_______________________________________________________________________________________________________________________
    # FUNCTIONALITY
    import arcpy # delayed arcpy import for performance

    # OUTPUT FILES: Create the new output files for the feature class inventory with headers
    output_feature_class_file, output_fields_file, output_domains_file = tuple(
        [os.path.join(output_file_directory, item) for item in output_file_names_tuple])
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

    # DOMAINS: make a list of domains for the geodatabase workspace environment.
    sde_environment_filename = os.path.basename(SDE_file_path)
    fhand_domains_file_handler = create_output_results_file_handler(output_filename=output_domains_file)
    try:
        domain_objects_list = run_ESRI_GP_tool(arcpy.da.ListDomains)
    except Exception as e:
        myutil.print_and_log(message="arcpy.da.ListDomains() failed. {}".format(e),log_level=myutil.ERROR_LEVEL)
        exit()
    else:
        for domain_object in domain_objects_list:
            gdb_domain_obj = GeodatabaseDomain_Class.GeodatabaseDomains(environment_name=sde_environment_filename,
                                                                        domain_object=domain_object,
                                                                        date=myutil.build_today_date_string())
            try:
                fhand_domains_file_handler.write("{}\n".format(gdb_domain_obj.generate_domain_properties_string()))
            except Exception as e:
                myutil.print_and_log(message="Did not write domains properties to file: {}. {}".format(domain_object.name, e),
                    log_level=myutil.WARNING_LEVEL)
    finally:
        fhand_domains_file_handler.close()

    # FEATURES: make a list of FD's present.
    feature_datasets_list = None
    try:
        feature_datasets_list = run_ESRI_GP_tool(arcpy.ListDatasets)
    except Exception as e:
        myutil.print_and_log(message="arcpy.ListDatasets did not run properly. {}".format(e), log_level=myutil.ERROR_LEVEL)
        exit()

    """Inspect each FD, then all FC's within, then fields of each FC. Assumption: DoIT naming is a three part 
    convention. Environment_Name.SDE.Entity_Data_Name for example Production.SDE.Transportation_Mile_Markers_etc .
     Coded for this, makes code brittle"""
    feature_datasets_list.sort()
    # FD Inspection
    for fd in feature_datasets_list:
        myutil.print_and_log(message="Examining FD: {}".format(fd),log_level=myutil.INFO_LEVEL)
        production_fd, sde_fd_ID, feature_dataset_name = fd.split(".") # first two vars are not used


        # FEATURE DATASET ISOLATION - TESTING
        # if feature_dataset_name != "PlanningCadastre_MD_LandUseLandCover":
        #     continue


        # Step into each feature dataset by altering the workspace
        arcpy.env.workspace = os.path.join(SDE_file_path, fd)
        feature_classes_list = None
        try:
            feature_classes_list = run_ESRI_GP_tool(arcpy.ListFeatureClasses)
        except Exception as e:
            myutil.print_and_log(message="Error creating list of FC's inside of FD: {}. {}".format(fd, e),
                                 log_level=myutil.WARNING_LEVEL)

        # Open the CSV files in preparation for writing data on all feature classes in a feature dataset
        fhand_featureclass_file_handler = create_output_results_file_handler(output_filename=output_feature_class_file)
        fhand_fields_file_handler = create_output_results_file_handler(output_filename=output_fields_file)

        # FC's Inspection
        print("\tFC List: {}".format(feature_classes_list))
        try:
            for fc in feature_classes_list:
                production_fc, sde_fc_ID, feature_class_name = fc.split(".") # first two vars are not used


                # FEATURE CLASS ISOLATION - TESTING
                # if feature_class_name != "PLAN_CountyLandUseLandCover2010_MDP":
                #     continue


                fc_id = myutil.generate_id_from_args(fd, feature_class_name)
                fc_row_id = myutil.generate_id_from_args(fc_id, myutil.build_today_date_string())
                number_of_fc_features = DATABASE_FLAG_NUMERIC.value

                # Instantiate object. Set other finicky parameters as they become available. Write out at end.
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
                    fhand_featureclass_file_handler.write(
                        "{}\n".format(fc_obj.generate_feature_class_properties_string()))
                    myutil.print_and_log(
                        message="{}. {}".format(
                            "Error generating Describe Object. Basic FC object record written. Fields object skipped.",
                            e),
                        log_level=myutil.ERROR_LEVEL)
                    continue
                else:
                    # If successful Describe object returned, proceed with next stage of analysis
                    fc_obj.data_type = fc_desc.dataType
                    fc_obj.shape_type = fc_desc.shapeType
                    fc_obj.spatial_ref_name = fc_desc.spatialReference.name
                    fc_field_objects_list = fc_desc.fields
                    fc_field_names_list = [field_obj.baseName for field_obj in fc_field_objects_list]

                    #NOTE: Due to a SQL error, needed to created prevent_SQL_error() function
                    #ERROR: "Attribute column not found [42S22:[Microsoft][ODBC Driver 13 for SQL Server][SQL Server]Invalid column name 'AREA'.]"
                    fc_field_names_list, fc_field_objects_list = myutil.prevent_SQL_error(fc_field_names_list, fc_field_objects_list)
                    fc_field_name_to_obj_dict = dict(zip(fc_field_names_list, fc_field_objects_list))
                    total_field_count = len(fc_field_objects_list)
                    fc_obj.total_field_count = total_field_count
                    total_value_count = myutil.calculate_total_number_of_values_in_dataset(
                        total_records_processed=number_of_fc_features,
                        number_of_fields_in_dataset=total_field_count,
                        database_flag=DATABASE_FLAG_NUMERIC.value)
                    fc_obj.total_value_count = total_value_count
                    fc_fields_null_value_tracker_dict = {field_obj.name : 0 for field_obj in fc_field_objects_list}
                    max_chars_used = DATABASE_FLAG_NUMERIC.value
                    string_fields_character_tracker_dict = {field_obj.name : max_chars_used for field_obj in fc_field_objects_list if field_obj.type.lower() == "string"}

                    # Access data values and analyze
                    try:
                        with arcpy.da.SearchCursor(fc, fc_field_names_list) as feature_class_cursor:
                            for row in feature_class_cursor:
                                row_dictionary = myutil.make_zipper(dataset_headers_list=fc_field_names_list,
                                                                    record_list=row)
                                # evaluate data and inventory the null/empty data values
                                myutil.inspect_record_for_null_values(field_null_count_dict=fc_fields_null_value_tracker_dict,
                                                                      record_dictionary=row_dictionary)
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
                    try:
                        fhand_featureclass_file_handler.write("{}\n".format(fc_obj.generate_feature_class_properties_string()))
                    except Exception as e:
                        myutil.print_and_log(message="Did not write FC properties to file: {}. {}".format(fc, e),
                                             log_level=myutil.WARNING_LEVEL)

                    # FC's Fields Metadata Inspection
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
                        try:
                            # print(fc_field_details_obj.generate_feature_class_field_properties_string())
                            fhand_fields_file_handler.write("{}\n".format(
                                fc_field_details_obj.generate_feature_class_field_properties_string()))
                        except Exception as e:
                            # For fc field details that don't process this records their presence so not undocumented.
                            myutil.print_and_log(message="Did not write FC field details to file: {}{}".format(fc_field_details_obj.row_id, e),
                                                 log_level=myutil.WARNING_LEVEL)
        except Exception as e:
            myutil.print_and_log(
                message="Problem iterating through FC's within FD: {}. {}".format(fd, e),log_level=myutil.WARNING_LEVEL)
        finally:
            fhand_featureclass_file_handler.close()
            fhand_fields_file_handler.close()

    print("\nScript completed.")
    return

if __name__ == "__main__":
    main()
