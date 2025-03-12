import pytest

from open_r1.formal_utils.smt_solver  import smt_resolve_api

class retobj :
    def __init__(self,josnx ):
        self.josnx = josnx 
    status_code =200 
    def json(self):
        return{"smt_verify": self.josnx }
    
class CCC:
   def post (self,url , json=None  ):
       json_dict = json 
       source_code = json_dict["source_code"]
       assertation = json_dict["assertation"]
       
       ret_json= smt_resolve_api(SMT2str=source_code,result=assertation)
       obj  = retobj( josnx=ret_json )
       return obj 
       # setattr(ret_json, "status_code", 200 )
client = CCC()




flag_fail = 0.1 
flag_error = 0.0 

SMT_105 = open("tests/test_formal/smt_test_data_dirs/105.c.smt.txt").read()
SMT_STR = open("tests/test_formal/smt_test_data_dirs/t_solved.c.smt").read()


def test_success_1_source_code():
    result = [
        "assert(hi == 2 * mid + lo && mid >= 0);", 
    
        "assert(hi == 20 * mid + lo  );", 
        "assert( 1==1  );", 
        ]
    # "assert(hi == 20 * mid + lo && mid >= 0);", 
    result = "\n".join( result )
    # Test case for empty source code
    response = client.post("/smt_verify", json={"source_code": SMT_STR.strip(), 
                                                "assertation": "assert(1 == 1);"})
    assert response.status_code == 200
    assert "smt_verify" in response.json()
    assert  response.json()["smt_verify"]["score"]  == flag_fail , response.json() #== {"smt_verify": None}


    response = client.post("/smt_verify", json={"source_code": SMT_STR.strip(), 
                                                "assertation": result })
    assert response.status_code == 200
    assert "smt_verify" in response.json()
    assert  response.json()["smt_verify"]["score"]  > 0.3 and response.json()["smt_verify"]["score"]  < 0.4, response.json()



def test_success_2_source_code():
    result = "assert((x >= 0) && (x <= n) && (n >= 0));"
    response = client.post("/smt_verify", json={"source_code": SMT_105.strip(), 
                                                "assertation": "assert(1 == 1);"})
    assert response.status_code == 200
    assert "smt_verify" in response.json()
    assert  response.json()["smt_verify"]["score"]  == flag_fail #== {"smt_verify": None}


    result = "assert(((n < 0) && (x == 0)) || ((n >= 0) && (0 <= x && x <= n)));"
    
    response = client.post("/smt_verify", json={"source_code": SMT_105.strip(), 
                                                "assertation": result })
    assert response.status_code == 200
    assert "smt_verify" in response.json()
    assert  response.json()["smt_verify"]["score"] ==1 


SMT_129 = open("tests/test_formal/smt_test_data_dirs/129.c.smt.txt").read()

def test_success_3_source_code():
    response = client.post("/smt_verify", json={"source_code": SMT_129.strip(), 
                                                "assertation": "assert(1 == 1);"})
    assert response.status_code == 200
    assert "smt_verify" in response.json()
    assert  response.json()["smt_verify"]["score"]  == flag_fail  #== {"smt_verify": None}
    #
    #
    result = 'assert((x >= 1) && (y <= 0 || x <= y) && (x <= y || x >= y));\n'
    response = client.post("/smt_verify", json={"source_code": SMT_129.strip(), 
                                                "assertation": result })
    assert response.status_code == 200
    assert "smt_verify" in response.json()
    assert  response.json()["smt_verify"]["score"]  == flag_fail  , response.json() 

    result = "assert((x >= 1) && ((x & (x - 1)) == 0));\n" 
    result = "assert((x >= 1) && (x & (x - 1)) == 0));\n" ## syntax error 
    response = client.post("/smt_verify", json={"source_code": SMT_129.strip(), 
                                                "assertation": result })
    assert response.status_code == 200
    assert "smt_verify" in response.json()
    assert  response.json()["smt_verify"]["score"]  == flag_error ,response.json()
    assert  response.json()["smt_verify"]["status_list"]  == [] , response.json() 

    
    result = "assert((x >= 1) && ( ((x - 1)) == 0) );\n"
    response = client.post("/smt_verify", json={"source_code": SMT_129.strip(), 
                                                "assertation": result })
    assert response.status_code == 200
    assert "smt_verify" in response.json()
    assert  response.json()["smt_verify"]["score"]  == flag_fail , response.json()

    result = "assert(x >= 1 && ((x & (x - 1)) == 0));"
    response = client.post("/smt_verify", json={"source_code": SMT_129.strip(), 
                                                "assertation": result })
    assert response.status_code == 200
    assert "smt_verify" in response.json()
    assert  response.json()["smt_verify"]["score"] ==0, response.json() 




    result = "assert((x >= 1) && (y > 0) || (x >= 1 && y <= 1));"
    response = client.post("/smt_verify", json={"source_code": SMT_129.strip(), 
                                                "assertation": result })
    assert response.status_code == 200
    assert "smt_verify" in response.json()
    assert  response.json()["smt_verify"]["score"] ==1, response.json() 





