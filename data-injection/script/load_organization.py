import pandas as pd
import sys
from credentials import engine
#organization
org_path = '../input/organization/'
constituents = org_path + 'constituents_csv.csv'
five_hundred_companies = org_path + 'S and P 500 Companies.csv'
federal_government = org_path + 'federal_government_acronym.csv'
#dataframe
organization_header = ['id', 'name','abbrv', 'type']

organization_df = pd.DataFrame(columns=organization_header)

five_hundred_companies_df = pd.read_csv(five_hundred_companies)
five_hundred_companies_df = five_hundred_companies_df[['Name', 'Symbol', 'Sector']]
five_hundred_companies_df = five_hundred_companies_df.rename(columns={'Name' : 'name', 'Symbol' : 'abbrv', 'Sector' : 'type'})
print(five_hundred_companies_df.head())


organization_df = organization_df.merge(five_hundred_companies_df, how='outer')
organization_df = organization_df[organization_header]
print(organization_df.tail())

constituents_df = pd.read_csv(constituents)
constituents_df = constituents_df[['Name', 'Symbol', 'Sector']]
constituents_df = constituents_df.rename(columns={'Name' : 'name', 'Symbol' : 'abbrv', 'Sector' : 'type'})
print(constituents_df.head())

organization_df = organization_df.merge(constituents_df, how='outer')
organization_df = organization_df[organization_header]
print(organization_df.tail())

federal_government_df = pd.read_csv(federal_government)
federal_government_df = federal_government_df[['accr', 'full_name']]
federal_government_df = federal_government_df.rename(columns={'full_name' : 'name', 'accr' : 'abbrv'})
federal_government_df['type'] = 'Government'
print(federal_government_df.head())

organization_df = organization_df.merge(federal_government_df, how='outer')
organization_df = organization_df[organization_header]
print(organization_df.tail())

organization_df = organization_df.drop_duplicates(['abbrv'], keep = 'first')
organization_df = organization_df.reset_index()
organization_df = organization_df[organization_header]
organization_df['id'] = organization_df.index + 1
print(organization_df.tail())
print(organization_df.shape[0])

organization_df.to_sql(name='important_organization', con=engine, if_exists = 'replace', index=False)
engine.execute("""ALTER TABLE `quantum`.`important_organization`
CHANGE COLUMN `id` `id` BIGINT(20) NOT NULL AUTO_INCREMENT ,
ADD PRIMARY KEY (`id`);""")
print('Complete')
