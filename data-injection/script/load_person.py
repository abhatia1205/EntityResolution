import pandas as pd
import pymysql
from credentials import engine

#person
person_path = '../input/people/'
actor_2018 = person_path + '100 Most In-Demand Actors Working 2018.csv'
people_hist = person_path + '12000 Miscellaneuos People from History.csv'
congress = person_path + 'Senate and House Members.csv'
athletes_2018 = person_path + 'Top 100 Athletes 2018.csv'
spo_mus_2018 = person_path + 'Top 100 Spotify Musicians 2018.csv'
spo_mus_2019 = person_path + 'Top 200 Spotify Musicians 2019.csv'
stars_2017 = person_path + 'Top 100 Stars of 2017.csv'
stars_2018 = person_path + 'Top 100 Stars of 2018.csv'
pop_celeb_1900_1 = person_path + 'Top 2000 most popular celebrities since 1900.csv'
pop_celeb_1900_2 = person_path + 'Top 6000 most popular celebrities since 1900.csv'
twitter_acc = person_path + 'Top-1000-Celebrity-Twitter-Accounts.csv'

#dataframe
person_header = ['id', 'fname', 'lname', 'original_name', 'type', 'subtype', 'detail', 'industry', 'domain', 'nickname', 'country', 'gender']

person_df = pd.DataFrame(columns=person_header)

#person transform
#actor 2018
actor_2018_df = pd.read_csv(actor_2018)
actor_2018_df['fname'] = actor_2018_df['Name'].str.split(' ').str[0]
actor_2018_df['lname'] = actor_2018_df['Name'].str.split(' ').str[-1]
actor_2018_df = actor_2018_df.rename(columns={'Name': 'original_name', 'Known For': 'detail'})
actor_2018_df['original_name'] = actor_2018_df['original_name'].str.lower()
actor_2018_df['type'] = 'actor'
actor_2018_df['subtype'] = 'show/movie'
actor_2018_df['industry'] = 'entertainment'
actor_2018_df['domain'] = 'show/movie'
print(actor_2018_df.head())

person_df = person_df.merge(actor_2018_df, how='outer')
person_df = person_df[person_header]
print(person_df.tail())

#people_hist
#has bad data
people_hist_df = pd.read_csv(people_hist)
people_hist_df = people_hist_df[pd.isnull(people_hist_df['bad_data'])]
people_hist_df = people_hist_df[['name', 'countryName', 'gender', 'occupation', 'industry', 'domain']]
people_hist_df = people_hist_df.rename(columns={'name': 'original_name', 'countryName': 'country', 'occupation' : 'type'})
people_hist_df['original_name'] = people_hist_df['original_name'].str.lower()
people_hist_df['country'] = people_hist_df['country'].str.lower()
people_hist_df['type'] = people_hist_df['type'].str.lower()
people_hist_df['fname'] = people_hist_df['original_name'].str.split(' ').str[0]
people_hist_df['lname'] = people_hist_df['original_name'].str.split(' ').str[-1]

print(people_hist_df.head())

person_df = person_df.merge(people_hist_df, how='outer')
person_df = person_df[person_header]
print(person_df.tail())

#congress
congress_df = pd.read_csv(congress)
congress_df = congress_df[['full_name', 'nickname', 'gender', 'type', 'state', 'party']]
congress_df = congress_df.rename(columns={'full_name': 'original_name', 'party': 'detail', 'type' : 'subtype'})
congress_df['original_name'] = congress_df['original_name'].str.lower()
congress_df['fname'] = congress_df['original_name'].str.split(' ').str[0]
congress_df['lname'] = congress_df['original_name'].str.split(' ').str[-1]
congress_df.loc[congress_df.gender == 'M', 'gender'] = 'Male'
congress_df.loc[congress_df.gender == 'F', 'gender'] = 'Female'
congress_df['country'] = 'United States'
congress_df['type'] = 'politician'
congress_df['industry'] = 'government'
congress_df['domain'] = 'institution'
print(congress_df.head())

person_df = person_df.merge(congress_df, how='outer')
person_df = person_df[person_header]
print(person_df.tail())

