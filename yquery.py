#!/usr/bin/env python
# POC: Guoqing.Ge@noaa.gov
#
import yaml
import sys

# Custom Dumper class to modify list formatting
class MyDumper(yaml.Dumper):
  def represent_list(self, data):
    # Check if the list contains only simple literals (strings, numbers, booleans)
    if all(isinstance(item, (str, int, float, bool)) for item in data):
      # Use compact flow style ([])
      return self.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)
    else:
      # Use block style (-)
      return self.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=False)

def shallow(data): # print out the information with "max_depth=1"
  if isinstance(data, dict):
    for key in data.keys():
      print(f"{key}")
  elif isinstance(data,list):
     print(f'[a list of {len(data)} item(s)]')

def traverse(subdata,n): # traverse the yaml dict tree until reaching leaves
  if isinstance(subdata,dict):
    n=n+1
    for key,value in subdata.items():
      print(f"{' '*(n-1)*2}{key}")
      traverse(value,n)
  elif isinstance(subdata,list):
    print(f"{' '*n*2}[a list of {len(subdata)} item(s)]")
    for item in subdata:
      traverse(item,n)

def getFinalValue(subdata,keytree): # get the value for a hirearchy query string
  if keytree: # not empty
    if isinstance(subdata,dict):
      subdata=subdata[keytree.pop(0)]
    elif isinstance(subdata,list):
      index=int(keytree.pop(0))
      if index <0: 
        index=0
      elif index >= len(subdata):
        index=len(subdata)-1
      subdata=subdata[index]
    if not keytree: # if empty now
      return subdata
    else:
      return getFinalValue(subdata,keytree)

# ====== main =========
MyDumper.add_representer(list, MyDumper.represent_list)
args=sys.argv
nargs=len(args)-1
if nargs <1:
  print(f"Usage: {args[0]} <file> [querystr] [shallow|traverse|dump|changeto=''] #default action is shallow")
  exit()
myfile=args[1]
myquerystr=""
if nargs >1:
  myquerystr=args[2]
action="shallow"
if nargs>2:
  action=args[3]

with open(myfile) as yfile:
  data=yaml.safe_load(yfile)

if myquerystr:
  keytree=myquerystr.split("/")
  subdata=(getFinalValue(data,keytree))

  if action=="shallow":
    shallow(subdata)
  elif action=="traverse":
    traverse(subdata,0)
  elif action=="dump":
    yaml.dump(subdata, sys.stdout, Dumper=MyDumper, default_flow_style=False, sort_keys=False) # explicit_end=False to disable the explicit "..." output which indicates the end or reaching the leaves

else:
  shallow(data)
