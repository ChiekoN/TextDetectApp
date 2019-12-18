from collections import defaultdict

item_list = [
    {
        'id': 1,
        'name': u'VASSE VIRGIN Margaret River',
        'keywords': u'VASSE,VIRGIN,Margaret,River',
        'done': False
    },
    {
        'id': 2,
        'name': u'Knorr Liquid Seasoning Original Flavor',
        'keywords': u'Knorr,LIQUID,SEASONING,ORIGINAL,FLAVOR',
        'done': False
    },
    {
        'id': 3,
        'name':u'Nerada Organics Green Tea 50 Tea Bags',
        'keywords': u'Nerada,Organics,Green,Tea,Pure,Organic,50,Tea,Cup,Bags',
        'done': False
    },
    {
        'id': 4,
        'name':u'Nerada Organics Original Tea 50 Tea Bags',
        'keywords': u'Nerada,Organics,Original,Tea,Pure,Organic,50,Tea,Cup,Bags,GREEN,TEA',
        'done': False
    },
    {
        'id': 5,
        'name': u'VASSE VIRGIN GINGER LIP BALM',
        'keywords': u'VASSE,VIRGIN,Margaret,River,GINGER,LIP,BALM',
        'done': False
    },
    {
        'id': 6,
        'name': u'CASIO Electric dictionary EX-word',
        'keywords': u'CASIO,EX-word,EX,word',
        'done': False
    },
    {
        'id': 7,
        'name':u'Olive Oil Australia',
        'keywords': u'OLIVE,OIL,AUSTRALIA',
        'done': False
    },
    {
        'id': 8,
        'name':u'Australian Lake Salt',
        'keywords': u'Lake,Salt,Western,Australia',
        'done': False
    }

]


def search_items(word_list):
    if len(word_list) == 0:
        return []

    found_list = defaultdict(int)
    for word_dic in word_list:
        word = word_dic['text']
        #print("word = {}".format(word))
        for item in item_list:
            if word in item['keywords'].split(','):
                found_list[item['id']] += 1
    
    print("found_list = {}".format(found_list))
    found_sortedid = sorted(found_list, key=found_list.get, reverse=True)
    found_item_list = []
    for i in found_sortedid:
        for item in item_list:
            if item['id'] == i:
                found_item_list.append(item)

    #return item_list # Mock result
    return found_item_list

