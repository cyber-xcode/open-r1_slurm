import json
import os 

data = [json.loads(x) for x in open("verified_z3_benchmarks621_assert_y_withsmt.jsonl").readlines() ] 


save_dir = "./save_dir"
os.makedirs(save_dir, exist_ok = True ) 

for item in data :
    idx=  item["idx"]
    if "code2inv_benchmarks" not in idx :
        continue 
    idxx =  os.path.basename( idx )
    smt_code = item["smt_code"] 

    save_path = os.path.join(save_dir ,  idxx )
    with open(save_path,"w") as fw:
        fw.write( smt_code )
