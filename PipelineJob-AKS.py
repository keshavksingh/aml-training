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
compute_name = "aks-aml"
try:
    compute_instance = ComputeInstance(workspace=ws, name=compute_name)
    print(f"Found existing compute instance: {compute_name}")
except ComputeTargetException:
    print(f"Not Found compute instance: {compute_name}")


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

run_config = RunConfiguration(conda_dependencies=conda_dep)
run_config.target = compute_name

exp = Experiment(workspace=ws, name="AMLWS-AKS-COMPUTE-IRIS-V1") 
step_1 = PythonScriptStep(source_directory = 'C:/Users/home/Downloads/pythonprojects/aml/ScheduleJob',
                          script_name='Train-AKS.py',
                          compute_target=compute_name,
                          runconfig = run_config,
                          allow_reuse=False)

pipeline = Pipeline(workspace=ws, steps=[step_1])
pipeline_run = pipeline.submit("AMLWS-AKS-COMPUTE-IRIS-V1", regenerate_outputs=True)
