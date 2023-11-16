import yaml
import deepdiff

def test(result_str="", reference_str=""):
    try:
        yaml_dict_list1 = list(yaml.safe_load_all(result_str))
    except:
        return 0
    try:
        yaml_dict_list2 = list(yaml.safe_load_all(reference_str))
        assert len(yaml_dict_list2) > 0, 'yaml_dict_list2 should not be empty'
    except:
        print(f"Invalid reference code:\n{reference_str}")
        return 0
    
    if len(list(yaml_dict_list1)) != len(list(yaml_dict_list2)):
        return False
    
    for yaml_dict1, yaml_dict2 in zip(yaml_dict_list1, yaml_dict_list2):
        diff = deepdiff.DeepDiff(yaml_dict1, yaml_dict2)
        if len(diff) > 0:
            return False
    return True
