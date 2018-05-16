class DataStandardsObject(object):
    doLogging = False

    def __init__(self, fcName, arcpyDescribeObject):
        self.fcName = fcName
        self.arcpyDescribeObject = arcpyDescribeObject
        self.spatialRefName = arcpyDescribeObject.spatialReference.name
        self.boolMeetsLooseStandard = False
        self.boolMeetsStrictStandard = False
        # self.contactPerson = contactPerson

        # Store the standards for each required field in a dictionary containing a key and a tuple value. Access the dictionary during my checks of field details for meeting standard requirements.
        # Order of tuple components (exists, fieldName, fieldType, fieldDefValue, fieldDomain, fieldIsNullable, fieldLength, fieldPrecision, fieldScale, fieldRequired)
        # These standards are the "strict" version. The "loose" version that was previously upheld was the field name and type, and RN and AddnID were not included.
        ''' (EXISTS,NAME,TYPE,DEFVAL,DOMAIN,NULLABLE,LENGTH,PRECISION,SCALE,REQUIRED)'''
        self.tupRNStandard = (True,"RN","String","-9999","",False,11,0,0,True)
        self.tupADDN_IDStandard = (True,"ADDN_ID","String","-9999","",False,25,0,0,True)
        self.tupLAT_DDStandard = (True,"LAT_DD","Double",-99.0,"",False,8,8,6,True)
        self.tupLONG_DDStandard = (True,"LONG_DD","Double",-999.0,"",False,8,9,6,True)
        self.tupHORZ_METHStandard = (True,"HORZ_METH","String","UNKNOWN","HORZMETH",False,10,0,0,True)
        self.tupHORZ_ACCStandard = (True,"HORZ_ACC","Single",-9999,"",False,4,5,1,True) # Wow, despite the field type being created and existing as "Float", the field.type property is "Single"
        self.tupHORZ_REFStandard = (True,"HORZ_REF","String","OTHER","HORZREF",False,10,0,0,True)
        self.tupHORZ_DATEStandard = (True,"HORZ_DATE","Date","1/1/1970","HORZ_DATE",False,8,0,0,True) # HORZ_DATE is from MSW Domains
        self.tupHORZ_ORGStandard = (True,"HORZ_ORG","String","UNKNOWN","HORZORG",False,7,0,0,True)
        self.tupHORZ_DATUMStandard = (True,"HORZ_DATUM","String","UNKNOWN","HORZDATUM",False,7,0,0,True)
        self.dictStrictRequiredFields = {"RN":self.tupRNStandard,"ADDN_ID":self.tupADDN_IDStandard,"LAT_DD":self.tupLAT_DDStandard,"LONG_DD":self.tupLONG_DDStandard,\
                              "HORZ_METH":self.tupHORZ_METHStandard,"HORZ_ACC":self.tupHORZ_ACCStandard,"HORZ_REF":self.tupHORZ_REFStandard,\
                              "HORZ_DATE":self.tupHORZ_DATEStandard,"HORZ_ORG":self.tupHORZ_ORGStandard,"HORZ_DATUM":self.tupHORZ_DATUMStandard}

        self.dictLooseRequiredFields = {"LAT_DD":self.tupLAT_DDStandard,"LONG_DD":self.tupLONG_DDStandard,"HORZ_METH":self.tupHORZ_METHStandard,\
                                   "HORZ_ACC":self.tupHORZ_ACCStandard,"HORZ_REF":self.tupHORZ_REFStandard, "HORZ_DATE":self.tupHORZ_DATEStandard,\
                                   "HORZ_ORG":self.tupHORZ_ORGStandard,"HORZ_DATUM":self.tupHORZ_DATUMStandard}
        if DataStandardsObject.doLogging:
            print("Strict Standards:\n")
            for key in self.dictStrictRequiredFields.keys():
                t = self.dictStrictRequiredFields.get(key)
                print("Field: {0}, Exists: {1}, Type: {2}, Default: {3}, Domain: {4}, Nullable: {5}, Length: {6}, Precision: {7}, Scale: {8}, Required: {9}".format(t[1],t[0],t[2],t[3],t[4],t[5],t[6],t[7],t[8],t[9]))
            print("Loose Standards:\n")
            for key in self.dictLooseRequiredFields.keys():
                t = self.dictLooseRequiredFields.get(key)
                print("Field: {0}, Exists: {1}, Type: {2}".format(t[1],t[0],t[2]))

    def evaluateFC_LooseStandards(self):

        # make a list of the names of required fields
        lsLooseStandardRequiredFieldNames = self.dictLooseRequiredFields.keys()

        # make a list of field objects to be able to access the details that need to be checked
        lsFCFieldObjects = self.arcpyDescribeObject.fields

        intNumberOfRequiredFieldsToCheckFor = len(lsLooseStandardRequiredFieldNames)
        count = 0
        try:
            for field in lsFCFieldObjects:

                # get the tuple for the standard field of focus
                tupTemp = self.dictLooseRequiredFields.get(field.name)

                # Check for the required field names, if exist then check to see if type is correct. Increment count, compare count to length of required fields list.
                if (field.name in lsLooseStandardRequiredFieldNames) and (field.type == tupTemp[2] or field.type == "Double"): #FIXME: Though the standard is now "Single", current feature classes use "Double". Delete "Double" once on new standard.
                    count += 1
