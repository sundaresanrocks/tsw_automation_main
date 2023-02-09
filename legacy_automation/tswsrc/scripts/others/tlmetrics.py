#!/usr/bin/python
"""
=======================
Testlink Metrics module
=======================

Function to find the automation metrics for test link project

"""
################################################################################
################################################################################
#                                                                              #
# Settings                                                                     #
#                                                                              #
################################################################################
################################################################################

TESTLINK_HOST = '172.19.216.198'
TESTLINK_USER = 'root'
TESTLINK_PASS = '1qazse4'
TESTLINK_DB   = 'testlink193'


# Imports 
                                                                     #
import sys
import logging
import MySQLdb
from collections import deque

################################################################################
################################################################################
#                                                                              #
# MySql wrapper                                                                #
#                                                                              #
################################################################################
################################################################################
class MySqlHelper:
    """
    Helper class for mySql handling.\n
    Creates a connection. \n
    Example:
        >>>
        sqlobj = MySqlHelper(host="localhost", user="usera", passwd="pass", db="dbname")
    """
    def __init__(self, **kwarg):
        """Creates a connection."""
        try:
            self.dbmod = __import__('MySQLdb')
            self.db = self.dbmod.connect(**kwarg)
            self.dbh = self.db.cursor()
        except:
            msg = "Unable to open/connect database"
            logging.error(msg)
            raise Exception(msg)

    def __del__(self):
        try:
            self.db.commit()
            self.dbh.close()
            self.db.close()
        except:
            msg = "Unable to commit/close database"
            logging.error(msg)
            raise Exception(msg)

    def query(self, sql):
        """
        Executes a SQL query.
        In case of SELECT query, a tuple of lists is returned.

        >>>
            res_sql = sqlobj.query("select * from builds")
            if res_sql[1][0] == (): #check for empty
                print "No Entry in db, can safely insert"
        """
        try:
            self.dbh.execute(sql)
        except Exception as err :
            msg = 'Unable to query\nSQL: %s\nError Msg: %s ' \
                % (sql,str(err.args[0]))
            logging.error(msg)
            raise Exception(msg)
                
        data  = self.dbh.fetchall()
        desc = self.dbh.description
        if desc is None:
            return ((),((),()))

        header = []
        n = len(desc)
        for i in range(n):
            header.append(desc[i][0])
        if len(data) == 0:
            return header, tuple([ () for i in range(n) ])

        tmp = list()
        for i in range(n):
            tmp.append([])

        for row in data:
            for i in range(n) :
                tmp[i].append(row[i])

        return header, tuple(tmp)

    def lastrowid(self):
        """Returns the last inserted id."""
        return self.dbh.lastrowid

    def make_insert(self, arg):
        """
        Converts a dict into an INSERT type syntax, dealing with the types.

        * If a dictionary is provided, returns: SET `key`=value, ...

        * If a list of dictionnaries is given, the long INSERT syntax is used(`key`, ...) VALUES (value, ...), (...), ...
            Here, the list of fields is read from the keys of the first row.
        """
        if type(arg)==type(dict()):
            fields = "SET "+", ".join(["`%s`=%s" % (k, self.str(v)) for k, v in list(arg.items())])
        elif type(arg)==type(list()):
            n = len(list(arg[0].keys()))
            fields  = "("+", ".join(["`%s`" % k for k in list(arg[0].keys())])+")"
            fields += " VALUES "
            L = list()
            for i, r in enumerate(arg):
                if len(list(r.values())) != n:
                    raise ValueError('On row %d, %d arguments found, %d expected.' % (i, len(list(r.values())), n))
                L.append("("+", ".join([self.str(v) for v in list(r.values())])+")")

            fields += ", ".join(L)
        else:
            raise TypeError('MySqlHelper.make_insert() argument should be dict or list (%s given).' % type(arg))
                
        return fields

    def str(self, v):
        """Converts, escapes a Python variable into SQL string to insert it in a query."""
        if v is None:
            return "NULL"
        elif type(v)==type(str()):
            return "\""+self.db.escape_string(v)+"\""
        else:
            return str(v)


