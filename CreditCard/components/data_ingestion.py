from CreditCard.entity.config_entity import DataIngestionConfig
import sys,os
from CreditCard.Exception import CreditException
from CreditCard.logger import logging
from CreditCard.entity.artifact_entity import DataIngestionArtifact
import tarfile
import numpy as np
from six.moves import urllib
import pandas as pd
import zipfile,shutil
from sklearn.model_selection import train_test_split
from CreditCard.constants import *

class DataIngestion:

    def __init__(self,data_ingestion_config:DataIngestionConfig ):
        try:
            logging.info(f"{'>>'*20}Data Ingestion log started.{'<<'*20} ")
            self.data_ingestion_config = data_ingestion_config

        except Exception as e:
            raise CreditException(e,sys)
    

    def download_Credit_data(self,) -> str:
        try:
            

            #folder location to download file
            tgz_download_dir = self.data_ingestion_config.tgz_download_dir

            tgz_file_name = self.data_ingestion_config.tgz_file_name
            
            if os.path.exists(tgz_download_dir):
                os.remove(tgz_download_dir)

            os.makedirs(tgz_download_dir,exist_ok=True)

           

            Source_dir = ROOT_DIR
            source_file = os.path.join(Source_dir,tgz_file_name)

            shutil.copy(source_file,tgz_download_dir)

            tgz_file_path = os.path.join(tgz_download_dir,tgz_file_name)

            logging.info(f"File :[{tgz_file_path}] has been downloaded successfully.")
            return tgz_file_path

        except Exception as e:
            raise CreditException(e,sys) from e

    def extract_tgz_file(self,tgz_file_path:str):
        try:
            raw_data_dir = self.data_ingestion_config.raw_data_dir

            if os.path.exists(raw_data_dir):
                os.remove(raw_data_dir)

            os.makedirs(raw_data_dir,exist_ok=True)


            logging.info(f"Extracting tgz file: [{tgz_file_path}] into dir: [{raw_data_dir}]")

            with zipfile.ZipFile(tgz_file_path,'r') as extract:
                extract.extractall(raw_data_dir)

            file_name = os.listdir(raw_data_dir)[0]
            Credit_file_path = os.path.join(raw_data_dir,file_name)
            credit_data_frame = pd.read_csv(Credit_file_path)
            credit_data_frame.rename(mapper={'default.payment.next.month':"default"},axis=1,inplace=True)
            credit_data_frame.to_csv(Credit_file_path,index=False)
            
            logging.info(f"Extraction completed")

        except Exception as e:
            raise CreditException(e,sys) from e
    
    def split_data_as_train_test(self) -> DataIngestionArtifact:
        try:
            raw_data_dir = self.data_ingestion_config.raw_data_dir

            file_name = os.listdir(raw_data_dir)[0]

            Credit_file_path = os.path.join(raw_data_dir,file_name)


            logging.info(f"Reading csv file: [{Credit_file_path}]")
            Credit_data_frame = pd.read_csv(Credit_file_path)

            convert_to_dict = {i:float for i in Credit_data_frame.columns.to_list()}
            Credit_data_frame = Credit_data_frame.astype(convert_to_dict)
            

            logging.info(f"Splitting data into train and test")
            strat_train_set = None
            strat_test_set = None

            strat_train_set,strat_test_set = train_test_split(Credit_data_frame)

            train_file_path = os.path.join(self.data_ingestion_config.ingested_train_dir,
                                            file_name)

            test_file_path = os.path.join(self.data_ingestion_config.ingested_test_dir,
                                        file_name)
            
            if strat_train_set is not None:
                os.makedirs(self.data_ingestion_config.ingested_train_dir,exist_ok=True)
                logging.info(f"Exporting training datset to file: [{train_file_path}]")
                strat_train_set.to_csv(train_file_path,index=False)

            if strat_test_set is not None:
                os.makedirs(self.data_ingestion_config.ingested_test_dir, exist_ok= True)
                logging.info(f"Exporting test dataset to file: [{test_file_path}]")
                strat_test_set.to_csv(test_file_path,index=False)
            

            data_ingestion_artifact = DataIngestionArtifact(train_file_path=train_file_path,
                                test_file_path=test_file_path,
                                is_ingested=True,
                                message=f"Data ingestion completed successfully."
                                )
            logging.info(f"Data Ingestion artifact:[{data_ingestion_artifact}]")
            return data_ingestion_artifact

        except Exception as e:
            raise CreditException(e,sys) from e

    def initiate_data_ingestion(self)-> DataIngestionArtifact:
        try:
            tgz_file_path =  self.download_Credit_data()
            self.extract_tgz_file(tgz_file_path=tgz_file_path)
            return self.split_data_as_train_test()
        except Exception as e:
            raise CreditException(e,sys) from e
    


    def __del__(self):
        logging.info(f"{'>>'*20}Data Ingestion log completed.{'<<'*20} \n\n")