#athlete 2018
athletes_2018_df = pd.read_csv(athletes_2018)
athletes_2018_df = athletes_2018_df[['Name', 'Sport', 'Country', 'Gender ']]
athletes_2018_df = athletes_2018_df.rename(columns={'Name': 'original_name', 'Sport': 'subtype', 'Country' : 'country', 'Gender ': 'gender'})
athletes_2018_df['original_name'] = athletes_2018_df['original_name'].str.lower()
athletes_2018_df['country'] = athletes_2018_df['country'].str.lower()
athletes_2018_df.loc[athletes_2018_df.country == ' u.s.', 'country'] = 'united states'
athletes_2018_df['fname'] = athletes_2018_df['original_name'].str.split(' ').str[0]
athletes_2018_df['lname'] = athletes_2018_df['original_name'].str.split(' ').str[-1]
athletes_2018_df['type'] = 'athlete'
athletes_2018_df.loc[athletes_2018_df.gender == 'M', 'gender'] = 'Male'
athletes_2018_df.loc[athletes_2018_df.gender == 'F', 'gender'] = 'Female'
athletes_2018_df['industry'] = 'entertainment'
athletes_2018_df['domain'] = 'sports'
print(athletes_2018_df.head())

person_df = person_df.merge(athletes_2018_df, how='outer')
person_df = person_df[person_header]
print(person_df.tail())

#spo_mus_2018

spo_mus_2018_df = pd.read_csv(spo_mus_2018)
spo_mus_2018_df = spo_mus_2018_df[['ARTIST']]
spo_mus_2018_df = spo_mus_2018_df.rename(columns={'ARTIST': 'original_name'})
spo_mus_2018_df['original_name'] = spo_mus_2018_df['original_name'].str.lower()
spo_mus_2018_df['type'] = 'musician'
spo_mus_2018_df['subtype'] = 'artist'
spo_mus_2018_df['industry'] = 'entertainment'
spo_mus_2018_df['domain'] = 'music'
print(spo_mus_2018_df.head())

person_df = person_df.merge(spo_mus_2018_df, how='outer')
person_df = person_df[person_header]
print(person_df.tail())

#spo_music_2019
spo_mus_2019_df = pd.read_csv(spo_mus_2019)
spo_mus_2019_df = spo_mus_2019_df[['Artist']]
spo_mus_2019_df = spo_mus_2019_df.rename(columns={'Artist': 'original_name'})
spo_mus_2019_df['original_name'] = spo_mus_2019_df['original_name'].str.lower()
spo_mus_2019_df['type'] = 'musician'
spo_mus_2019_df['subtype'] = 'artist'
spo_mus_2019_df['industry'] = 'entertainment'
spo_mus_2019_df['domain'] = 'music'
print(spo_mus_2019_df.head())

person_df = person_df.merge(spo_mus_2019_df, how='outer')
person_df = person_df[person_header]
print(person_df.tail())

#star_2017

stars_2017_df = pd.read_csv(stars_2017)
stars_2017_df = stars_2017_df[['Name', 'Known For']]
stars_2017_df = stars_2017_df.rename(columns={'Name': 'original_name', 'Known For': 'detail'})
stars_2017_df['original_name'] = stars_2017_df['original_name'].str.lower()
stars_2017_df['fname'] = stars_2017_df['original_name'].str.split(' ').str[0]
stars_2017_df['lname'] = stars_2017_df['original_name'].str.split(' ').str[-1]
stars_2017_df['type'] = 'actor'
stars_2017_df['subtype'] = 'show/movie'
stars_2017_df['industry'] = 'entertainment'
stars_2017_df['domain'] = 'show/movie'
print(stars_2017_df.head())

person_df = person_df.merge(stars_2017_df, how='outer')
person_df = person_df[person_header]
print(person_df.tail())

#stars_2018
stars_2018_df = pd.read_csv(stars_2018)
stars_2018_df = stars_2018_df[['Name', 'Known For']]
stars_2018_df = stars_2018_df.rename(columns={'Name': 'original_name', 'Known For': 'detail'})
stars_2018_df['original_name'] = stars_2018_df['original_name'].str.lower()
stars_2018_df['fname'] = stars_2018_df['original_name'].str.split(' ').str[0]
stars_2018_df['lname'] = stars_2018_df['original_name'].str.split(' ').str[-1]
stars_2018_df['type'] = 'actor'
stars_2018_df['subtype'] = 'show/movie'
stars_2018_df['industry'] = 'entertainment'
stars_2018_df['domain'] = 'show/movie'
print(stars_2018_df.head())

