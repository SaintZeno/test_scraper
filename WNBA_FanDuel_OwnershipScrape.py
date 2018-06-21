
# coding: utf-8

# In[42]:


import pandas as pd
from urllib import urlopen
from bs4 import BeautifulSoup
from bs4 import Comment
import re
import json




# In[43]:


## parameters and bs4 connection
url = "https://www.linestarapp.com/Ownership/Sport/WNBA/Site/FanDuel/PID/379"
output_path = '/output/path/goes/here/'

html = urlopen(url)
print(html)
soup = BeautifulSoup(html, "html.parser")

#print(soup)


# In[44]:


## scrape page to get pretty column headers
column_headers = [td.getText() for td in
                      soup.findAll('tr', limit=10)[1].findAll('td')]

print(column_headers)


# In[45]:


## function definitions

def format_script_string(hold):
    hold = hold.replace('\r', '')
    hold = hold.replace('\n', '')
    return(hold)

def format_js_var_string(x):
    x = x.replace(sub_str, '').replace("'", '"')
    x = x.replace('            ', ' ').replace(';', '') ## replacing the big space isn't needed but makes the string easier to read
    ## these are specific to the js variable dict... must be adjusted based on what is pulled  
    ## want to replace each key so that json.loads can read it correctly
    ## since each key is a string need to add quotes to it to make it {"key":value} format
    x = x.replace('id:', '"id":') 
    x = x.replace('name:', '"name":')
    x = x.replace('owned:', '"owned":')
    x = x.replace('pos:', '"pos":')
    x = x.replace('team:', '"team":')
    x = x.replace('sal:', '"sal":')
    ## finally, we replace the pesky piece of the js variable.. the fucking ',}' and ',]' (these don't work w/ json loads)
    x = re.sub(',\s*}', '}', x) ## note: this give weird results depending on the strings passed.. 
    x = re.sub(',\s*]', ']', x)
    return(x)
            
            
def scrape_scripts(sub_str, scripts):
    #html_scripts = soup.findAll('script')
    #sub_str = 'var actualResultsDict = '
    res = {}
    temp = re.compile(sub_str + '{(.*)};', re.MULTILINE) 
    for script in scripts: ## loop thru scripts tags, then search the strings for matches of the `temp` search above
        hold = format_script_string(str(script.string))
        x = temp.search(hold) ## do the search 
        if x: ## if we found something then.. 
            x = x.group()
            x = format_js_var_string(x) ## format js variable string 
            res = json.loads(x)
    return(res)



# In[46]:


sub_str = 'var actualResultsDict = '  ## this is hte js variable dict that holds the table data 
#sub_str = 'var projectedSlatesDict = ' ## this is hte js variable dict that holds the table data 

json_object = scrape_scripts(sub_str, soup.findAll('script'))

## need to format the json_object a bit for pandas
res = []
for slate_id, sub_list in json_object.items():
    for val in sub_list:
        val.update({'slate_id':slate_id})
        res.append(val)

        
res = pd.DataFrame(res)


# In[47]:


## rename pandas df 
new_names = {'id': 'player_id', ## could be wrong about this.. not really sure what the ID is.. 
             'owned': 'ownership',
             'pos': 'position',
             'sal': 'salary',
             'team':'team',
             'slate_id': 'slate_id'  ## have no clue what this is... take a look at print(soup) and youll see how the variables are structured
            }

res.rename(columns = new_names, inplace=True)


# In[48]:


res


# In[ ]:


#res.to_csv(output_path + 'res.csv')

