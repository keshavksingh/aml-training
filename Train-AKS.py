import mlflow
from azure.ai.ml import MLClient
from azure.identity import ClientSecretCredential


#Enter details of your AzureML workspace
subscription_id = ''
resource_group = ''
workspace_name = ''

tenant_id=""
client_id=""
client_secret=""

credentials = ClientSecretCredential(
                        tenant_id=tenant_id,
                        client_id=client_id,
                        client_secret=client_secret
                    )

ml_client = MLClient(credential=credentials,
                        subscription_id=subscription_id, 
                        resource_group_name=resource_group,
                        workspace_name=workspace_name)
mlflow_tracking_uri = ml_client.workspaces.get(ml_client.workspace_name).mlflow_tracking_uri
mlflow_uri = mlflow.set_tracking_uri(mlflow_tracking_uri)
print(mlflow_tracking_uri)


import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn import datasets
import numpy as np

ExperimentName="AMLWS-AKS-COMPUTE-IRIS-V1"
model_name = "iris-random-forest-model"
mlflow.set_tracking_uri(mlflow_tracking_uri)
#mlflow.set_experiment("Synapse IRIS V1")
mlflow.set_experiment(ExperimentName)

iris = datasets.load_iris()
x = iris.data[:,:]
y = iris.target

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=7)

with mlflow.start_run(run_name="IRIS EXPERIMENT RUN 1") as run:
    # add parameters for tuning
    num_estimators = 100
    mlflow.log_param("num_estimators",num_estimators)

    # train the model
    rf = RandomForestRegressor(n_estimators=num_estimators)
    fit_model = rf.fit(X_train, y_train)
    predictions = rf.predict(X_test)

    # save the model artifact for deployment
    # this will save the model to the Azure Blobstore Configured On the MLFlow server
    mlflow.sklearn.log_model(rf, model_name)

    # log model performance 
    mse = mean_squared_error(y_test, predictions)
    mlflow.log_metric("MSE", mse)
    print("mse: %f" % mse)
    
    # log model performance
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    print("rmse:",rmse)
    mlflow.log_metric("RMSE", rmse)

    run_id = run.info.run_uuid
    experiment_id = run.info.experiment_id
    mlflow.end_run()
    print(mlflow.get_artifact_uri())
    print("runID: %s" % run_id)