T_SOLVED_SMT_STR = open("tests/test_formal/smt_test_data_dirs/t_solved.v2.smt").read()


def test_success_tsolved_source_code():
    # Test case for empty source code
    response = client.post("/smt_verify", json={"source_code": T_SOLVED_SMT_STR.strip(), 
                                                "assertation": "assert(1 == 1);"})
    assert response.status_code == 200
    assert "smt_verify" in response.json()
    assert  response.json()["smt_verify"]["score"]  == flag_fail , response.json() #== {"smt_verify": None}


    result = [
        "assert(hi == 2 * mid + lo && mid >= 0);"         
        ]
    # "assert(hi == 20 * mid + lo && mid >= 0);", 
    result = "\n".join( result )
    response = client.post("/smt_verify", json={"source_code": T_SOLVED_SMT_STR.strip(), 
                                                "assertation": result })
    assert response.status_code == 200
    assert "smt_verify" in response.json()
    assert  response.json()["smt_verify"]["score"]  > flag_fail , response.json()





def test_empty_source_code():
    # Test case for empty source code
    response = client.post("/smt_verify", json={"source_code": "", "assertation": "assert(1 == 1);"})
    assert response.status_code == 200
    assert response.json()["smt_verify"]["score"]  == flag_fail  #  == {"smt_verify": None}

def test_empty_assertation():
    # Test case for empty assertion
    response = client.post("/smt_verify", json={"source_code": "(set-logic QF_LIA)", "assertation": ""})
    assert response.status_code == 200
    assert response.json()["smt_verify"]["score"] == flag_error  , response.json() 

def test_valid_source_code_and_assertation():
    # Test case for valid source code and assertion
    source_code = """
    (set-logic QF_LIA)
    (declare-const x Int)
    (declare-const y Int)
    (assert (= x y))
    """
    assertation = "assert(x == y);"
    response = client.post("/smt_verify", json={"source_code": source_code, "assertation": assertation})
    assert response.status_code == 200
    # Assuming the SMT solver returns some information
    assert "smt_verify" in response.json()

def test_multiple_assertations():
    # Test case for multiple assertions
    source_code = """
    (set-logic QF_LIA)
    (declare-const x Int)
    (declare-const y Int)
    (assert (= x y))
    """
    assertation = """
    assert(x == y);
    assert(x == 2 * y);
    assert(1 == 1);
    """
    response = client.post("/smt_verify", json={"source_code": source_code, "assertation": assertation})
    assert response.status_code == 200
    # Assuming the SMT solver returns some information
    assert "smt_verify" in response.json()

def test_invalid_assertation():
    # Test case for invalid assertion
    source_code = """
    (set-logic QF_LIA)
    (declare-const x Int)
    (declare-const y Int)
    (assert (= x y))
    """
    assertation = "assert(x == y + 1);"
    response = client.post("/smt_verify", json={"source_code": source_code, "assertation": assertation})
    assert response.status_code == 200
    # Assuming the SMT solver returns some information
    assert "smt_verify" in response.json()

def test_complex_assertation():
    # Test case for complex assertion
    source_code = """
    (set-logic QF_LIA)
    (declare-const x Int)
    (declare-const n Int)
    (assert (and (>= x 0) (<= x n) (>= n 0)))
    """
    assertation = "assert((x >= 0) && (x <= n) && (n >= 0));"
    response = client.post("/smt_verify", json={"source_code": source_code, "assertation": assertation})
    assert response.status_code == 200
    # Assuming the SMT solver returns some information
    assert "smt_verify" in response.json()

def test_another_complex_assertation():
    # Test case for another complex assertion
    source_code = """
    (set-logic QF_LIA)
    (declare-const x Int)
    (declare-const n Int)
    (assert (or (and (< n 0) (= x 0)) (and (>= n 0) (<= 0 x) (<= x n))))
    """
    assertation = "assert(((n < 0) && (x == 0)) || ((n >= 0) && (0 <= x && x <= n)));"
    response = client.post("/smt_verify", json={"source_code": source_code, "assertation": assertation})
    assert response.status_code == 200
    # Assuming the SMT solver returns some information
    assert "smt_verify" in response.json()