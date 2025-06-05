'''
An artifact entity in a machine learning or data pipeline project is typically a data structure (often a class or dataclass) that represents the outputs ("artifacts") produced by different pipeline steps.

For example, after data preprocessing, model training, or evaluation, you might want to store:

File paths to saved models or datasets
Metrics (accuracy, loss, etc.)
Configuration details
Any other outputs needed for later steps
By defining an artifact entity (using a @dataclass), you can easily pass these outputs between pipeline components in a structured and type-safe way.'''

from dataclasses import dataclass
@dataclass
class DataIngestionArtifact:
 trained_file_path:str
 test_file_path:str



@dataclass
class DataValidationArtifact:
 validation_status:bool
 valid_train_file_path:str
 valid_test_file_path:str
 invalid_train_file_path:str
 invalid_test_file_path:str
 drift_report_file_path:str

@dataclass
class DataTransformationArtifact:
 transformed_object_file_path:str
 transformed_train_file_path:str
 transformed_test_file_path:str

@dataclass
class ClassificationMetricArtifact:
 f1_score:float
 precision_score:float
 recall_score:float

@dataclass
class ModelTrainerArtifact:
 trained_model_file_path:str
 train_metric_artifact: ClassificationMetricArtifact
 test_metric_artifact: ClassificationMetricArtifact
 

