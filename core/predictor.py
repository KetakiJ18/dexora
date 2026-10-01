import joblib

model = joblib.load("train_test_data\\models\\asl_model.pkl")

def predict(data):
    return model.predict(data)[0]