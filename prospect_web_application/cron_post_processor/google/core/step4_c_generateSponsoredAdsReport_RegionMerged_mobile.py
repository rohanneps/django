import pandas as pd
import os
from GlobalVariables import (
							BATCH_OUTPUT_DIR_MOBILE,
							S3_REGION_LIST
							)


def main(client):
	output_df = pd.DataFrame()
	output_dir = BATCH_OUTPUT_DIR_MOBILE.format(client)
	
	for region in S3_REGION_LIST:
		print(region)
		region_related_path = os.path.join(output_dir, region, 'SponsoredAds_Combined{}.tsv'.format(region))
		if os.path.exists(region_related_path):
			df = pd.read_csv(region_related_path, sep='\t')
			output_df = output_df.append(df)

	if len(output_df)>0:
		output_df.to_csv(os.path.join(output_dir,'SponsoredAds_Combined_allregion.tsv'), index=False,sep='\t')
	else:
		print('No sponsored Mobile for all regions.')
		
if __name__ == '__main__':
	main()