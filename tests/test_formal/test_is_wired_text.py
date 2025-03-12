import pytest 
import json 

from open_r1.formal_utils.wired_text_detect   import is_wired_text


f_p = "tests/test_formal/smt_test_data_dirs/tmp_small_wired.jsonl"

item_list =[json.loads(x) for x in   open(f_p).readlines() ] 

def test_from_jsonl ( ):
    is_wired = 0 
    
    for each in item_list :
        flg = is_wired_text(each["assert_str"] )
        # flg = int( wired_dict["flg"] )
        is_wired += flg 
        
    assert is_wired==57 , is_wired