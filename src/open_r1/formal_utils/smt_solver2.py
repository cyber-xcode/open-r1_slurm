import random 

import re 
import z3 
from .SMT2 import  convert_and_split 
from .SMT2 import  SMT_verifier  



def add_parentheses_to_pow_args(expression):
    pattern = re.compile(r'pow\(([^,]+),([^)]+)\)')
    def replacer(match):
        arg1, arg2 = match.groups()
        return f'pow(({arg1}),({arg2}))'
    result = pattern.sub(replacer, expression)
    return result






def smt_resolve_api(SMT2str,result, total_assert_c = None   ,fail_score=0.1 , success_score=1.0,  error_score=0.0  ):
    if type(result)!=str  and type(result) in [tuple,list]:
        result = "\n".join( result )
    result_ori = result
    result_list= convert_and_split.extract_asserts( result )
    if total_assert_c is None :
        total_assert_c = len( result_list )
    
    if total_assert_c == 0 :
        return {
            "total_assert_c": total_assert_c, 
            "status_list":[],
            "score": error_score , 
            "msg":"cannot find assert from C",
            }
        
    result = "\n".join ( result_list )
    # result = convert_and_split.merge_asserts( result_list )
    
    result=add_parentheses_to_pow_args(result)
    result=extract_assert_statements(result)
    
    result_new = [x for x in result if "?" not in x ]
    
    smtlib2 = None 
    # smtlib2=convert_and_split.convert_c_assert_list_to_smtlib2(result_new)
    try:
        smtlib2=convert_and_split.convert_c_assert_list_to_smtlib2(result_new)
    except Exception : 
        pass 
    # except AttributeError : 
    #     pass 
    if not smtlib2 or len(smtlib2) == 0 :
        return {
            "total_assert_c": 0, 
            "status_list":[],
            "score": error_score , 
            "msg":"cannot convert c to smt2, assert is {}, -> origin assert {}".format( result_new, result_ori ),
            }
        

    
    
    PT = smtlib2 
    sMT_verifier = SMT_verifier.SMT_verifier()

    verify_list = [] 
    for Iteration in range( len( PT )):
        Can_I=PT[Iteration]
        Can_I_smt = Can_I[7:-1]
        verified  = fail_score 
        try :
            Counter_example, istrue = sMT_verifier.verify(Can_I, SMT2str)

            if istrue and Counter_example is None :
                verified = success_score
                # score = 1 
            # if not istrue and Counter_example is None : #except 
            #     verified =  error_score
        except TimeoutError as OOT:  # Out Of Time
            verified = fail_score
        except AssertionError as OOT:  # Out Of Time
            verified = fail_score
        except z3.Z3Exception:
            verified = error_score
        except Exception :
            verified = error_score
             
        
        verify_list.append( verified )

    return {
        "total_assert_c": total_assert_c, 
        "status_list":verify_list,
        "score": sum( list(map(float, verify_list ) ) ) / total_assert_c 
        }






def extract_assert_statements(text):
    """
    Extracts all assert(...) statements from the given text.

    Parameters:
    - text: A string from which to extract assert statements.

    Returns:
    - A list of extracted assert statements.
    """
    def is_parentheses_balanced(s):
        stack = []
        matching_parentheses = {')': '(', ']': '[', '}': '{'}
        
        for char in s:
            if char in '({[':
                stack.append(char)
    
            elif char in ')}]':
                if not stack or stack[-1] != matching_parentheses[char]:
                    return False
                stack.pop()
        return not stack
    
    def undefined_function(subassertion):
        cannot_exist = ['min', '?', 'max', 'unknown', 'factorial', 'pow', 'for', '=>', 'old', 'INT', '->>', '->']
        for cannot_exist_function in cannot_exist:
            if str(cannot_exist_function) in subassertion:
                return False
        return True
    
    # Define a regular expression pattern to match assert statements
    pattern = r'assert\s*\((.*?)\)\s*;'
    
    # Find all occurrences of the pattern in the text
    matches = re.findall(pattern, text, flags=re.DOTALL)
    
    # Format the matches as assert statements and return them
    result = []
    for match in matches:
        if is_parentheses_balanced(match) and undefined_function(match):
            parts = match.split(',')
            for part in parts:
                tmp = f"assert({part.strip()});"
                if '"' not in tmp:
                    result.append(tmp)
    return result





def smt_resolve_api_counterexample(SMT2str,result, total_assert_c = None   ,fail_score=0.1 , success_score=1.0,  error_score=0.0  ):
    if type(result)!=str  and type(result) in [tuple,list]:
        result = "\n".join( result )
    result_ori = result
    result_list= convert_and_split.extract_asserts( result )
    if total_assert_c is None :
        total_assert_c = len( result_list )
    
    if total_assert_c == 0 :
        return {
            "total_assert_c": total_assert_c, 
            "status_list":[],
            "score": error_score , 
            "msg":"cannot find assert from C",
            }
        
    result = "\n".join ( result_list )
    # result = convert_and_split.merge_asserts( result_list )
    
    result=add_parentheses_to_pow_args(result)
    result=extract_assert_statements(result)
    
    result_new = [x for x in result if "?" not in x ]
    
    smtlib2 = None 
    # smtlib2=convert_and_split.convert_c_assert_list_to_smtlib2(result_new)
    try:
        smtlib2=convert_and_split.convert_c_assert_list_to_smtlib2(result_new)
    except Exception : 
        pass 
    # except AttributeError : 
    #     pass 
    if not smtlib2 or len(smtlib2) == 0 :
        return {
            "total_assert_c": 0, 
            "status_list":[],
            "score": error_score , 
            "msg":"cannot convert c to smt2, assert is {}, -> origin assert {}".format( result_new, result_ori ),
            }
        

    
    
    PT = smtlib2 
    sMT_verifier = SMT_verifier.SMT_verifier()

    verify_list = [] 
    for Iteration in range( len( PT )):
        Can_I=PT[Iteration]
        Can_I_smt = Can_I[7:-1]
        verified  = fail_score 
        try :
            Counter_example, istrue = sMT_verifier.verify(Can_I, SMT2str)

            if istrue and Counter_example is None :
                verified = success_score
            
            if istrue and Counter_example is not None :
                verified = min(success_score, max(fail_score, fail_score + random.randint(1,50)/500 ) )


        except TimeoutError as OOT:  # Out Of Time
            verified = fail_score
        except AssertionError as OOT:  # Out Of Time
            verified = fail_score
        except z3.Z3Exception:
            verified = error_score
        except Exception :
            verified = error_score
             
        
        verify_list.append( verified )

    return {
        "total_assert_c": total_assert_c, 
        "status_list":verify_list,
        "score": sum( list(map(float, verify_list ) ) ) / total_assert_c 
        }


