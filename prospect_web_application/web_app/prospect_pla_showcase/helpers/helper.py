import os
import pandas as pd


def create_dir(dir_path):
	if not os.path.exists(dir_path):
		os.mkdir(dir_path)


def get_column_header_list(file_path):
	df = pd.read_csv(file_path, sep='\t')
	return df.columns.tolist()