person_df = person_df.merge(stars_2018_df, how='outer')
person_df = person_df[person_header]
print(person_df.tail())

#pop_celeb_1900_1
pop_celeb_1900_1_df = pd.read_csv(pop_celeb_1900_1)
pop_celeb_1900_1_df = pop_celeb_1900_1_df[['name', 'countryName', 'gender', 'occupation', 'industry', 'domain']]
pop_celeb_1900_1_df = pop_celeb_1900_1_df.rename(columns={'name': 'original_name', 'countryName': 'country', 'occupation' : 'type'})
pop_celeb_1900_1_df['original_name'] = pop_celeb_1900_1_df['original_name'].str.lower()
pop_celeb_1900_1_df['country'] = pop_celeb_1900_1_df['country'].str.lower()
pop_celeb_1900_1_df['type'] = pop_celeb_1900_1_df['type'].str.lower()
pop_celeb_1900_1_df['fname'] = pop_celeb_1900_1_df['original_name'].str.split(' ').str[0]
pop_celeb_1900_1_df['lname'] = pop_celeb_1900_1_df['original_name'].str.split(' ').str[-1]
print(pop_celeb_1900_1_df.head())

person_df = person_df.merge(pop_celeb_1900_1_df, how='outer')
person_df = person_df[person_header]
print(person_df.tail())

#pop_celeb_1900_2
pop_celeb_1900_2_df = pd.read_csv(pop_celeb_1900_2, encoding='latin-1')
pop_celeb_1900_2_df = pop_celeb_1900_2_df[['name', 'countryName', 'gender', 'occupation', 'industry', 'domain']]
pop_celeb_1900_2_df = pop_celeb_1900_2_df.rename(columns={'name': 'original_name', 'countryName': 'country', 'occupation' : 'type'})
pop_celeb_1900_2_df['original_name'] = pop_celeb_1900_2_df['original_name'].str.lower()
pop_celeb_1900_2_df['type'] = pop_celeb_1900_2_df['type'].str.lower()
pop_celeb_1900_2_df['country'] = pop_celeb_1900_2_df['country'].str.lower()
pop_celeb_1900_2_df['fname'] = pop_celeb_1900_2_df['original_name'].str.split(' ').str[0]
pop_celeb_1900_2_df['lname'] = pop_celeb_1900_2_df['original_name'].str.split(' ').str[-1]
print(pop_celeb_1900_2_df.head())

person_df = person_df.merge(pop_celeb_1900_2_df, how='outer')
person_df = person_df[person_header]
print(person_df.tail())

#delete dupe
person_df = person_df.drop_duplicates(['original_name', 'type', 'country'], keep = 'first')
person_df = person_df.drop_duplicates(['fname','lname', 'type', 'country'], keep = 'first')
person_df = person_df.reset_index()
person_df = person_df[person_header]

print(person_df.tail())
print(person_df.head())
print(person_df.shape[0])
#twitter
twitter_acc_df = pd.read_csv(twitter_acc)
twitter_acc_df = twitter_acc_df[['twitter', 'domain', 'name']]
twitter_acc_df = twitter_acc_df.rename(columns={'name': 'original_name', 'domain': 'website'})
twitter_acc_df['original_name'] = twitter_acc_df['original_name'].str.lower()
twitter_acc_df = twitter_acc_df.drop_duplicates(['original_name'], keep = 'first')
twitter_acc_df = twitter_acc_df.reset_index()
twitter_acc_df = twitter_acc_df[['twitter', 'website', 'original_name']]
person_df = pd.merge(person_df, twitter_acc_df, on='original_name', how='left')
person_df['id'] = person_df.index + 1
print(person_df.tail())
print(person_df.head())
print(person_df.shape[0])
#upload to db


person_df.to_sql(name='important_person', con=engine, if_exists = 'replace', index=False)
engine.execute("""ALTER TABLE `quantum`.`important_person`
CHANGE COLUMN `id` `id` BIGINT(20) NOT NULL AUTO_INCREMENT ,
ADD PRIMARY KEY (`id`);""")
print('Complete')
