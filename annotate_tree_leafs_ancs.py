#!/usr/bin/env python

import newick
import parse
import argparse
import os
import re


#####
### calibrate internal nodes
def parse_tree(tree_str):
    nested_tree = []
    level = 0
    for i in tree_str:
        if i=='(':
            
            ## add new one
            nested_tree.append(['', 'OPEN', level]) ## [string, open_status, started_level]
            
            ## and update others
            for chunk_index in range(len(nested_tree)):
                if nested_tree[chunk_index][1] in ['OPEN','LATE_CLOSE']:
                    nested_tree[chunk_index][0] += i
            level+=1
            
        elif i==')':
            
            level-=1
            
            for chunk_index in range(len(nested_tree)):
                if nested_tree[chunk_index][1] in ['OPEN','LATE_CLOSE']:
                    nested_tree[chunk_index][0] += i
                
                if nested_tree[chunk_index][2]==level: ## close to finish one
                    if nested_tree[chunk_index][1] in ['OPEN']:
                        nested_tree[chunk_index][1] = 'LATE_CLOSE'
        
        elif i==':':
                
            for chunk_index in range(len(nested_tree)):
                if nested_tree[chunk_index][1] in ['OPEN']:
                    nested_tree[chunk_index][0] += i
            
                elif nested_tree[chunk_index][1]=='LATE_CLOSE':  ## finish one
                    nested_tree[chunk_index][1] = 'CLOSE'

        else:
            for chunk_index in range(len(nested_tree)):
                if nested_tree[chunk_index][1] in ['OPEN','LATE_CLOSE']:
                    nested_tree[chunk_index][0] += i
                
        # print(nested_tree)
    return nested_tree
        
        
        
        

def cali_inter_nodes(tree_str):
    ### calibrate internal nodes
    unchange_epoch = 0
    for iter_ in range(100):
        change_count = 0
        parsed_tree = parse_tree(tree_str)
        sorted_parsed_tree = sorted(parsed_tree, key=lambda x:len(x[0]))
        for i in sorted_parsed_tree:
            sp_count = len(i[0].split(','))
            forgound_count = len(re.findall('{Foreground}', i[0]))
            if forgound_count==sp_count:
                tree_str = tree_str.replace(i[0], i[0]+'{Foreground}')
                change_count+=1


        if change_count==0:
            unchange_epoch+=1
        print('Annotation added: ',change_count)
        if unchange_epoch>=5: ## early stop
            break

    print('DONE!')
    return tree_str
        
    
def annotate_tree(aa, anno_list):
    ### get str
    tree_str = aa.newick
    ### annotate leafs
    for name in aa.get_leaf_names():
        if name in anno_list:
            tree_str = tree_str.replace(name, name+'{Foreground}')
    ### annotate internal nodes
    tree_str = cali_inter_nodes(tree_str)
        
    return tree_str

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Annotate tree with given leaf names and their ancestors')

    #### annotate relax tree
    parser.add_argument('--input_tree_path')
    parser.add_argument('--output_tree_path')
    parser.add_argument('--annotation_file_path', help='One name per line')

    args = parser.parse_args()

    with open(args.annotation_file_path) as f:
        anno_list = [i.strip() for i in f.readlines() if not i.strip()=='']

    with open(args.input_tree_path) as f:
        aa = newick.load(f)[0]
    
    tree_str = annotate_tree(aa, anno_list)
    with open(output_tree_path,'w') as f:
        f.write(tree_str)
   
        
        