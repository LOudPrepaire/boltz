# AlphaFold_B API

## Running the Docker Container
To start the AlphaFold_B API, first pull the necessary image and run the Docker container using the following command:

```bash
docker run --gpus all --shm-size=16G -d --user root -v ./output/:/workspace/output/ -p 8002:8000 alphafold_b:latest
```

### Notes:
- The model requires **at least 10 minutes** to be fully loaded before it is ready to receive requests.
- If you want to store outputs in a specific location, modify the volume mount in the command (`-v ./output/:/workspace/output/`) to your desired directory.

## API Description
The API is built using **FastAPI** and runs on port `8002`. It provides a sequence folding service using the **Boltz predictor**.

### **Endpoint: `/fold/`**
- **Method**: `POST`
- **Request Body**: JSON with a list of sequences
- **Response**:
  - `success`: `true` if the request is processed successfully, `false` otherwise.
  - `output_path`: The location of the generated `.pdb` file.
  - `stdout`: Standard output from the folding process.
  - `stderr`: Error output if any issues occur.

#### Example Request:
```json
{
    "sequences": ["TQVCTGTDMKLRLPASPETHLDMLRHLYQGCQVVQGNLELTYLP","TNASLSFLQDIQEVQGYVLIAHNQVRQVPLQRLRIVRG"]
}
```

#### Example Response:
```json
{
    "success": true,
    "output_path": "./output/boltz_results_seq_model_0.pdb",
    "stdout": "...",
    "stderr": ""
}
```

### Example Python Code for Sending a Request
```python
import requests

url = "http://localhost:8002/fold/"
data = {
    "sequences": ["TQVCTGTDMKLRLPASPETHLDMLRHLYQGCQVVQGNLELTYLP","TNASLSFLQDIQEVQGYVLIAHNQVRQVPLQRLRIVRG"],
}

response = requests.post(url, json=data)

print("Response:", response.json())
```

#### Example Output
```json
{
    "success": true,
    "output_path": "./output/boltz_results_seq_f0e51/predictions/seq_f0e51/seq_f0e51_model_0.pdb",
    "stdout": "Checking input data.\nRunning predictions for 1 structure\nProcessing input data.\nFound explicit empty MSA for some proteins, will run these in single sequence mode. Keep in mind that the model predictions will be suboptimal without an MSA.\nFound explicit empty MSA for some proteins, will run these in single sequence mode. Keep in mind that the model predictions will be suboptimal without an MSA.\n\nPredicting: |          | 0/? [00:00<?, ?it/s]\nPredicting:   0%|          | 0/1 [00:00<?, ?it/s]\nPredicting DataLoader 0:   0%|          | 0/1 [00:00<?, ?it/s]\nPredicting DataLoader 0: 100%|██████████| 1/1 [00:12<00:00,  0.08it/s]Number of failed examples: 0\n\nPredicting DataLoader 0: 100%|██████████| 1/1 [00:12<00:00,  0.08it/s]\n",
}
```

## Files Overview
### **1. `app.py`**
- Initializes the FastAPI application.
- Loads the model at startup (`load_model()` function).
- Defines the `/fold/` endpoint to process input sequences and generate predictions using the `boltz predict` command.

### **2. `initializer.py`**
- Converts input sequences into **FASTA** format.
- Assigns unique job names and organizes output files.
- Ensures that job directories exist before processing requests.

### **3. `entrypoint.sh`**
- Starts the FastAPI server using `uvicorn` on port `8000`.

### **4. `test.py`**
- A simple script to send test requests to the API.
- Uses the `requests` library to POST sequences to `http://localhost:8002/fold/` and print the response.


## Running Tests
After waiting for the model to load (~10 minutes), you can test the API using:

```bash
python test.py
```
This script will send a sample request and display the response.

