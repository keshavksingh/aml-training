from azure.identity import ClientSecretCredential
from azureml.core import Workspace
from azureml.core.experiment import Experiment
from azureml.core.compute import AmlCompute
from azureml.core.compute_target import ComputeTargetException
from azureml.core.compute import ComputeInstance
from azureml.core import Experiment,Environment
#from azureml.core.authentication import ClientSecretCredential
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core import ScriptRunConfig
from azureml.core.conda_dependencies import CondaDependencies
from azureml.pipeline.core import Pipeline
from azureml.pipeline.steps import PythonScriptStep, SynapseSparkStep
#Enter details of your AzureML workspace
subscription_id = 'XXX'
resource_group = 'mlops'
workspace_name = 'amlws'

tenant_id="******"
client_id="*************"
client_secret="*************"

# Create the credentials object
#creds = ClientSecretCredential(tenant_id, client_id, client_secret)
creds = ServicePrincipalAuthentication(
    tenant_id=tenant_id,
    service_principal_id=client_id,
    service_principal_password=client_secret
)

# Load the workspace from the subscription, resource group, and workspace name
ws = Workspace(subscription_id=subscription_id, resource_group=resource_group, workspace_name=workspace_name, auth=creds)

# Get the compute instance
spark_compute_name = "sparkcompute"
vm_cluster_compute_name = "generalpurposecomputecluster"
aks_compute_name = "aks-aml"


#from azureml.core.environment import CondaDependencies
conda_dep = CondaDependencies()
conda_dep.add_pip_package("mlflow")
conda_dep.add_pip_package("azureml-mlflow")
conda_dep.add_pip_package("azure-ai-ml")
conda_dep.add_pip_package("azureml-core")
conda_dep.add_pip_package("azure-identity")

from azureml.core import RunConfiguration
from azureml.core import ScriptRunConfig 
from azureml.core import Experiment

exp = Experiment(workspace=ws, name="AMLWS-PARALLEL-COMPUTE-IRIS-V1") 

run_config = RunConfiguration(framework="pyspark")
run_config.target = spark_compute_name

run_config.spark.configuration["spark.driver.memory"] = "1g" 
run_config.spark.configuration["spark.driver.cores"] = 2 
run_config.spark.configuration["spark.executor.memory"] = "1g" 
run_config.spark.configuration["spark.executor.cores"] = 1 
run_config.spark.configuration["spark.executor.instances"] = 1 
step_1 = PythonScriptStep(source_directory = 'C:/Users/home/Downloads/pythonprojects/aml/ScheduleJob',
                          script_name='Train.py',
                          compute_target=spark_compute_name,
                          runconfig = run_config,
                          allow_reuse=False)

run_config = RunConfiguration()
run_config.target = vm_cluster_compute_name
step_2 = PythonScriptStep(source_directory = 'C:/Users/home/Downloads/pythonprojects/aml/ScheduleJob',
                          script_name='Train-VM.py',
                          compute_target=vm_cluster_compute_name,
                          runconfig = run_config,
                          allow_reuse=False)

run_config = RunConfiguration(conda_dependencies=conda_dep)
run_config.target = aks_compute_name
step_3 = PythonScriptStep(source_directory = 'C:/Users/home/Downloads/pythonprojects/aml/ScheduleJob',
                          script_name='Train-AKS.py',
                          compute_target=aks_compute_name,
                          runconfig = run_config,
                          allow_reuse=False)

pipeline = Pipeline(workspace=ws, steps=[step_1,step_2,step_3])
pipeline_run = pipeline.submit("AMLWS-PARALLEL-COMPUTE-IRIS-V1", regenerate_outputs=True)
