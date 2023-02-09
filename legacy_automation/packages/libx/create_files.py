"""
====================
Utility to generate files on the fly
====================

"""
class Creator:
    def create_text_file(self,list):
        url_file='url_file.txt'
        fp=open(url_file,'w')
        for i in list:
            # logging.warning(i)
            i=str(i)+'\n'
            fp.write(i)
        fp.close()    