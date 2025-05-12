##PSEUDOCODE - ESTABLISH A FRAMEWORK FOR +- SCORES FOR COOKIES 
## COMPARE EACH COOKIE TO THAT SCORING FRAMEWORK
## SCORE IT
## STORE SCORES SOMEWHERE

import pandas as pd
import numpy as np
from datetime import datetime, timezone
import json

cookies_df = pd.read_json("cookies_output.json")
#print(cookies_df.head(5))

bad = 2
neutral = 1
fine = 0

secure_m = 1
httpOnly_m = 1
cookieDomain_m = 1
path_m = 1
expires_m = 1
sameSite_m = 1

dt = datetime(2025, 4, 22, 23, 0, 0, tzinfo=timezone.utc)
creation_time = dt.timestamp()
print(creation_time)

one_month = 60*60*24*30 # number of seconds for UTC
one_week =  60*60*24*7

cookies_df5 = cookies_df[:5]
#print(cookies_df5)

data = [[]]


domain_index = 0
for _,main_domain in cookies_df.iterrows():
    if(domain_index == 0):
        data = [[main_domain["domain"]]]
    else:
        print(domain_index)
        data.append([main_domain["domain"]])# [domain name ie google.com, [cookie 1 score, cookie 2 score]]
    #print(main_domain)
    cookie_index = 0
    #print(main_domain["cookies"])

    for cookie in main_domain["cookies"]:
        #print(cookie)
        if("error" in cookie): # if no actual cookie data then just go to next cookie
            continue
        score = 0
        
        if(cookie["secure"] == False): #if change the min from 0, add the other conditions
            score+=(bad*secure_m)
        
        if(cookie["httpOnly"] == False):
            score+=(bad*httpOnly_m)
        
        if(cookie["domain"] != ""):
            if (cookie["domain"] == main_domain["domain"]): # if exact match
                score+=(neutral*cookieDomain_m)
            else:
                temp_main_domain = main_domain["domain"]
                temp_cookie_domain = cookie["domain"]
                if("www" in temp_main_domain): # check if the domains would match with/out www
                    temp_main_domain = temp_main_domain[3:]
                if("www." in temp_cookie_domain):
                    temp_main_domain = temp_main_domain[4:]
                if(temp_main_domain == temp_cookie_domain): # if non-www match
                    score+=(neutral*cookieDomain_m)
                else: # no match whatsoever
                    score+=(bad*cookieDomain_m)


        if(cookie["path"] == "/"):
            if(not("__Host" in cookie["name"])):
                score+=(bad*path_m)
        
        time_diff = cookie["expires"] - creation_time
        if(time_diff > one_month):
            score+=(bad*expires_m)
        elif(time_diff > one_week):
            score+=(neutral*expires_m)

        if(cookie["sameSite"] == "None"):
            score+=(bad*sameSite_m)



        if(cookie_index == 0):
            data[domain_index].append([score])
        else:
            #print(data)
            data[domain_index][1].append(score)
        cookie_index+=1
    
    domain_index+=1

#print(data)

with open('2025-05-11_test_all.json', 'w') as f:
    json.dump(data, f, indent = 4)