#                     print(self.fcName + ": " + field.name + " - " + str(count) + " of " + str(intNumberOfRequiredFieldsToCheckFor) + " fields meet standards."
                else:
                    pass
#                 print("\t\t\t", field.name, tupTemp, field.type
        except:
            print("Failed processing fields while checking loose standards")

        if count == intNumberOfRequiredFieldsToCheckFor:
            self.boolMeetsLooseStandard = True

    def evaluateFC_StrictStandards(self):
        doLogging = False

        # make a list of the names of required fields
        lsStrictStandardRequiredFieldNames = self.dictStrictRequiredFields.keys()

        # make a list of field objects to be able to access the details that need to be checked
        lsFCFieldObjects = self.arcpyDescribeObject.fields
        intNumberOfRequiredFieldsToCheckFor = len(lsStrictStandardRequiredFieldNames)
        count = 0
        try:
            if doLogging:
                print(self.fcName)
                print("Spatial Reference is GCS_North_American_1983? " + str(self.spatialRefName == "GCS_North_American_1983"))
            for field in lsFCFieldObjects:
#                 print("Location: ", 4, count
                # get the tuple for the standard field of focus, if it exists.
                tupTemp = self.dictStrictRequiredFields.get(field.name)
#                 print("Location: ", 4.5
                # Check for the required field names, if exist then check to see if type is correct. Increment count, compare count to length of required fields list.
                ''' (EXISTS,NAME,TYPE,DEFVAL,DOMAIN,NULLABLE,LENGTH,PRECISION,SCALE,REQUIRED)'''
                if doLogging:
                    try:
                        print(1,(field.name in lsStrictStandardRequiredFieldNames))
                        print(2,tupTemp[2],(field.type == tupTemp[2]))
                        print(3,(field.defaultValue == tupTemp[3]))
                        print(4,(field.domain == tupTemp[4]))
                        print(5,(field.isNullable == tupTemp[5]))
                        print(6,(field.length == tupTemp[6]))
                        print(7,(field.precision == tupTemp[7]))
                        print(8,(field.scale == tupTemp[8]))
                        print(9,(field.required == tupTemp[9]))
                    except:
                        print("Problem with my print(statements")
                    print(tupTemp)
                if (tupTemp != None) and (field.name in lsStrictStandardRequiredFieldNames) and (field.type == tupTemp[2]) and (field.defaultValue == tupTemp[3]) \
                 and (field.domain == tupTemp[4]) and (field.isNullable == tupTemp[5]) and (field.length == tupTemp[6]) and (field.precision == tupTemp[7]) \
                 and (field.scale == tupTemp[8]) and (field.required == tupTemp[9]) and (self.spatialRefName == "GCS_North_American_1983"):
#                     print("Location: ", 5
                    count += 1
#                     print(self.fcName + ": " + field.name + " - " + str(count) + " of " + str(intNumberOfRequiredFieldsToCheckFor) + " fields meet standards."
                else:
                    pass
#                 print("\t\t\t", field.name, tupTemp, field.type
        except:
            print("Failed processing fields while checking strict standards")

        if count == intNumberOfRequiredFieldsToCheckFor:
            self.boolMeetsStrictStandard = True


# try:
#     # Evaluate the Loose standards
#     FC.evaluateFC_LooseStandards()
# except:
#     print("Loose standards evaluation failed")
# try:
#     # Evaluate the Loose standards
#     FC.evaluateFC_StrictStandards()
# except:
#     print("Strict standards evaluation failed")