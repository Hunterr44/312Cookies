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

secure_m = 3 # can be intercepted by unknown 3rd party and HTTPS data sending is standard protocal --- this violates said standard
httpOnly_m = 2 # can allow local scripting to access, vulnerable to leakage attacks and user virus
cookieDomain_m = 3 # allows sharing with 3rd party - opens door to data privacy risks 
path_m = 1 # generally covered by other categories such as __HOST; internal issues are less problematic than external domain vulnerability
expires_m = 1 # low priority
sameSite_m = 2 # generally want to limit scope of data sharing; but none can be useful sometimes, but our data will not have instances where none is beneficial (SSO login etc)

dt = datetime(2025, 4, 22, 23, 0, 0, tzinfo=timezone.utc) # completion time of runnning
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
        if("error" in cookie): # if error getting cookie data then just go to next cookie
            if(cookie_index == 0):
                data[domain_index].append([-1])
            else:
                #print(data)
                data[domain_index][1].append(-1)
            cookie_index+=1
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

def score_cookies(domain: str, cookies: list):
    scores = []

    for cookie in cookies:
        if "error" in cookie:
            scores.append(-1)
            continue

        score = 0

        if not cookie.get("secure", False):
            score += bad * secure_m

        if not cookie.get("httpOnly", False):
            score += bad * httpOnly_m

        cookie_domain = cookie.get("domain", "")
        if cookie_domain:
            if cookie_domain == domain:
                score += neutral * cookieDomain_m
            else:
                stripped_cookie_domain = cookie_domain.replace("www.", "")
                stripped_domain = domain.replace("www.", "")
                if stripped_cookie_domain == stripped_domain:
                    score += neutral * cookieDomain_m
                else:
                    score += bad * cookieDomain_m

        if cookie.get("path", "") == "/" and "__Host" not in cookie.get("name", ""):
            score += bad * path_m

        expires = cookie.get("expires", 0)
        time_diff = expires - datetime.utcnow().timestamp()
        if time_diff > one_month:
            score += bad * expires_m
        elif time_diff > one_week:
            score += neutral * expires_m

        if cookie.get("sameSite") == "None":
            score += bad * sameSite_m

        scores.append(score)

    return scores

with open('2025-05-11_test_all.json', 'w') as f:
    json.dump(data, f, indent = 4)