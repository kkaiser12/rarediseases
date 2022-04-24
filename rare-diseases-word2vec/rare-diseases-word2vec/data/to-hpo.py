import csv
import os

# Made by Alexander Weiss alexander.weiss@mail.de
info={
    "lines":0,
    "no_loinc":0,
    "no_possible_hpo_features":0,
    "no_active_hpo_features":0,
    "no_annotation":0
    }
loinc_dict = {}
anno_dict={}
with open(os.path.join(os.path.dirname(__file__),"loinc2hpo-annotations.tsv")) as anno_f:
    anno = csv.reader(anno_f, delimiter='	', quotechar='"')
    next(anno)
    for line in anno:
        if not line[0] in anno_dict:
            anno_dict[line[0]]={line[2]:line[3]}
        else:
            anno_dict[line[0]][line[2]]=line[3]

with open(os.path.join( os.path.dirname(__file__),"D_LABITEMS.csv")) as D_labitems_f:
    D_labitems = csv.reader(D_labitems_f, delimiter=',', quotechar='"')
    next(D_labitems)
    for line in D_labitems:
        loinc_dict[line[1]]=line[5]
data=[]
with open(os.path.join( os.path.dirname(__file__),"LABEVENTS.csv")) as labevents_f:
    labevents = csv.reader(labevents_f, delimiter=',', quotechar='"')
    next(labevents)
    for line in labevents:
        info["lines"]+=1
        line_copy=line
        loinc_code=loinc_dict[line[3]]
        if loinc_code == "":
            info["no_loinc"]+=1
        line_copy.append(loinc_code)
        if loinc_code in anno_dict:
            possible_hpo_features=list(anno_dict[loinc_code].values())
            if len(possible_hpo_features)==0:
                info["no_possible_hpo_features"]+=1
            line_copy.append(possible_hpo_features)
            active_hpo_features=[]
            if "low" in line[5].lower() and "L" in anno_dict[loinc_code]:
                active_hpo_features=anno_dict[loinc_code]["L"]
            elif "neg" in line[5].lower() and "NEG" in anno_dict[loinc_code]:
                active_hpo_features=anno_dict[loinc_code]["NEG"]
            elif line[8] == "abnormal":
                for i in anno_dict[loinc_code]:
                    if i != "N":
                        active_hpo_features.append(anno_dict[loinc_code][i])
            if len(active_hpo_features)==0:
                info["no_active_hpo_features"]+=1
            line_copy.append(active_hpo_features)
            # print(line_copy)
            data.append(line_copy)
        else:
            info["no_annotation"]+=1
with open("LABEVENTS_HPO.csv","w") as f:
    string=""
    string+="row_id,subject_id,hadm_id,itemid,charttime,value,valuenum,valueuom,flag,possible_hpo_features,active_hpo_features\n"
    for i in data:
        for x in range(9):
            string+=i[x]
            string+=","
        string+=";".join(i[10])
        string+=","
        string+=";".join(i[11])
        string+="\n"
    f.write(string)
print(info)