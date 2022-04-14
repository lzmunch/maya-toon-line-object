# credit: https://www.reddit.com/r/Maya/comments/agogg2/how_to_reorder_node_hierarchy_in_the_outliner/

import pymel.core as pm
import re

def convert_text_to_int(text):
    return int(text) if text.isdigit() else text

def natural_keys(pynode, case_sensitive=False):
    '''
    grabbed from: https://stackoverflow.com/a/5967539
    sorts list like     ["1", "2", "3", "10", "20", "30"]
    instead of standard ["1", "10", "2", "20", "3", "30"]
    '''
    if case_sensitive:
        return [convert_text_to_int(c) for c in re.split('(\d+)', pynode.nodeName())]
    else:
        return [convert_text_to_int(c) for c in re.split('(\d+)', pynode.nodeName().lower())]


def sort_children(item=None, entire_hierarchy=True, case_sensitive=False, natural_number_sort=True):
    """
    Gets children of item and sorts them by alphabetical order
    
    param: entire_hierarchy, determines whether to go through all the children and childrens children
    param: case_sensitive, whether to sort the items with case or not
    """
    
    item_children = item.getChildren(type="transform")
    if not item_children:
        return
    
    
    # set "entire_hierarchy" to False to skip this
    if entire_hierarchy:
        for child_item in item_children:
            sort_children(item=child_item, entire_hierarchy=entire_hierarchy, case_sensitive=case_sensitive, natural_number_sort=natural_number_sort)
    
    
    # Sorting methods
    sort_method = None
    if natural_number_sort:
        sort_method = lambda s: (natural_keys(s, case_sensitive=case_sensitive)) # run the natural number sort with whatever case sensitivity is specified
        
    elif case_sensitive is False:
        sort_method = lambda s: (s.nodeName().lower()) # otherwise just standard case-insensitive
        
    item_children.sort(key=sort_method)
    
    
    # the actual reorder command
    for sorted_item in item_children:
        pm.reorder(sorted_item, back=True)


def sort_selected_children(**kwargs):
    for top_node in pm.selected():
        sort_children(top_node, **kwargs)


class SortTool():
    def __init__(self):
        
        window_title = "Sort Tool"
        window_internal_name = window_title.replace(" ", "_")
        
        if pm.window(window_internal_name, exists=True):
        	pm.deleteUI(window_internal_name)
        
        with pm.window(window_internal_name, title=window_title) as win:
            with pm.horizontalLayout():
                with pm.verticalLayout():
                    self.CHK_entire_hierarchy = pm.checkBox("Entire Hierarchy", value=True)
                    self.CHK_natural_number_sort = pm.checkBox("Natural Number Sort", value=True)
                    self.CHK_case_sensitive = pm.checkBox("Case Sensitive", value=False)
                    
                pm.button("Sort", command=self.launch_command)
                
    
    def launch_command(self, *args):
        kwargs = {}
        kwargs["entire_hierarchy"] = self.CHK_entire_hierarchy.getValue()
        kwargs["natural_number_sort"] = self.CHK_natural_number_sort.getValue()
        kwargs["case_sensitive"] = self.CHK_case_sensitive.getValue()
        
        sort_selected_children(**kwargs)
        
        
if __name__ == "__main__":
    win = SortTool()