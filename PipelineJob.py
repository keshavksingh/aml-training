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
subscription_id = ''
resource_group = ''
workspace_name = ''

tenant_id=""
client_id=""
client_secret=""

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
compute_name = "sparkcompute"
try:
    compute_instance = ComputeInstance(workspace=ws, name=compute_name)
    print(f"Found existing compute instance: {compute_name}")
except ComputeTargetException:
    print(f"Not Found compute instance: {compute_name}")

# Create an experiment
#experiment_name = "Local-IRIS-V1"
#experiment = Experiment(workspace=ws, name=experiment_name)

# Set the script parameters for the notebook run
#notebook_path = "Users/keshav_singh/TrainMLFlow.ipynb"
#params = {"ExperimentName": experiment_name}

#experiment = Experiment(workspace=ws, name=experiment_name)
#list_experiments = Experiment.list(ws)

#list_runs = experiment.get_runs()
#for run in list_runs:
#    print(run.id)

#from azureml.core.environment import CondaDependencies
#conda_dep = CondaDependencies()
#conda_dep.add_pip_package("azure-mlflow==1.49.0")
#conda_dep.add_pip_package("azure-ai-ml")

from azureml.core import RunConfiguration
from azureml.core import ScriptRunConfig 
from azureml.core import Experiment

run_config = RunConfiguration(framework="pyspark")
run_config.target = compute_name

run_config.spark.configuration["spark.driver.memory"] = "1g" 
run_config.spark.configuration["spark.driver.cores"] = 2 
run_config.spark.configuration["spark.executor.memory"] = "1g" 
run_config.spark.configuration["spark.executor.cores"] = 1 
run_config.spark.configuration["spark.executor.instances"] = 1 

#run_config.environment.python.conda_dependencies = conda_dep
"""
script_run_config = ScriptRunConfig(source_directory = 'C:/Users/kesin/Downloads/pythonprojects/aml/ScheduleJob',
                                    script= 'Train.py',
                                    run_config = run_config) 


# Submit the run
from azureml.core import Experiment 
exp = Experiment(workspace=ws, name="Local-IRIS-V1") 
run = exp.submit(config=script_run_config) 
print(run.get_portal_url())
run.wait_for_completion()
"""
exp = Experiment(workspace=ws, name="Local-IRIS-V1") 
step_1 = PythonScriptStep(source_directory = 'C:/Users/kesin/Downloads/pythonprojects/aml/ScheduleJob',
                          script_name='Train.py',
                          compute_target=compute_name,
                          runconfig = run_config,
                          allow_reuse=False)

pipeline = Pipeline(workspace=ws, steps=[step_1])
pipeline_run = pipeline.submit("Local-IRIS-V1", regenerate_outputs=True)
