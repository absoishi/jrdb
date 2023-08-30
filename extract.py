# python script_name.py INPUT_DIRECTORY OUTPUT_DIRECTORY
# ex) ❯ python bin/extract.py data/jrdb/source/OV data/jrdb/extract/OV
import os
import zipfile
import argparse
import subprocess
import glob

def unzip_files_with_status(input_directory, output_directory):
    """指定ディレクトリ内の圧縮ファイルを別ディレクトリに解凍する関数（処理状況を表示）"""
    
    for ext in ["zip", "lzh"]:
        files = glob.glob(os.path.join(input_directory, f"*.{ext}"))
        
        for file_path in files:
            print(f"Starting to unzip: {file_path}")
            
            if ext == "zip":
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(output_directory)
            elif ext == "lzh":
                subprocess.run(["lha", "xw=" + output_directory, file_path])
            
            print(f"Finished unzipping: {file_path}")

def main():
    parser = argparse.ArgumentParser(description='Unzip files from one directory to another with status messages.')
    parser.add_argument('input_directory', help='Directory containing the compressed files.')
    parser.add_argument('output_directory', help='Directory to extract the files to.')
    args = parser.parse_args()

    unzip_files_with_status(args.input_directory, args.output_directory)

if __name__ == "__main__":
    main()




