from networksecurity.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from scipy.stats import ks_2samp
import pandas as pd
import os,sys
from networksecurity.utils.main_utils.utils import read_yaml_file
from networksecurity.utils.main_utils.utils import write_yaml_file
'''  Data drift refers to a change in the statistical properties of your input data over time,
 compared to the data your machine learning model was originally trained on.

Why does it matter?
If data drift occurs, your model may make less accurate predictions because it is seeing data that is different
 from what it learned.
Data drift can happen due to changes in user behavior, external factors, data collection methods, 
or other reasons.
'''

class DataValidation:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,
                 data_validation_config:DataValidationConfig):
        
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)

        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    #create a function for reading data (staticType)
    @staticmethod
    def read_data(file_path)->pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        

    def validate_number_of_columns(self,dataframe:pd.DataFrame)->bool:
        try:
            number_of_columns=len(self._schema_config)
            logging.info(f"required number of columns:{number_of_columns}")
            logging.info(f"Data frame has columns:{len(dataframe.columns)}")
            if len(dataframe.columns)==number_of_columns:
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    ## data drift detector function lega current vala data frame,shuru vala dataframe aur threshold parameter
    #  agar threshold se zyada drift hua to Datadrift ho gya hai bhot zyada dont do calculations with current model
    def detect_dataset_drift(self,base_df,current_df,threshold=0.05)->bool:
        try:
            status=True
            report={}
            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]

                ##k2_2samp use hota hai 2 dataframe me drift nikalne ke liye
                ##drift value nikal ke d1 aur d2 ki humne is_same_dist me store kra dii
                is_same_dist=ks_2samp(d1,d2)
                if threshold<=is_same_dist.pvalue:
                    is_found=False
                else:
                    is_Found=True
                    status=False
                report.update({column:{
                    "p_value":float(is_same_dist.pvalue),
                    "drift_status":is_found
                }})
                drift_report_file_path=self.data_validation_config.drift_report_file_path

                #Create directory
                dir_path = os.path.dirname(drift_report_file_path)
                os.makedirs(dir_path,exist_ok=True)
                write_yaml_file(file_path=drift_report_file_path,content=report)

        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
        
    ##create data validation intiation function having return type "DataIngestionArtifact"
    def initiate_data_validation(self)->DataIngestionArtifact:
        try:
            train_file_path=self.data_ingestion_artifact.trained_file_path
            test_file_path=self.data_ingestion_artifact.test_file_path

            ##read the data from train and test
            train_dataframe = DataValidation.read_data(train_file_path)
            test_dataframe=DataValidation.read_data(test_file_path)

            ##validate number of columns
            status = self.validate_number_of_columns(dataframe=train_dataframe)
            if not status:
                error_message=f"Train dataFrame does not contain all columns.\n"
            status = self.validate_number_of_columns(dataframe=test_dataframe)
            if not status:
                error_message=f"Test dataframe does not contain all columns.\n"

            ##check data Drift
            status = self.detect_dataset_drift(base_df=train_dataframe,current_df=test_dataframe)
            dir_path=os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path,exist_ok=True)

            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path,index=False,header=True
            )
            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path,index=False,header=True
            )
            data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_ingestion_artifact.trained_file_path,
                valid_test_file_path=self.data_ingestion_artifact.test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )
            return data_validation_artifact

        except Exception as e:
            raise NetworkSecurityException(e,sys)


