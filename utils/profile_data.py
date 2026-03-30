import os
import pandas as pd
import yaml

def profile_input_files(input_dir="data/input"):
    print(f"{'Archivo':<40} | {'Columnas Detectadas'}")
    print("-" * 100)
    
    for filename in os.listdir(input_dir):
        if filename.endswith(('.csv', '.xlsx')):
            file_path = os.path.join(input_dir, filename)
            try:
                if filename.endswith('.csv'):
                    df = pd.read_csv(file_path, nrows=1)
                else:
                    df = pd.read_excel(file_path, nrows=1)
                
                cols = df.columns.tolist()
                print(f"{filename:<40} | {cols}")
            except Exception as e:
                print(f"{filename:<40} | ERROR: {str(e)}")

if __name__ == "__main__":
    profile_input_files()
