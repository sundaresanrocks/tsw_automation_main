import datetime
#import lib.mongowrap
# from lib.mongowrap import MongoWrap
# from datetime import date, timedelta

seen_first = first_seen = datetime.date(2010,10,10)
seen_last = first_seen
 
class TestDataBP:

    @staticmethod
    def test01_expected(url):
        values = {'*://BUILDTEST1.COM' : {
        "_id" : "0x5eb714a3d186edc9cdba4198",
        #"categorization_history" : [
        #        {
        #                #"_id" : "10003",
        #                #"date" : "201305211450",
        #                "category" : "ms"
        #        }
        #],
        "category" : "ms",
        "domain" : "BUILDTEST1.COM",
        "reputation" : 127,
        #"reputation_history" : [
        #        {
        #                #"_id" : "10003",
        #                #"date" : "201305211450",
        #                "reputation" : 127
        #        }
        #],
        "url" : "*://BUILDTEST1.COM"
        },
        "HTTPS://BUILDTEST1.COM" : {
        "_id" : "0xbbc237174bc2db70385aeae1",
        #"categorization_history" : [
        #        {
        #                #"_id" : "10003",
        #                #"date" : "201305211450",
        #                "category" : "ms"
        #        }
        #],
        "category" : "ms",
        "domain" : "BUILDTEST1.COM",
        "reputation" : 127,
        #"reputation_history" : [
        #        {
        #                #"_id" : "10003",
        #                #"date" : "201305211450",
        #                "reputation" : 127
        #        }
        #],
        "url" : "HTTPS://BUILDTEST1.COM"
        },
        "*://BUILDTEST1.COM/1.html" : {
        "_id" : "0xf584968ef46759e00c000445",
        #"categorization_history" : [
        #        {
        #                #"_id" : "10003",
        #                #"date" : "201305211450",
        #                "category" : "ms"
        #        }
        #],
        "category" : "ms",
        "domain" : "BUILDTEST1.COM",
        "reputation" : 127,
        #"reputation_history" : [
        #        {
        #                #"_id" : "10003",
        #                #"date" : "201305211450",
        #                "reputation" : 127
        #        }
        #],
        "url" : "*://BUILDTEST1.COM/1.html"
        }}
        return values[url]
    
    
    @staticmethod
    def test02_expected(url):

        values = {'*://BUILDTEST1.COM' : {
        "_id" : "0x5eb714a3d186edc9cdba4198",
        "category" : "ms",
        "domain" : "BUILDTEST1.COM",
        "url" : "*://BUILDTEST1.COM"
        },
        "HTTPS://BUILDTEST1.COM" : {
        "_id" : "0xbbc237174bc2db70385aeae1",
        "category" : "ms",
        "domain" : "BUILDTEST1.COM",
        "url" : "HTTPS://BUILDTEST1.COM"
        },
        "*://BUILDTEST1.COM/1.html" : {
        "_id" : "0xf584968ef46759e00c000445",
        "category" : "ms",
        "domain" : "BUILDTEST1.COM",
        "url" : "*://BUILDTEST1.COM/1.html"
        }}
        return values[url]
            
    
    
