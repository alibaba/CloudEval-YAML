import yaml

def append_labels_to_keys(kv_labeled_str):
    output_lines = []
    for line in kv_labeled_str.splitlines():
        if '#' in line and line.rstrip().endswith('*'):
            split = line.split(':', 1)
            output_lines.append(split[0].rstrip() + '*:' + split[1]) # rstrip() in case there are spaces trailing the key
        else:
            output_lines.append(line)
    if kv_labeled_str.endswith('\n'):
        output_lines.append('')
    return '\n'.join(output_lines)

def match_dict(target_dict, kv_labeled_dict):
    # number of keys should be the same
    if len(target_dict) != len(kv_labeled_dict):
        return False
    
    for kv_labeled_key, kv_labeled_value in kv_labeled_dict.items():
        # check the existence of the key
        if kv_labeled_key.rstrip('*') not in target_dict:
            return False

        if isinstance(kv_labeled_value, dict):
            assert not kv_labeled_key.endswith('*'), f'Labels should only be applied to leaf nodes'
            if not match_dict(target_dict[kv_labeled_key], kv_labeled_value):
                return False
        elif isinstance(kv_labeled_value, list):
            if len(kv_labeled_value) > 0 and isinstance(kv_labeled_value[0], dict):
                # all elements in the list should be dict, otherwise we consider it sematically incorrect
                assert not kv_labeled_key.endswith('*'), f'Labels should only be applied to leaf nodes'

                # Compare the length of the list
                if len(target_dict[kv_labeled_key]) != len(kv_labeled_value):
                    return False
                
                # Compare each element in the list, while ignoring the order
                for kv_labeled_value_item in kv_labeled_value:
                    found = False
                    for target_dict_item in target_dict[kv_labeled_key]:
                        if match_dict(target_dict_item, kv_labeled_value_item):
                            found = True
                            break
                    if not found:
                        return False
            else:
                # if this is a leaf node
                if not kv_labeled_key.endswith('*'):
                    if target_dict[kv_labeled_key] != kv_labeled_value:
                        return False
        else:
            if not kv_labeled_key.endswith('*'):
                if target_dict[kv_labeled_key] != kv_labeled_value:
                    return False
    return True

def get_leaf_nodes(target_dict):
    leaf_nodes = []
    for key, value in target_dict.items():
        if isinstance(value, dict):
            sub_tree_leaf_nodes = get_leaf_nodes(value)
            leaf_nodes += [{'key_path': [key.rstrip('*')] + leaf_node['key_path'], 
                            'value': leaf_node['value'],
                            'wildcard': leaf_node['wildcard']} 
                            for leaf_node in sub_tree_leaf_nodes]
        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
            # all elements in the list should be dict, otherwise we consider it sematically incorrect
            for item in value:
                sub_tree_leaf_nodes = get_leaf_nodes(item)
                leaf_nodes += [{'key_path': [key.rstrip('*')] + leaf_node['key_path'], 
                                'value': leaf_node['value'],
                                'wildcard': leaf_node['wildcard']} 
                                for leaf_node in sub_tree_leaf_nodes]
        else:
            leaf_nodes.append({'key_path': [key.rstrip('*')], 
                               'value': value, 
                               'wildcard': key.endswith('*')})
    return leaf_nodes

def calc_intersection(target_leaf_nodes, reference_leaf_nodes):
    intersection = 0
    for reference_leaf_node in reference_leaf_nodes:
        for target_leaf_node in target_leaf_nodes:
            if target_leaf_node['key_path'] == reference_leaf_node['key_path']:
                if reference_leaf_node['wildcard'] \
                or target_leaf_node['value'] == reference_leaf_node['value']:
                    intersection += 1
                    break
    return intersection

def test(result_str="", kv_labeled_str=""):
    try:
        result_dict_list = list(yaml.safe_load_all(result_str))
    except Exception as e:
        return False

    try:
        kv_labeled_dict_list = list(yaml.safe_load_all(append_labels_to_keys(kv_labeled_str)))
        assert len(kv_labeled_dict_list) > 0, 'kv_labeled_dict_list should not be empty'
    except Exception as e:
        raise Exception(f"Error occurred while loading [kv_labeled_str]: {str(e)}") from e
    
    # pad result_dict_list or kv_labeled_dict_list with empty dict
    diff_len = len(result_dict_list) - len(kv_labeled_dict_list)
    if diff_len > 0:
        kv_labeled_dict_list += [{} for _ in range(diff_len)]
    elif diff_len < 0:
        result_dict_list += [{} for _ in range(abs(diff_len))]
    
    total_intersection = 0
    total_union = 0
    for result_dict, kv_labeled_dict in zip(result_dict_list, kv_labeled_dict_list):
        result_leaf_nodes = get_leaf_nodes(result_dict)
        reference_leaf_nodes = get_leaf_nodes(kv_labeled_dict)
        intersection = calc_intersection(result_leaf_nodes, reference_leaf_nodes)
        union = len(result_leaf_nodes) + len(reference_leaf_nodes) - intersection
        total_intersection += intersection
        total_union += union
        
    return total_intersection / total_union

    