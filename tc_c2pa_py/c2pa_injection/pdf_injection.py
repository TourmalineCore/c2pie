
class PdfStreamObj():
    
    def __init__(self, payload_length: int, obj_num: str):
        self.payload_length_ = payload_length
        self.obj_num_ = obj_num
        self.header_ = self.create_header()
        self.footer_ = self.create_footer()


    def create_header(self):
        header = b''
        header += self.obj_num_.encode('utf-8')
        header += ' 0 obj\r'.encode('utf-8')
        header += '<</DL '.encode('utf-8')
        header += str(self.payload_length_).encode('utf-8')
        header += "/Length ".encode('utf-8')
        header += str(self.payload_length_).encode('utf-8')
        header += '>>'.encode('utf-8')
        header += 'stream'.encode('utf-8')
        header += '\r\n'.encode('utf-8')
        
        return header
    
    
    def get_header_len(self):
        return len(self.header_)
    

    def create_footer(self):
        footer = b''
        footer += '\r'.encode('utf-8')
        footer += 'endstream\r'.encode('utf-8')
        footer += 'endobj\r'.encode('utf-8')

        return footer
    
    def get_footer_len(self):
        return len(self.footer_)

    
    def serialize(self, payload):
        serialized_data = b''

        serialized_data += self.header_
        serialized_data += payload
        serialized_data += self.footer_

        return serialized_data

