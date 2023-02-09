from libx.utils import DictDiffer
import logging

class MongoDictDiffer(DictDiffer):

    """
    Calculate the difference between two dictionaries 
    (with partial match enabled for dicts inside lists):

    
    1) partial match (deep check)
    2) changed (deep check)
    """

    def changed_deepchk(self):
        """returns items changed in current dict, if the items are dict, do a partial match inturn"""
        
        ch_list = []  # Change list - used for storing differing keys
        logging.debug("self.intersect ...")
        logging.debug(self.intersect)
        for o in self.intersect:
           
            #logging.debug("checking value of - %s"% o)
            #logging.debug("expected value - ")
            #logging.debug(self.current_dict[o])
            #logging.debug("actual value - ")
            #logging.debug(self.past_dict[o])

             #If the value is not an iterable (list or dict) 
             #   --> do an apple to apple comparison
            if ((not isinstance(self.current_dict[o], list)) and (not isinstance(self.current_dict[o], dict))):
                if self.past_dict[o] != self.current_dict[o]:
                    
                    #populate change list with the differing keys
                    ch_list.extend(o)

            elif (isinstance(self.current_dict[o], list)):
                #If the value is a list (of dicts ) 
                #(Assumption --> if value is a list, it is a list of dicts
                # This is true currently. 
                # But,this should be updated as and when required
                
                clist = self.current_dict[o]
                plist = self.past_dict[o]

                # clist - list from expected data
                # plist - list from mongo db document


                #For debugging
                #logging.debug("clist ...")
                #logging.debug(clist)
                #logging.debug("plist ...")
                #logging.debug(plist)

                for each_cdict in clist:
                #{
                    cid = each_cdict['_id']
                    idexists = 0
                    for each_pdict in plist:
                    #{
                        ch_sub_list = []
                        pid =  each_pdict['_id']

                        #Basically, we find dicts to compared based on "_id" and do a partial match between them


                        if cid == pid:
                        #{
                            idexists = 1
                            ch_sub = []

                            #Compare two dicts using partial_match 
                            subdiff = DictDiffer(each_cdict,each_pdict)

                            #If partial match fails, populate the differing keys to change list
                            if subdiff.partial_match() is False:
                                #[ch_sub for ch_sub in subdiff.intersect if subdiff.past_dict[o] != subdiff.current_dict[o]]
                                #ch_list.extend(ch_sub)
                                ch_list.extend(o)

                            #Break and go to next dict in the clist
                            break
                        #}
                        else:
                            #Continue to next dict in the plist
                            continue
                    #}


                    #If the dict in expected result doesnot exists in the actual result
                    #       -> put it to change list
                    if idexists == 0:
                        ch_list.extend(o)



                    #Before going to next dict in the list
                    #If change list has a key
                    if ch_list:
                        #This means the partial match (for the list of dicts) has failed
                        #no need to go further processing the list of dicts
                        #hence, break 

                        break
                    
                 
                #}


        return set(ch_list)

    def partial_match_deep_chk(self):
        """Returns True if subset match exists
        If the items are dictionaries, this will check using a partial match inturn"""
        if (len(self.added()) == 0) and (len(self.changed_deepchk()) == 0):
            return True
        return False