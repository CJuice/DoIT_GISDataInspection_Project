"""

NOTE: When dataset is pulled from Socrata, the numbers come with thousands separator commas. These will cause issues
unless removed before processing. In Excel, change the column type to Numbers with no thousand separators or replace
them programmatically.

"""


def main():

    # IMPORTS
    import pandas as pd

    # VARIABLES
    godi_results_dataset_level_csv = r"GODI_datasets_results_cleaned.csv"
    godi_results_field_level_csv = r"GODI_fields_results_cleaned.csv"
    godi_dataset_output_csv = r"GODI_datasets_cleaned_output.csv"
    godi_field_output_csv = r"GODI_fields_cleaned_output.csv"
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
    def revise_names(godi_value):
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

    def replace_values(dataframe, column_list):
        for column in column_list:
            # print(f"\n{column}")
            dataframe[column] = dataframe[column].apply(func=revise_names)
        return dataframe

    # FUNCTIONALITY
    # GODI Dataset Level
    df_datasets_level = pd.read_csv(filepath_or_buffer=godi_results_dataset_level_csv)
    print(df_datasets_level.info())
    cols_to_change_datasetlevel = ["Name", "FC_ID", "ROW_ID"]
    df_datasets_level = replace_values(dataframe=df_datasets_level, column_list=cols_to_change_datasetlevel)
    df_datasets_level.to_csv(path_or_buf=godi_dataset_output_csv, index=False)

    # GODI Field Level
    df_field_level = pd.read_csv(filepath_or_buffer=godi_results_field_level_csv)
    print(df_field_level.info())
    cols_to_change_fieldlevel = ["FLD_ID", "FC_ID", "ROW_ID"]
    df_field_level = replace_values(dataframe=df_field_level, column_list=cols_to_change_fieldlevel)
    df_field_level.to_csv(path_or_buf=godi_field_output_csv, index=False)


if __name__ == "__main__":
    main()
