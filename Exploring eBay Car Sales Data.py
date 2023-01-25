#!/usr/bin/env python
# coding: utf-8

# ## Exploring eBay Car Sales Data

# Modified dataset of used cars from eBay Kleinanzeigen, a classifieds section of the German eBay website.

# The data dictionary provided with data is as follows:
# 
# dateCrawled - When this ad was first crawled. All field-values are taken from this date.
# 
# name - Name of the car.
# 
# seller - Whether the seller is private or a dealer.
# 
# offerType - The type of listing
# 
# price - The price on the ad to sell the car.
# 
# abtest - Whether the listing is included in an A/B test.
# 
# vehicleType - The vehicle Type.
# 
# yearOfRegistration - The year in which the car was first registered.
# 
# gearbox - The transmission type.
# 
# powerPS - The power of the car in PS.
# 
# model - The car model name.
# 
# odometer - How many kilometers the car has driven.
# 
# monthOfRegistration - The month in which the car was first registered.
# 
# fuelType - What type of fuel the car uses.
# 
# brand - The brand of the car.
# 
# notRepairedDamage - If the car has a damage which is not yet repaired.
# 
# dateCreated - The date on which the eBay listing was created.
# 
# nrOfPictures - The number of pictures in the ad.
# 
# postalCode - The postal code for the location of the vehicle.
# 
# lastSeenOnline - When the crawler saw this ad last online.

# In[45]:


# importing libraries
import pandas as pd
import numpy as np


# In[46]:


#reading csv file
df = pd.read_csv(r'C:\Users\ABDULLAH\Desktop\autos.csv', encoding='Latin-1')
df.info()
df.head()


# Our dataset contains 20 columns, most of which are stored as strings. There are a few columns with null values. There are some columns that contain dates stored as strings.
# 
# Next: Cleaning the column names to make the data easier to work with.

# In[47]:


# create a list of columns
df.columns


# We'll make a few changes here:
# 
# Change the columns from camelcase to snakecase. Change a few wordings to more accurately describe the columns.

# In[51]:


#Renaming the columns
df.columns = ['date_crawled', 'name', 'seller',
              'offer_type', 'price', 'ab_test',
              'vehicle_type', 'registration_year',
              'gear_box', 'power_ps','model', 'odometer',
              'registration_month', 'fuel_type', 'brand',
              'unrepaired_damage', 'ad_created', 'num_photos',
              'postal_code', 'last_seen']


# In[52]:


# overview of data
df.describe(include='all')


# Num_photos column contains all null values. Needs to be dropped. 'Offer_type' and 'seller' columns only contain 2 unique values. Will drop them, too.

# In[53]:


# dropping unrequired columns
df = df.drop(['seller', 'offer_type', 'num_photos'], axis =1 )


# There are two columns, price and auto, which are numeric values with extra characters being stored as text. We'll clean and convert these.

# In[54]:


# removing '$' & ',' sign from price column, replacing them with space, converting the data type to integer
df['price'] = df['price'].str.replace('$', '').str.replace(',', '').astype(int)


# In[55]:


# reving 'km' & ',' sign, replacing them with space and converting to integer type
df['odometer'] = df['odometer'].str.replace('km', '').str.replace(',', '').astype(int)


# In[56]:


# renaming the column for clarity
df.rename(columns = {'odometer':'odometer_km'}, inplace = True)


# In[57]:


# summary of price column
df['price'].describe()


# In[61]:


# counting unique values for lower prices
df['price'].value_counts().sort_index(ascending = True)


# There are 1,421 cars listed with $0 price - given that this is only 2 % of the of the cars, we might consider removing these rows.

# In[60]:


# # counting unique values in descending order for higher prices
df['price'].value_counts().sort_index(ascending = False).head(20)


# Only 14 cars have a price above $350 000. Need to drop these rows.

# In[62]:


# adjusting the df to have prices in the specified range
df = df[df['price'].between(1,351000)]


# ## Exploring the date columns

# In[63]:


# exploring date columns
df[['date_crawled', 'ad_created', 'last_seen']][0:5]


