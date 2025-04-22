import xgboost as xgb

# Check if GPU is available and XGBoost is compiled with GPU support


def check_xgboost_gpu():
    params = {'tree_method': 'gpu_hist', 'gpu_id': 0}
    dmatrix = xgb.DMatrix(data=[[1, 2], [3, 4]], label=[1, 2])
    try:
        # Perform a simple training to check for GPU availability
        xgb.train(params, dmatrix, num_boost_round=1)
        print("XGBoost GPU is available and the model is compiled with GPU support.")
    except xgb.core.XGBoostError as e:
        print("XGBoost GPU is not available or not compiled with GPU support.")
        print(e)


check_xgboost_gpu()