class TestDataBPFunctional:

    @staticmethod
    def test01_expected(url):
        values = {'*://BUILDTEST1.COM' : {
        "_id" : "0x5eb714a3d186edc9cdba4198",
        "category" : "ms",
        "domain" : "BUILDTEST1.COM",
        "reputation" : 127,
        "url" : "*://BUILDTEST1.COM"
        },
        "HTTPS://BUILDTEST1.COM" : {
        "_id" : "0xbbc237174bc2db70385aeae1",
        "category" : "ms",
        "domain" : "BUILDTEST1.COM",
        "reputation" : 127,
        "url" : "HTTPS://BUILDTEST1.COM"
        },
        "*://BUILDTEST1.COM/1.html" : {
        "_id" : "0xf584968ef46759e00c000445",
        "category" : "ms",
        "domain" : "BUILDTEST1.COM",
        "reputation" : 127,
        "url" : "*://BUILDTEST1.COM/1.html"
        }}
        return values[url]
    
    
    @staticmethod
    def test02_expected(url):
        values = {'*://TECNICASMENTALES.COM/el-cuadrante-de-flujo-de-dinero.htm' :
        {
        "_id" : "0xffd9418817485932e6e1f2c5",
        "category" : "ms",
        "domain" : "TECNICASMENTALES.COM",
        "url" : "*://TECNICASMENTALES.COM/el-cuadrante-de-flujo-de-dinero.htm"
        },
        "*://0-PORNOGRAPHY.COM" : {
        "_id" : "0x320cf10bd38e5e48daeedbfd",
        "category" : "uncat",
        "domain" : "0-PORNOGRAPHY.COM",
        "url" : "*://0-PORNOGRAPHY.COM"
        }}
      

        return values[url]
    
    @staticmethod
    def test03_expected(url):
        values = {'*://96.47.69.60?&gid&oid&aid={adcenterid}&yid={yahooid}':
        {
        "_id" : "0xab45d0bade10082b14246111",
        "url" : "*://96.47.69.60?&gid&oid&aid={adcenterid}&yid={yahooid}",
        "domain" : "96.47.69.60",
        "category" : "ms",
        "reputation" : 0
        }}

        return values[url]

    @staticmethod
    def test04_expected(url):
        values = {'*://CHARIOTS-OF-FIRE.COM':
        {
        "_id" : "0x78a5bfa98c9b654a7be15e87",
        "url" : "*://CHARIOTS-OF-FIRE.COM",
        "domain" : "CHARIOTS-OF-FIRE.COM",
        "reputation" : 18
        
        },
        "*://CASHMEL.COM" :{
        "_id" : "0x78a65dcbfe57d481792522e4",
        "url" : "*://CASHMEL.COM",
        "domain" : "CASHMEL.COM",
        "reputation" : 16
          
        },
        "*://DEKASTAAN.NL":{
        "_id" : "0x78a6d4a06ec322018c86ccab",
        "url" : "*://DEKASTAAN.NL",
        "domain" : "DEKASTAAN.NL",
        "reputation" : 16
        }}

        return values[url]
            
       
    @staticmethod
    def test05_expected(url):
        values = {'*://199.59.149.230/McAfee':
        {
        "_id" : "0x63117fd99b56f9d5cd678279",
        "category" : "bl  bu  hw  sn  tf",
        "domain" : "199.59.149.230",
        "reputation" : 0,
        "url" : "*://199.59.149.230/McAfee"
            
        },
        "*://199.59.150.7/McAfee":{
        "_id" : "0x3c0fbd354f5d766558b64369",
        "url" : "*://199.59.150.7/McAfee",
        "domain" : "199.59.150.7",
        "category" : "bl  bu  hw  sn  tf",
        "reputation" : 0
        }}
                         
            
        return values[url]
                      
    @staticmethod
    def test06_expected(url):
        values = { '*://HANDRITE.COM':
        {
        "_id" : "0x4b05a236de28fe825f0b9f08",
        "category" : "uncat",
        "domain" : "HANDRITE.COM",
        "reputation" : 0,
        "url" : "*://HANDRITE.COM"
        },

        "*://TAP2.NL" :{
        "_id" : "0x38b4b527eeaa67a906f377d0",
        "category" : "uncat",
        "domain" : "TAP2.NL",
        "reputation" : 0,
        "url" : "*://TAP2.NL"
        },

        "*://POTOPON.COM" :{
        "_id" : "0x23be7543c9986b7fc38b1035",
        "category" : "uncat",
        "domain" : "POTOPON.COM",
        "reputation" : 0,
        "url" : "*://POTOPON.COM"
        }}              

        return values[url]
            

    @staticmethod
    def test07_expected(url):
        values = {'FTP://AGEOCITIES.COM':
        {
        "_id" : "0xd4646a7764906cd4ba5eb64e",
        "category" : "sx",
        "domain" : "AGEOCITIES.COM",
        "reputation" : 0,
        "url" : "FTP://AGEOCITIES.COM"
        },

        "FTP://PAPTEST8.COM/path":
        {
        "_id" : "0xf33f6e43c8fdc0c79a1485b6",
        "url" : "FTP://PAPTEST8.COM/path",
        "domain" : "PAPTEST8.COM",
        "category" : "sx",
        "reputation" : 0
        }}             
                      
        return values[url]

    @staticmethod
    def test08_expected(url): 
        values = { 'HTTPS://PAPTEST11.COM':
        {
        "_id" : "0x23d4c016a1c11bfc0acf5cb2",
        "category" : "tg",
        "domain" : "PAPTEST11.COM",
        "reputation" : 0,
        "url" : "HTTPS://PAPTEST11.COM"
        },

        "HTTPS://PAPTEST11.COM:8080":
        {
        "_id" : "0xc1aa9820069207ecc7fc55c0",
        "category" : "mb",
        "domain" : "PAPTEST11.COM",
        "reputation" : 0,
        "url" : "HTTPS://PAPTEST11.COM:8080"
        }}

        return values[url]

    @staticmethod
    def test09_expected(url): 
        values = { '*://200.55.198.67':
        {
        "_id" : "0x17dd427ecc7e4501067a94d5",
        "url" : "*://200.55.198.67",
        "domain" : "200.55.198.67",
        "reputation" : 16
        },
        "*://64.12.79.57/klcartao" :
        {
        "_id" : "0x17ec6c013585a0f5f24cb98e",
        "url" : "*://64.12.79.57/klcartao",
        "domain" : "64.12.79.57",
        "reputation" : 16

        },
        "*://212.219.56.133/sites/ftp.simtel.net" :
        {
        "_id" : "0x4abc7b543864822ee1569658",
        "url" : "*://212.219.56.133/sites/ftp.simtel.net",
        "domain" : "212.219.56.133",
        "reputation" : 16
        }
        }

        return values[url]



    @staticmethod
    def test10_expected(url): 
        values = { 'http://[3ffe:1900:4545:3:200:f8ff:fe21:67cf]:80/index.html':
        {
        "_id" : "0xa52496a9d2413dfec63cd925",
        "url" : "http://[3ffe:1900:4545:3:200:f8ff:fe21:67cf]:80/index.html",
        "domain" : "[3ffe:1900:4545:3:200:f8ff:fe21:67cf]",
        "category" : "ms",
        "reputation" : 0
        }
        }
        return values[url]



    @staticmethod
    def test11_expected(url): 
        values = { 'ftp://[3ffe:1900:4545:3:200:f8ff:fe21:67cf]:80/index.html' :
        {
        "_id" : "0x3e8fb003a48b11a006f2020a",
        "url" : "ftp://[3ffe:1900:4545:3:200:f8ff:fe21:67cf]:80/index.html",
        "domain" : "[3ffe:1900:4545:3:200:f8ff:fe21:67cf]",
        "category" : "ms",
        "reputation" : 0
        }
        }

        return values[url]


    @staticmethod
    def test12_expected(url): 
        values = { 'https://[3ffe:1900:4545:3:200:f8ff:fe21:67cf]:80/index.html' :

        {
        "_id" : "0xebe039398db3fc2a6fb78df6",
        "url" : "https://[3ffe:1900:4545:3:200:f8ff:fe21:67cf]:80/index.html",
        "domain" : "[3ffe:1900:4545:3:200:f8ff:fe21:67cf]",
        "category" : "ms",
        "reputation" : 0
        }
        }
        return values[url]



    @staticmethod
    def test13_expected_1(url): 
        values = { '*://BUILDTEST13.COM':
        {
        "_id" : "0x30f7d0f4eb6e4705361ad278",
        "category" : "ms",
        "domain" : "BUILDTEST13.COM",
        "reputation" : 0,
        "url" : "*://BUILDTEST13.COM"
        }}
        return values[url]
    
    @staticmethod
    def test13_expected_2(url): 
        values = { '*://BUILDTEST13.COM':
        {
        "_id" : "0x30f7d0f4eb6e4705361ad278",
        "category" : "delete",
        "domain" : "BUILDTEST13.COM",
        "reputation" : 0,
        "url" : "*://BUILDTEST13.COM"
        }}
        return values[url]
    
    @staticmethod
    def test14_expected_1(url): 
        values = { '*://BUILDTEST14.COM':
        {
        "_id" : "0x3d8342513f05be0c3d0361f7",
        "domain" : "BUILDTEST14.COM",
        "reputation" : 30,
        "url" : "*://BUILDTEST14.COM"
        }}
        return values[url]

    @staticmethod
    def test14_expected_2(url): 
        values = { '*://BUILDTEST14.COM':
        {
        "_id" : "0x3d8342513f05be0c3d0361f7",
        "domain" : "BUILDTEST14.COM",
        "reputation" : 127,
        "url" : "*://BUILDTEST14.COM"
        }}
        return values[url]
    
    
    
    