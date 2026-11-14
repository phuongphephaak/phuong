import json,os,re,sys,time,urllib.parse,urllib.request
UA={"User-Agent":"EducationalVideoDraft/1.0 (non-commercial research script)"}
cr=json.load(open('photos/credits.json')) if os.path.exists('photos/credits.json') else {}
for name,t in json.load(open(sys.argv[1])).items():
    if name in cr: continue
    fn=t.split(":",1)[1].replace(" ","_")
    try:
        data=urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/wiki/Special:FilePath/"+urllib.parse.quote(fn)+"?width=1280",headers=UA),timeout=120).read()
    except Exception as e:
        print("FAIL",name,e,flush=True); time.sleep(10); continue
    open(f"photos/{name}.jpg","wb").write(data)
    lic="?";art=""
    try:
        u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","titles":t,"prop":"imageinfo","iiprop":"extmetadata"})
        pg=list(json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))["query"]["pages"].values())[0]
        md=pg["imageinfo"][0]["extmetadata"]; g=lambda k: re.sub("<[^>]+>","",md.get(k,{}).get("value","")).strip()
        lic,art=g("LicenseShortName"),g("Artist")[:80]
    except Exception as e: print("meta fail",name,e)
    cr[name]={"title":t,"license":lic,"artist":art}; json.dump(cr,open('photos/credits.json','w'),ensure_ascii=False,indent=1)
    print(name,len(data),lic,"|",art[:40],flush=True); time.sleep(6)
