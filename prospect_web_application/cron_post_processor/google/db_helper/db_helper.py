import pandas as pd
from GlobalVariables import (
								SHOWCASE_TABLE_NAME,
								SPONSORED_TABLE_NAME,
								MANDATORY_COLUMN_HEADERS,
								SHOWCASE_COLUMNS
							)

def insert_computed_file_to_db(engine, src_file_path, client, source):

	df = pd.read_csv(src_file_path.format(client), sep='\t')
	# for PLA
	sponsored_df = df[df['PLA/Showcase']=='PLA']
	del sponsored_df['PLA/Showcase']
	showcase_df = df[df['PLA/Showcase']=='Showcase']

	total_sponsored_records = len(sponsored_df)
	total_showcase_records = len(showcase_df)

	showcase_df = showcase_df[['Prospect Name'] + MANDATORY_COLUMN_HEADERS + ['Search From'] + SHOWCASE_COLUMNS]

	# if SERVER:
	print('For client {}: Inserting into the database.'.format(client))

	sponsored_df.to_sql(name=SPONSORED_TABLE_NAME, con=engine, if_exists='append', index=False)
	showcase_df.to_sql(name=SHOWCASE_TABLE_NAME, con=engine, if_exists='append', index=False)

	return total_sponsored_records, total_showcase_records