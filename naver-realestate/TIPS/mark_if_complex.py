import pandas as pd
import re

# Define the classification function based on the enhanced rules


def final_housing_type_classification(address):
    patterns = [
        r'아파트|오피스텔|단지|타운|자이|래미안|푸르지오|하이츠|캐슬|빌라|e편한|팰리스|해모로|휴먼시|힐스테이트|아이파크',
        r'\s*\b\d+동\s*[-]{0,1}\s*\d+호',
        r'\([^)]*,[^)]*\)[\w-]+\d+-[\w-]+\d+',
        r'\([^)]*,[^)]*\)\s*[\dA-Za-z]+',
        r'\([^)]*,[^)]*\)[\dA-Za-z]+호',
        r'\([^)]*동[^)]*\)[\dA-Za-z]+호',
        r'\)\s*[^\(]*[\dA-Za-z]+[호]*$',
        r'\b[\dA-Za-z]+동\s*[\dA-Za-z]+호\b',  # Building directly connected with "동" and "호"
        r'\b\w+빌\b',          # Ends with '빌'
        r'[^\(]+[\dA-Za-z]+\s*호',        # '호' after text outside parentheses
        r'\b[\dA-Za-z]+-[\dA-Za-z]+호\b',       # Adding pattern to capture "104-303" format
        r'[^길]\b[\dA-Za-z]+\s*-\s*[\dA-Za-z]+\b\s*'       # Adding pattern to capture "104-303" format
    ]
    return '공동' if any(re.search(pattern, address) for pattern in patterns) else '일반'


# Load the addresses from a TSV file
addresses_df = pd.read_csv('addresses.tsv', sep='\t')

# Apply the classification function to each address
addresses_df['주택유형'] = addresses_df['회원주소'].apply(final_housing_type_classification)

# Save the results to a new TSV file
addresses_df.to_csv('marked_addresses.tsv', sep='\t', index=False)
