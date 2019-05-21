"""
Clean GODI results to address changes in feature class names but no change to actual data values.

Changes to feature class names and presence in the geodatabase have lead to some poor quality data in our sde. GODI
inspects the geodatbase monthly and provides metrics on the contents. As we clean up our practices and standards the
historical runs will be out of sync with the new runs for the same datasets. This script assists with cleaning the
historical runs so that they are consistent with modern names. For instance, a feature class previously named
my_feature_class may have been updated to my_feature_class_DOIT. This will result in two separate visualizations with
non-overlapping date ranges when really this is the same dataset and the results should be visualized together, not as
two separate datasets.

NOTE: When dataset is pulled from Socrata, the numbers come with thousands separator commas. These will cause issues
unless removed before processing. In Excel, change the column type to Numbers with no thousand separators or replace
them programmatically.

"""


def main():

    # IMPORTS
    import pandas as pd

    # VARIABLES
    cols_to_change_datasetlevel = ["Name", "FC_ID", "ROW_ID"]
    cols_to_change_fieldlevel = ["FLD_ID", "FC_ID", "ROW_ID"]
    godi_dataset_output_csv = r"GODI_datasets_cleaned_output.csv"
    godi_field_output_csv = r"GODI_fields_cleaned_output.csv"
    godi_results_dataset_level_csv = r"GODI_datasets_results_cleaned.csv"
    godi_results_field_level_csv = r"GODI_fields_results_cleaned.csv"
    replace_dict = {'SOCI_SportVenues_Archery': 'SOCI_Archery_MDSports',
                    'SOCI_SportVenues_AutoRacing': 'SOCI_AutoRacing_MDSports',
                    'SOCI_SportVenues_BMX': 'SOCI_BMX_MDSports',
                    'SOCI_SportVenues_Badminton': 'SOCI_Badminton_MDSports',
                    'SOCI_SportVenues_Baseball': 'SOCI_Baseball_MDSports',
                    'SOCI_SportVenues_Basketball': 'SOCI_Basketball_MDSports',
                    'SOCI_SportVenues_BeachVolleyball': 'SOCI_BeachVolleyball_MDSports',
                    'SOCI_SportVenues_Boating': 'SOCI_Boating_MDSports',
                    'SOCI_SportVenues_Bowling': 'SOCI_Bowling_MDSports',
                    'SOCI_SportVenues_Boxing': 'SOCI_Boxing_MDSports',
                    'SOCI_SportVenues_Broomball': 'SOCI_Broomball_MDSports',
                    'SOCI_SportVenues_CheerDance': 'SOCI_CheerDance_MDSports',
                    'SOCI_SportVenues_Cricket': 'SOCI_Cricket_MDSports',
                    'SOCI_SportVenues_CrossCountry': 'SOCI_CrossCountry_MDSports',
                    'SOCI_SportVenues_CrossCountrySkiing': 'SOCI_CrossCountrySkiing_MDSports',
                    'SOCI_SportVenues_Curling': 'SOCI_Curling_MDSports',
                    'SOCI_SportVenues_Cycling': 'SOCI_Cycling_MDSports',
                    'SOCI_SportVenues_DiscGolf': 'SOCI_DiscGolf_MDSports',
                    'SOCI_SportVenues_Diving': 'SOCI_Diving_MDSports',
                    'SOCI_SportVenues_DodgeBall': 'SOCI_DodgeBall_MDSports',
                    'SOCI_SportVenues_Equestrian': 'SOCI_Equestrian_MDSports',
                    'SOCI_SportVenues_ExtremeSports': 'SOCI_ExtremeSports_MDSports',
                    'SOCI_SportVenues_Fencing': 'SOCI_Fencing_MDSports',
                    'SOCI_SportVenues_FieldHockey': 'SOCI_FieldHockey_MDSports',
                    'SOCI_SportVenues_Fishing': 'SOCI_Fishing_MDSports',
                    'SOCI_SportVenues_FlagFootball': 'SOCI_FlagFootball_MDSports',
                    'SOCI_SportVenues_Football': 'SOCI_Football_MDSports',
                    'SOCI_SportVenues_Futsal': 'SOCI_Futsal_MDSports',
                    'SOCI_SportVenues_Golf': 'SOCI_Golf_MDSports',
                    'SOCI_SportVenues_Gymnastics': 'SOCI_Gymnastics_MDSports',
                    'SOCI_SportVenues_HorseRacing': 'SOCI_HorseRacing_MDSports',
                    'SOCI_SportVenues_Hunting': 'SOCI_Hunting_MDSports',
                    'SOCI_SportVenues_IceHockey': 'SOCI_IceHockey_MDSports',
                    'SOCI_SportVenues_IceSkating': 'SOCI_IceSkating_MDSports',
                    'SOCI_SportVenues_IndoorSports': 'SOCI_IndoorSports_MDSports',
                    'SOCI_SportVenues_IndoorTrack': 'SOCI_IndoorTrack_MDSports',
                    'SOCI_SportVenues_Judo': 'SOCI_Judo_MDSports',
                    'SOCI_SportVenues_Karate': 'SOCI_Karate_MDSports',
                    'SOCI_SportVenues_Kayaking': 'SOCI_Kayaking_MDSports',
                    'SOCI_SportVenues_Kickball': 'SOCI_Kickball_MDSports',
                    'SOCI_SportVenues_Lacrosse': 'SOCI_Lacrosse_MDSports',
                    'SOCI_SportVenues_MartialArts': 'SOCI_MartialArts_MDSports',
                    'SOCI_SportVenues_Motorsports': 'SOCI_Motorsports_MDSports',
                    'SOCI_SportVenues_MountainBiking': 'SOCI_MountainBiking_MDSports',
                    'SOCI_SportVenues_Orienteering': 'SOCI_Orienteering_MDSports',
                    'SOCI_SportVenues_Other': 'SOCI_Other_MDSports',
                    'SOCI_SportVenues_Paintball': 'SOCI_Paintball_MDSports',
                    'SOCI_SportVenues_Polo': 'SOCI_Polo_MDSports',
                    'SOCI_SportVenues_Racquetball': 'SOCI_Racquetball_MDSports',
                    'SOCI_SportVenues_Rafting': 'SOCI_Rafting_MDSports',
                    'SOCI_SportVenues_RockClimbing': 'SOCI_RockClimbing_MDSports',
                    'SOCI_SportVenues_Rodeo': 'SOCI_Rodeo_MDSports',
                    'SOCI_SportVenues_RollerSports': 'SOCI_RollerSports_MDSports',
                    'SOCI_SportVenues_RowingCrew': 'SOCI_RowingCrew_MDSports',
                    'SOCI_SportVenues_Rugby': 'SOCI_Rugby_MDSports',
                    'SOCI_SportVenues_RunningSports': 'SOCI_RunningSports_MDSports',
                    'SOCI_SportVenues_Sailing': 'SOCI_Sailing_MDSports',
                    'SOCI_SportVenues_Shooting': 'SOCI_Shooting_MDSports',
                    'SOCI_SportVenues_Skateboarding': 'SOCI_Skateboarding_MDSports',
                    'SOCI_SportVenues_Skiing': 'SOCI_Skiing_MDSports',
                    'SOCI_SportVenues_Snowboarding': 'SOCI_Snowboarding_MDSports',
                    'SOCI_SportVenues_Soccer': 'SOCI_Soccer_MDSports',
                    'SOCI_SportVenues_Softball': 'SOCI_Softball_MDSports',
                    'SOCI_SportVenues_SpeedSkating': 'SOCI_SpeedSkating_MDSports',
                    'SOCI_SportVenues_Squash': 'SOCI_Squash_MDSports',
                    'SOCI_SportVenues_Swimming': 'SOCI_Swimming_MDSports',
                    'SOCI_SportVenues_SynchronizedSwimming': 'SOCI_SynchronizedSwimming_MDSports',
                    'SOCI_SportVenues_TableSports': 'SOCI_TableSports_MDSports',
                    'SOCI_SportVenues_TaeKwonDoe': 'SOCI_TaeKwonDoe_MDSports',
                    'SOCI_SportVenues_TeamHandball': 'SOCI_TeamHandball_MDSports',
                    'SOCI_SportVenues_Tennis': 'SOCI_Tennis_MDSports',
                    'SOCI_SportVenues_TrackField': 'SOCI_TrackField_MDSports',
                    'SOCI_SportVenues_Triathlon': 'SOCI_Triathlon_MDSports',
                    'SOCI_SportVenues_UltimateFrisbee': 'SOCI_UltimateFrisbee_MDSports',
                    'SOCI_SportVenues_Volleyball': 'SOCI_Volleyball_MDSports',
                    'SOCI_SportVenues_WaterPolo': 'SOCI_WaterPolo_MDSports',
                    'SOCI_SportVenues_WaterSports': 'SOCI_WaterSports_MDSports',
                    'SOCI_SportVenues_Weightlifting': 'SOCI_Weightlifting_MDSports',
                    'SOCI_SportVenues_Wrestling': 'SOCI_Wrestling_MDSports'}

    # FUNCTIONS
    def replace_values(dataframe: pd.DataFrame, column_list: list) -> pd.DataFrame:
        """
        Apply custom function to column series
        :param dataframe: dataframe from csv file of results from GODI runs
        :param column_list: list of column names in the results dataset that need the function applied
        :return: dataframe with cleaned values
        """
        for column in column_list:
            dataframe[column] = dataframe[column].apply(func=revise_names)
        return dataframe

    def revise_names(godi_value: str) -> str:
        """
        Replace sought value with sustitute, focusing on sportvenues at time of design.
        :param godi_value: str data value from columns series
        :return: string
        """
        if "sportvenues" in godi_value.lower():
            pass
        else:
            return godi_value

        for key, value in replace_dict.items():
            if key in godi_value:
                result = godi_value.replace(key, value)
                # print(f"\tREVISED: {result}")
                return result
            else:
                continue

        return godi_value

    # FUNCTIONALITY
    # GODI Dataset Level
    df_datasets_level = pd.read_csv(filepath_or_buffer=godi_results_dataset_level_csv)
    # print(df_datasets_level.info())
    df_datasets_level = replace_values(dataframe=df_datasets_level, column_list=cols_to_change_datasetlevel)
    df_datasets_level.to_csv(path_or_buf=godi_dataset_output_csv, index=False)

    # GODI Field Level
    df_field_level = pd.read_csv(filepath_or_buffer=godi_results_field_level_csv)
    # print(df_field_level.info())
    df_field_level = replace_values(dataframe=df_field_level, column_list=cols_to_change_fieldlevel)
    df_field_level.to_csv(path_or_buf=godi_field_output_csv, index=False)


if __name__ == "__main__":
    main()
