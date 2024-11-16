from ultralytics import YOLO
import sys
import io
from contextlib import redirect_stdout

class SilentPredictor:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        
    def predict(self, image_path, **kwargs):
        # Temporarily redirect stdout to suppress prints
        temp_stdout = io.StringIO()
        with redirect_stdout(temp_stdout):
            results = self.model.predict(
                source=image_path,
                verbose=False,  # This helps reduce some output but doesn't catch everything
                **kwargs
            )
        return results

# Usage example
def run_silent_inference(model_path, image_path):
    predictor = SilentPredictor(model_path)
    results = predictor.predict(image_path)
    return results

# Alternative approach using context manager
class SuppressOutput:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open('/dev/null', 'w')
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

# Usage example with context manager
def alternative_silent_inference(model_path, image_path):
    model = YOLO(model_path)
    with SuppressOutput():
        results = model.predict(source=image_path, verbose=False)
    return results