################################################################################
################################################################################
#                                                                              #
# Function to calculate metrics                                                #
#                                                                              #
################################################################################
################################################################################
def get_testlink_automation_metrics(project_prefix, 
                                    sql_host, sql_user, sql_pass, sql_db):
    """
    :param project_prefix: Prefix for the project from test link. Must be List
    Example: [mcst, gti]
    :param sql_host: host/ip of sql db machine
    :param sql_user: sql user name
    :param sql_pass: sql password
    :param sql_db: sql database name for testlink

    Returns a tuple of values (total, automated, manual)
    """

    def get_project_id(_prefix):
        """Returns the project id based on the project prefix"""
        _qry = "select id from testprojects where prefix='%s'" % _prefix
        qobj = sqlobj.query(_qry)
        if len(qobj[1][0]) != 1:
            raise Exception('Unable to get unique project id')
        return qobj[1][0][0]

    def get_stats_top_level_suites(parent_id):
        """
        List of metrics for the top level suites
        Raises NotImplementedError
        """
        raise NotImplementedError('get_stats_top_level_suites() - parent_id'\
            % parent_id)

    def get_metrics_for_parent(parent_id):
        """
        Returns a tuple of values (total, automated, manual)
        """
        tc_ver_list = []
        ret_var = {'leaf_nodes':[],
                   'node_type_2':{},
                   'node_type_3':{},
                   'node_type_4':{},
                   'all_nodes':[],
                  }
        suite_queue = deque()
        suite_queue.append(parent_id)

        _qry = "select id nid, parent_id pid, node_type_id tid from nodes_hierarchy order by parent_id"
        qobj = sqlobj.query(_qry)
        if len(qobj[1][0]) <= 0:
            raise Exception('Unable to get node_hierarcy information')

        nlist = qobj[1][qobj[0].index('nid')]
        plist = qobj[1][qobj[0].index('pid')]
        tlist = qobj[1][qobj[0].index('tid')]

        #map a table and find inverse map -> child list
        [ret_var['node_type_' + str(tlist[_node])].update({nlist[_node]: plist[_node]}) for _node in range(len(nlist)) if tlist[_node] in (2, 3, 4)]
        ret_var['node_tree'] = {}
        for _key, _val in list(ret_var['node_type_2'].items()):
            ret_var['node_tree'][_val] = ret_var['node_tree'].get(_val, [])
            ret_var['node_tree'][_val].append(_key)


        while len(suite_queue) > 0:
            cur_node = suite_queue.popleft()
            ret_var['all_nodes'].append(cur_node)
            if cur_node not in ret_var['node_tree']:
                ret_var['leaf_nodes'].append(cur_node)
            else:
                suite_queue.extend(ret_var['node_tree'][cur_node])
            #print suite_queue

        xx = {}
        yy = []
        for val in ret_var['all_nodes']:
            #print val
            _qry = "select id nid from nodes_hierarchy where parent_id in (select id from nodes_hierarchy where parent_id = %s and node_type_id=3)" % val
            qobj = sqlobj.query(_qry)
            if (len(qobj[1][0])) != 0:
                yy.extend(qobj[1][0])
        _qry = 'select count(distinct(tc_external_id)) from tcversions where id in ( %s )' % ','.join(str(x) for x in yy)
        qobj = sqlobj.query(_qry)
#        print 'Total', qobj[1][0]
        _total = qobj[1][0]

        qobj = sqlobj.query(_qry + ' and execution_type=2')
#        print 'Automated', qobj[1][0]
        _automated = qobj[1][0]

        qobj = sqlobj.query(_qry + ' and execution_type=1')
        _manual = qobj[1][0]
#        print 'Manual', qobj[1][0]

        _qry = 'select tc_external_id, count(tc_external_id) c from tcversions where id in (%s) group by tc_external_id having c>1 ' % ','.join(str(x) for x in yy)
        qobj = sqlobj.query(_qry)
        print(('Tests with more than one active version(Conflicts):', qobj[1][0]))
        return (_total[0], _automated[0], _manual[0])
    #with conflicts
#        return (_total[0], _automated[0], _manual[0], tc_ver_list)
    #only conflict list
#        return tc_ver_list


    sqlobj = MySqlHelper(host=sql_host,
                         user=sql_user,
                         passwd=sql_pass,
                         db=sql_db)
    if type(project_prefix) != type([]):
        raise TypeError('project_prefix must be a list! found %s' % \
                                                    type(project_prefix))
    results = {}
    aggregate = [0, 0, 0]
    for prefix in project_prefix:
        _project_id = get_project_id(prefix)
        results[prefix] = get_metrics_for_parent(_project_id)
        aggregate[0] += results[prefix][0]
        aggregate[1] += results[prefix][1]
        aggregate[2] += results[prefix][2]
    return results, aggregate


def main():
    """Main function"""
    if len(sys.argv) == 0:
        print('Usage: python tlmetrics.py prefix1, prefix2, prefixn')
        sys.exit(100)

    prefix_list = []
    [prefix_list.append(prefix) for prefix in sys.argv[1:]]

    prefix_list = ['GTICloud', 'SUS']     #from testlink

    results, aggregate = get_testlink_automation_metrics(prefix_list, 
                                         TESTLINK_HOST, TESTLINK_USER,
                                         TESTLINK_PASS, TESTLINK_DB)

    for prefix, value in list(results.items()):
        print(('%s: (Total, Automated, Manual) = (%s, %s, %s)' % (prefix, 
                                                value[0],value[1],value[0]-value[1])))
    print(('Aggregate: (Total, Automated, Manual) = (%s, %s, %s)' % (
                                aggregate[0], aggregate[1], aggregate[0]-aggregate[1])))
        
if __name__ == "__main__":
    main()
