
from tc_c2pa_py.jumbf_boxes.super_box import SuperBox
from tc_c2pa_py.utils.assertion_schemas import C2PA_AssertionTypes
from tc_c2pa_py.utils.content_types import c2pa_content_types



class AssertionStore(SuperBox):

    def __init__(self, assertions=None):
        self.assertions = [] if assertions == None else assertions
        super().__init__(content_type=c2pa_content_types['assertions'], label='c2pa.assertions', content_boxes=self.assertions)
        
    
    def get_assertions(self):
        return self.assertions
    
    
    def set_hash_data_length(self, length):
        for assertion_id in range(len(self.assertions)):
            if self.assertions[assertion_id].type == C2PA_AssertionTypes.data_hash:
                self.assertions[assertion_id].set_hash_data_length(length)
        
        super().__init__(content_type=c2pa_content_types['assertions'], label='c2pa.assertions', content_boxes=self.assertions)
