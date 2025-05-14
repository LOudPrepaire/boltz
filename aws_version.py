import boto3
import subprocess
import os
import sys
import initializer
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
TMP_INPUT = "/tmp/input.json"
OUTPUT_DIR = "./output/"

def download_from_s3(local_file, bucket, object_key):
    s3 = boto3.client('s3')
    logging.info(f"Downloading s3://{bucket}/{object_key} to {local_file}")
    s3.download_file(bucket, object_key, local_file)

def upload_to_s3(local_file, bucket, object_key):
    s3 = boto3.client('s3')
    logging.info(f"Uploading {local_file} to s3://{bucket}/{object_key}")
    s3.upload_file(local_file, bucket, object_key)

def run_fold(fasta_path: str) -> subprocess.CompletedProcess:
    """Runs Boltz prediction and returns the result object."""
    cmd = [
        "boltz", "predict", fasta_path,
        "--use_msa_server", "--output_format", "pdb",
        "--override", "--out_dir", OUTPUT_DIR
    ]
    logging.info(f"Running BoltzFold for {fasta_path}")
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def preload_model():
    """Runs model folding once to warm up the model container."""
    logging.info("Preloading model to warm up prediction engine...")
    init = initializer.seq_to_fasta()
    fasta_path = init.get('fasta_path')

    if not fasta_path:
        logging.error("FASTA path missing during preload.")
        return

    try:
        result = run_fold(fasta_path)
        if result.returncode != 0:
            logging.warning(f"Model warm-up failed:\n{result.stderr}")
        else:
            logging.info("Model warm-up successful.")
    except Exception as e:
        logging.exception(f"Unexpected error during model preload: {e}")

def main(s3_input_key, s3_output_key, s3_bucket):
    if not s3_input_key or not s3_bucket or not s3_output_key:
        raise ValueError("Environment variables INPUT and BUCKET and OUTPUT must be set. Ensure they are correctly configured.")

    download_from_s3(TMP_INPUT, s3_bucket, s3_input_key)

    if not os.path.exists(TMP_INPUT):
        logging.error(f"❌ Input file not found: {TMP_INPUT}")
        sys.exit(1)

    try:
        with open(TMP_INPUT, "r") as f:
            data = json.load(f)

        sequences = ":".join(data.get("sequences", []))
        if not sequences:
            logging.error("No sequences found in input file.")
            sys.exit(1)

        logging.info(f" Using sequences: {sequences}")
        init = initializer.seq_to_fasta(sequences)
        jobname = init.get("jobname")
        fasta_path = init.get("fasta_path")

        result = run_fold(fasta_path)
        if result.returncode != 0:
            logging.error(f"❌ Fold failed with exit code {result.returncode}")
            logging.error(f"stdout:\n{result.stdout}")
            logging.error(f"stderr:\n{result.stderr}")
            sys.exit(1)

        logging.info(f"Fold completed:\n{result.stdout}")
        output_pdb = os.path.join(OUTPUT_DIR, f"boltz_results_{jobname}/predictions/{jobname}/{jobname}_model_0.pdb")
        upload_to_s3(output_pdb, s3_bucket, s3_output_key)

    except Exception as e:
        logging.exception(f"❌ Unexpected error during main execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python aws_version.py <s3_input_path> <s3_output_path>  <BUCKET>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])
