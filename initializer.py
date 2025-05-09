import os
import re
import random
import hashlib
import random
import requests
from string import ascii_uppercase

# Function to add a hash to the jobname
def add_hash(x, y):
    return x + "_" + hashlib.sha1((y+str(random.random())).encode()).hexdigest()[:5]

# Check if a directory with jobname exists
def check(folder):
    return not os.path.exists(folder)

def seq_to_fasta(query_sequence='QVQLVQSGAEVKKPGSSVKVSCKASGGTFSSYAISWVRQAPGQGLEWMGGIIPIFGTANYAQKFQGRVTITADESTSTAYMELSSLRSEDTAVYYCARGGPGNFDYWGQGTLVTVSS:DIQMTQSPSSLSASVGDRVTITCRASQSISSYLNWYQQKPGKAPKLLIYAASSLQSGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQQSYSTPPVTFGQGTKVEIK'):
    jobname = 'seq' 
    
    # Clean up the query sequence and jobname
    query_sequence = "".join(query_sequence.split())

    basejobname = "".join(jobname.split())
    basejobname = re.sub(r'\W+', '', basejobname)
    jobname = add_hash(basejobname, query_sequence)

    if not check(jobname):
        n = 0
        while not check(f"{jobname}_{n}"):
            n += 1
        jobname = f"{jobname}_{n}"

    # Make directory to save results
    os.makedirs(jobname, exist_ok=True)


    # Split sequences on chain breaks
    protein_sequences = query_sequence.strip().split(':') if query_sequence.strip() else []

    # Initialize chain labels starting from 'A'
    chain_labels = iter(ascii_uppercase)

    fasta_entries = []
    csv_entries = []
    chain_label_to_seq_id = {}
    seq_to_seq_id = {}
    seq_id_counter = 0  # Counter for unique sequences

    # Process protein sequences
    for seq in protein_sequences:
        seq = seq.strip()
        if not seq:
            continue  # Skip empty sequences
        chain_label = next(chain_labels)
        # Check if sequence has been seen before
        if seq in seq_to_seq_id:
            seq_id = seq_to_seq_id[seq]
        else:
            seq_id = f"{jobname}_{seq_id_counter}"
            seq_to_seq_id[seq] = seq_id
            seq_id_counter += 1
            # For CSV file (for ColabFold), add only unique sequences
            csv_entries.append((seq_id, seq))
        chain_label_to_seq_id[chain_label] = seq_id
        # For FASTA file
        msa_path = "empty"
        header = f">{chain_label}|protein|{msa_path}"
        sequence = seq
        fasta_entries.append((header, sequence))

    # Write the CSV file for ColabFold
    queries_path = os.path.join(jobname, f"{jobname}.csv")
    with open(queries_path, "w") as text_file:
        text_file.write("id,sequence\n")
        for seq_id, seq in csv_entries:
            text_file.write(f"{seq_id},{seq}\n")

    # Write the FASTA file
    queries_fasta = os.path.join(jobname, f"{jobname}.fasta")
    with open(queries_fasta, 'w') as f:
        for header, sequence in fasta_entries:
            f.write(f"{header}\n{sequence}\n")
    
    if os.path.exists(queries_fasta):    
        return {
            'jobname':jobname,
            'fasta_path':queries_fasta,
            }
    else:
        return None


if __name__ == "__main__":
    print(seq_to_fasta())