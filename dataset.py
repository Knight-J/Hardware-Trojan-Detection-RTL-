import re

test_mode = 0  # 0:2轮 1:10轮

# **************************************neg**************************************
data_neg = {}
for node in range(21):
    node += 1

    path = 'database\\round2\\' + str(node) + '_neg.txt'
    # print(path)
    if test_mode == 0:
        fp = open(path, 'r')
    elif test_mode == 1:
        fp = open(path, 'r')
    data0 = fp.read()
    l = []
    data_neg[node] = []
    for item in data0.split('\n'):
        if item == '':
            continue
        else:
            #print('item:', item)
            item = item.lstrip('[')
            item = item.rstrip(']')
            #print('new item:', item)
            for a in re.split(',', item):
                l.append(float(a))
            #print('l:   ', l)

            data_neg[node].append(l)
            l = []
    fp.close()

# **************************************pos**************************************
data_pos = {}
for node in range(21):
    node += 1

    path = 'database\\round2\\' + str(node) + '_pos.txt'
    # print(path)
    if test_mode == 0:
        fp = open(path, 'r')
    elif test_mode == 1:
        fp = open(path, 'r')
    data0 = fp.read()
    l = []
    data_pos[node] = []
    for item in data0.split('\n'):
        if item == '':
            continue
        else:
            #print('item:', item)
            item = item.lstrip('[')
            item = item.rstrip(']')
            #print('new item:', item)
            for a in re.split(',', item):
                l.append(float(a))
            #print('l:   ', l)

            data_pos[node].append(l)
            l = []
    fp.close()


# print('data_neg:%s' % data_neg)
# print('data_pos:%s' % data_pos)
count_n = 0
count_p = 0
for items in data_neg.keys():
    # print(len(data_neg[items]))
    count_n += len(data_neg[items])
print(count_n)
for items in data_pos.keys():
    # print(len(data_pos[items]))
    count_p += len(data_pos[items])
print(count_p)

