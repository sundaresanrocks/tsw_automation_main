"""
==============================
SQL Wrapper class
==============================
Sample Script
>>>
    from libx.sqlwrap import mySqlHelper
    sqlobj=mySqlHelper(host=con.DB.host,user=con.DB.user,passwd=con.DB.passwd,db=con.DB.db)

    res_sql = sqlobj.query("select * from builds where engine='" + str(engine) + 
                "' and arch='" + str(arch) + "' and build='" + str(build) + 
                "' and package='" + str(pkg) + "'"
                 )
    dict={
            'engine': str(engine),
            'arch': str(arch),
            'build': str(build),
            'package':str(pkg),
            'file_name': str(fs_file),
            'md5': str(rmd5),
            'unc_path':str(unc_path + fs_file).replace("\\", "\\\\"),
            'http_url': str(fs_http_path),
            'copied_from_location':str(src_url)
                }
    if res_sql[1][0] == ():     #check for null
        print "No Entry in db, can safely insert"

        try:
            sqlobj.query ('insert into builds ' + sqlobj.make_insert(dict))
            pass
        except Exception,err:
            print err
    else:
        print "Entry already exists. Update?"
"""

import logging
import pymysql
pymysql.install_as_MySQLdb()


class mySqlHelper:
    """
    Helper class for mySql handling.\n
    Creates a connection. \n
    Example:
        >>>
        sqlobj = mySqlHelper(host="localhost", user="usera", passwd="pass", db="dbname")
    """
    def __init__(self, **kwarg):
        """Creates a connection."""
        try:
            self.db = pymysql.connect(**kwarg)
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
            msg = 'Unable to query\nSQL: %s\nError Msg: %s '%(sql,str(err))
            logging.error(msg)
            raise Exception(msg)
                
        data  = self.dbh.fetchall()
        desc = self.dbh.description
        if desc is None:
            return ((),((),()))

        header=[]
        n = len(desc)
        for i in range(n):
            header.append(desc[i][0])
        if len(data)==0:
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
            raise TypeError('mySqlHelper.make_insert() argument should be dict or list (%s given).' % type(arg))
                
        return fields

    def str(self, v):
        """Converts, escapes a Python variable into SQL string to insert it in a query."""
        if v is None:
            return "NULL"
        elif type(v)==type(str()):
            return "\""+self.db.escape_string(v)+"\""
        else:
            return str(v)