# In[64]:


# converting the column to string, extracting only date and not time, with relative frequency 
df['date_crawled'].str[:10].value_counts(normalize = True, dropna = False).sort_index()


# Looks like the site was crawled daily over roughly a one month period in March and April 2016. The distribution of listings crawled on each day is roughly uniform.

# In[65]:


# # converting the column to string, extracting only date and not time, with relative frequency 
df['ad_created'].str[:10].value_counts(normalize = True, dropna = False).sort_index()


# There is a large variety of ad created dates.

# In[67]:


# # converting the column to string, extracting only date and not time, with relative frequency 
df["last_seen"].str[:10].value_counts(normalize=True, dropna=False).sort_index()


# In[68]:


# summary of the column
df['registration_year'].describe()


# The year that the car was first registered will likely indicate the age of the car. Looking at this column, we note some odd values. The minimum value is 1000, long before cars were invented and the maximum is 9999, many years into the future.

# ## Dealing with incorrect registration year data

# Because a car can't be first registered before the listing was seen, any vehicle with a registration year above 2016 is definitely inaccurate. Determining the earliest valid year is more difficult. Realistically, it could be somewhere in the first few decades of the 1900s.
# One option is to remove the listings with these values. Let's determine what percentage of our data has invalid values in this column:

# In[28]:


(~df["registration_year"].between(1900,2016)).sum() / df.shape[0]


# Given that this is less than 4% of our data, we will remove these rows.

# In[70]:


# selecting rows where registration_year is between 1900 and 2016
df = df[df["registration_year"].between(1900,2016)]
df["registration_year"].value_counts(normalize=True)


# It appears that most of the vehicles were first registered in the past 20 years. Intuitively also.

# ## Exploring Price by Band

# In[71]:


# unique values in the column with relative frequencies
df["brand"].value_counts(normalize=True)


# There are lots of brands that don't have a significant percentage of listings, so we will limit our analysis to brands representing more than 5% of total listings.

# In[72]:


# selecting brand with relative frequency higher than 0.05
brand_count = df['brand'].value_counts(normalize = True)
common_brands = brand_count[brand_count > 0.05].index
common_brands


# In[73]:


# brands and their mean price
brand_mean_price = {} # empty dictionary
for brand in common_brands:
    brand_only = df[df['brand'] == brand]
    mean_price  = brand_only['price'].mean()
    brand_mean_price[brand] = int(mean_price)

brand_mean_price


# Of the top 5 brands, there is a distinct price gap:
# 
# Audi, BMW and Mercedes Benz are more expensive
# 
# Ford and Opel are less expensive
# 
# Volkswagen is in between.

# In[77]:


# converting dictionary to pandas series
brand_mean_price_series = pd.Series(brand_mean_price)
brand_mean_price_series


# ## Exploring Mileage

# In[80]:


# working for mileage of brands
brand_mean_mileage = {} # empty dictionary

for brand in common_brands:
    brand_only = df[df["brand"] == brand]
    mean_mileage = brand_only["odometer_km"].mean()
    brand_mean_mileage[brand] = int(mean_mileage)


# In[83]:


# converting dictionary to pandas series
brand_mean_mileage_series = pd.Series(brand_mean_mileage)
brand_mean_mileage_series


# In[91]:


# sorting te series
brand_mean_mileage_series = pd.Series(brand_mean_mileage).sort_values(ascending=False)
brand_mean_mileage_series


# In[92]:


# sorting the series
brand_mean_prices_series = pd.Series(brand_mean_price).sort_values(ascending=False)
brand_mean_prices_series


# In[96]:


# converting the series into dataframe
brand_info = pd.DataFrame(brand_mean_mileage_series,columns=['mean_mileage'])
brand_info


# In[97]:


# adding series to the dataframe
brand_info["mean_price"] = brand_mean_prices_series
brand_info


# The range of car mileages does not vary as much as the prices do by brand. There is a slight trend to the more expensive vehicles having higher mileage, with the less expensive vehicles having lower mileage

# In[ ]:




