from pathlib import Path
import joblib

ROOT_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = ROOT_DIR / "train_test_data" / "models" / "asl_model.pkl"

model = joblib.load(MODEL_PATH)

def predict(data):
    return model.predict(data)[0]