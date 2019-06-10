import re

count = 0
count1 = 0
base_count = 0
final_count = 0
if_lay = 0
parallel_lay = 0
case_lay = 0
input_name = []
output_name = []
fp = open("top_simple.txt", "r")
content = fp.read()
exam_name = ''  #例化的模块名
top_name = ''  #模块名
top_port = {}  #模块的顶层端口
inst_list = {}  #每个模块的例化模块
inst_port = {}
top_signal = {}
#port_replace = {} #例化模块里需要替换的信号，key为原始信号 value为例化模块信号


class Node(object):
    count_class = 0

    def __init__(self, top='', name=0, add_minus=0, or_and=0, xor=0, shift=0, cat=0, num=0, ifc=0, cac=0, max_op=0, driven=[], driving=[]):
        self.top = top
        self.name = name
        self.add_minus = add_minus
        self.or_and = or_and
        self.xor = xor
        self.shift = shift
        self.cat = cat
        self.num = num
        self.ifc = ifc
        self.cac = cac
        self.max_op = max_op
        self.driven = driven
        self.driving = driving
        Node.count_class += 1


class Node1(object):
    count_class1 = 0

    def __init__(self, top='', name=0, add_minus=0, or_and=0, xor=0, shift=0, cat=0, num=0, ifc=0, cac=0, max_op=0, driven=[], driving=[]):
        self.top = top
        self.name = name
        self.add_minus = add_minus
        self.or_and = or_and
        self.xor = xor
        self.shift = shift
        self.cat = cat
        self.num = num
        self.ifc = ifc
        self.cac = cac
        self.max_op = max_op
        self.driven = driven
        self.driving = driving
        Node1.count_class1 += 1


def form(arg1):
    arg1 = arg1.strip()
    arg1 = arg1[:-1]
    return arg1


def analysis(arg1, arg2):
    '''
    print('begin')
    print('0', arg1.driving)
    print('0', arg1.driven)
    arg2 = arg2.strip()
    arg2 = arg2[:-1]
    '''
    arg1.top = top_name
    arg1.name = count
    arg1.add_minus += arg2.count('+') + arg2.count('-')
    arg1.or_and += arg2.count('&') + arg2.count('|')
    arg1.xor += arg2.count('^')
    arg1.cat += len(re.findall('{.*?}', arg2))
    arg1.num += 1
    b = re.split('=', arg2)
    origin = re.split(' ', b[0])[1]  # assign等号左侧的信号
    origin = re.compile(origin)
    if len(re.findall(origin, arg2)) > 1 and len(re.findall('{.*?}', arg2)) > 0:
        arg1.shift += 1
    # max_op
    if (len(re.split(r'\=|\,|\+|\-|\^|\|', arg2)) - 1) > arg1.max_op:
        arg1.max_op = len(re.split(r'\=|\,|\+|\-|\^|\|', arg2)) - 1
    # signal
    if re.search('<=', arg2) is not None:  # 时序逻辑
        #print('时序')
        items = re.split(r'<=', arg2)
        for i in re.split(r',|\+|\-|\^|\|', items[0]):
            i = i.strip()
            if i[0] == '{' or i[0] == '(':
                i = i[1:]
            if i[-1] == '}' or i[-1] == ')':
                i = i[:-1]
            if re.search('\[', i):
                i = re.split('\[', i)[0]
            # print(items)
            if i not in arg1.driven:
                arg1.driven.append(i)
        for i in re.split(r',|\+|\-|\^|\|', items[1]):
            i = i.strip()
            if i[-1] == ';': #去掉最后的;
                i = i[:-1]
            if i[0] == '{' or i[0] == '(':
                i = i[1:]
            if i[-1] == '}' or i[-1] == ')':
                i = i[:-1]
            if re.search('\[', i):
                i = re.split('\[', i)[0]
            # print(items)
            if i not in arg1.driving:
                arg1.driving.append(i)
    else:  # 组合逻辑
        #print('组合')
        items = re.split(r'=', arg2)
        for i in re.split(r',|\+|\-|\^|\|', items[0]):
            i = i.strip()
            if i[0] == '{' or i[0] == '(':
                i = i[1:]
            if i[-1] == '}' or i[-1] == ')':
                i = i[:-1]
            if re.search('\[', i):
                i = re.split('\[', i)[0]
            # print(items)
            if i not in arg1.driven:
                arg1.driven.append(i)
        for i in re.split(r',|\+|\-|\^|\|', items[1]):
            i = i.strip()
            if i[-1] == ';': #去掉最后的;
                i = i[:-1]
            if i[0] == '{' or i[0] == '(':
                i = i[1:]
            if i[-1] == '}' or i[-1] == ')':
                i = i[:-1]
            if re.search('\[', i):
                i = re.split('\[', i)[0]
            # print(items)
            if i not in arg1.driving:
                arg1.driving.append(i)
    '''
    print('end')
    print('1', arg1.driving)
    print('1', arg1.driven)
    '''


def top_ports(arg1, agr2):
    for item6 in re.split('\n', arg1):
        item6 = item6.strip()
        #print('item6', item6)
        if (re.search('input', item6) is not None) or (re.search('output', item6) is not None):
            if item6[-1] == ',' or item6[-1] == ';':
                item6 = item6[:-1]
            if re.search(',', item6):  # print("一行多个端口")
                for item in re.split(',', item6):  #item 为一行里的一个信号
                    if re.search(' ', item): #一行里的第一个信号
                        if re.split(' ', item)[-1] not in agr2:
                            agr2.append(re.split(' ', item)[-1])
                    else:
                        if item not in agr2:
                            print('item:', item)
                            agr2.append(item)
            else:  # print("一行一个端口")
                if re.split(' ', item6)[-1] not in agr2:
                    agr2.append(re.split(' ', item6)[-1])


def find_module(data):
    iter = re.findall('module[\s\S]*?endmodule', data)
    return iter


def find_topname(data):
    string = data.strip()  #去掉首尾空格
    string = string[:-1]  #去掉最后的括号
    string = string.strip()
    name = re.split(' ', string)
    return name[1]


def find_inst_port(arg1, arg2):
    list_temp = []
    port_list = re.search('\([\s\S]*\)', arg1).group()
    port_list = re.sub('\(|\)', '', port_list)  # 得到例化模块的端口
    for item in re.split(',', port_list):
        item = item.strip()
        list_temp.append(item)
    arg2.append(list_temp)


'''
def func_port_replace(arg1, arg2, arg3):  #arg1为inst_port, arg2为top_port, arg3为port_replace
    for item in range(len(arg2)):
        if arg1[item] != arg2[item]:
            arg3[arg2[item]] = arg1[item]
'''


def func_port_replace(arg1, arg2):  #arg1为inst_port, arg2为top_port, arg3为port_replace
    arg3 = {}
    if len(arg2) != len(arg1):
        print('error input')
        print(len(arg1))
        print(len(arg2))
    for item in range(len(arg2)):
        if arg1[item] != arg2[item]:
            arg3[arg2[item]] = arg1[item]
    return arg3


def copy_attribute_update(arg1, arg2, arg3):  #arg1为新实例 arg2为老实例 arg3为端口替换表
    arg1.top = arg2.top
    arg1.name = count1
    arg1.add_minus = arg2.add_minus
    arg1.or_and = arg2.or_and
    arg1.xor = arg2.xor
    arg1.shift = arg2.shift
    arg1.cat = arg2.cat
    arg1.num = arg2.num
    arg1.ifc = arg2.ifc
    arg1.cac = arg2.cac
    arg1.max_op = arg2.max_op
    arg1.driving = arg2.driving[:]
    arg1.driven = arg2.driven[:]
    '''
    for item8 in arg2.driven:
        if item8 in arg3.keys():
            arg1.driven.append(arg3[item8])
        else:
            arg1.driven.append(item8)
    for item9 in arg2.driving:
        if item9 in arg3.keys():
            arg1.driving.append(arg3[item9])
        else:
            arg1.driving.append(item9)
    '''
    for memb1 in arg3.keys():
        comp = re.compile(memb1 + '\[\d+')
        for memb2 in range(len(arg1.driving)):
            if arg1.driving[memb2] == memb1:
                arg1.driving[memb2] = arg3[memb1]
            elif re.match(comp, arg1.driving[memb2]) is not None:
                arg1.driving[memb2] = re.sub(memb1, arg3[memb1], arg1.driving[memb2])
            else:
                continue
    for memb1 in arg3.keys():
        comp = re.compile(memb1 + '\[\d+')
        for memb2 in range(len(arg1.driven)):
            if arg1.driven[memb2] == memb1:
                arg1.driven[memb2] = arg3[memb1]
            elif re.match(comp, arg1.driven[memb2]) is not None:
                arg1.driven[memb2] = re.sub(memb1, arg3[memb1], arg1.driven[memb2])
            else:
                continue


def copy_attribute(arg1, arg2):  #arg1为新实例 arg2为老实例
    arg1.top = arg2.top
    arg1.name = count1
    arg1.add_minus = arg2.add_minus
    arg1.or_and = arg2.or_and
    arg1.xor = arg2.xor
    arg1.shift = arg2.shift
    arg1.cat = arg2.cat
    arg1.num = arg2.num
    arg1.ifc = arg2.ifc
    arg1.cac = arg2.cac
    arg1.max_op = arg2.max_op
    for item8 in arg2.driven:
        arg1.driven.append(item8)
    for item9 in arg2.driving:
        arg1.driving.append(item9)


def add_node_of_inst(module_name, replace): #当前模块的顶层名字;当前模块的port_replace
    global count1
    port_replace = {}
    for item9 in range(len(inst_list[module_name])):  # 该顶层有几个例化模块
        exam_name = inst_list[module_name][item9]
        update_port = inst_port[module_name][item9][:]  #更新例化模块的端口
        for item11 in replace.keys():
            comp = re.compile(item11 + '\[\d+')
            for item12 in range(len(update_port)):
                if update_port[item12] == item11:
                    update_port[item12] = replace[item11]
                elif re.match(comp, update_port[item12]) is not None:
                    update_port[item12] = re.sub(item11, replace[item11], update_port[item12])
                else:
                    continue
        print('\ntest exam_name:', exam_name)
        #print('now port:', update_port)
        for n in range(base_count):  # 在基本模块里找例化模块的节点
            n += 1
            print('module:', globals()['node' + str(n)].top)
            if globals()['node' + str(n)].top == exam_name:
                print('success')
                count1 += 1
                globals()['node1_' + str(count1)] = Node1(driven=[], driving=[])
                #func_port_replace(inst_port[module_name][item9], top_port[exam_name], port_replace)  # 找到需要替换的端口名字
                port_replace = func_port_replace(update_port, top_port[exam_name])  # 找到需要替换的端口名字
                print('port_replace:', port_replace)
                copy_attribute_update(globals()['node1_' + str(count1)], globals()['node' + str(n)], port_replace)  # 更新新节点的属性
            else:
                print('error')
        if inst_list[exam_name]:  # 例化的模块里还有例化  exam_name = lfsr_counter
            port_replace = func_port_replace(update_port, top_port[exam_name])  # 找到需要替换的端口名字
            print(exam_name, 'inst has inst')
            print('input port_replace:', port_replace)
            add_node_of_inst(exam_name, port_replace)
        else:
            print('empty')


def signal_analysis(arg1):  # arg1为待分析的语句块
    arg2 = {}
    arg3 = arg1.split('\n')
    for arg4 in arg3:
        if re.search('<=', arg4) is not None:  # 时序逻辑
            items = re.split(r'<=', arg4)
            for i in re.split(r',|\+|\-|\^|\|', items[0]):
                i = i.strip()
                if i[0] == '{' or i[0] == '(':
                    i = i[1:]
                if i[-1] == '}' or i[-1] == ')':
                    i = i[:-1]
                if re.search('\[', i):
                    i = re.split('\[', i)[0]
                #print('时序 i：', i)
                if i not in arg2.keys():
                    arg2[i] = []
                    #print('时序 arg2', arg2)
                    for i1 in re.split(r',|\+|\-|\^|\|', items[1]):
                        i1 = i1.strip()
                        if i1[-1] == ';':  # 去掉最后的;
                            i1 = i1[:-1]
                        if i1[0] == '{' or i1[0] == '(':
                            i1 = i1[1:]
                        if i1[-1] == '}' or i1[-1] == ')':
                            i1 = i1[:-1]
                        if re.search('\[', i1):
                            i1 = re.split('\[', i1)[0]
                        #print('时序 i1:', i1)
                        if i1 not in arg2[i]:
                            arg2[i].append(i1)
        elif re.search('=', arg4) is not None:  # 组合逻辑
            if re.search('assign', arg4) is not None:
                arg4 = re.split('assign ', arg4)[1]
                #print('arg4:', arg4)
            items = re.split(r'=', arg4)
            for i in re.split(r',|\+|\-|\^|\|', items[0]):
                i = i.strip()
                if i[0] == '{' or i[0] == '(':
                    i = i[1:]
                if i[-1] == '}' or i[-1] == ')':
                    i = i[:-1]
                if re.search('\[', i):
                    i = re.split('\[', i)[0]
                #print('组合 i：', i)
                if i not in arg2.keys():
                    arg2[i] = []
                    #print('组合 arg2', arg2)
                    for i1 in re.split(r',|\+|\-|\^|\|', items[1]):
                        i1 = i1.strip()
                        if i1[-1] == ';':  # 去掉最后的;
                            i1 = i1[:-1]
                        if i1[0] == '{' or i1[0] == '(':
                            i1 = i1[1:]
                        if i1[-1] == '}' or i1[-1] == ')':
                            i1 = i1[:-1]
                        #print('组合 i1:', i1)
                        if re.search('\[', i1):
                            i1 = re.split('\[', i1)[0]
                        if i1 not in arg2[i]:
                            arg2[i].append(i1)
        else:
            #print('pass:', arg4)
            pass

    return arg2


module_list = find_module(content)
# 分析基本模块，不考虑例化
for item in module_list:  # 按module分析 item -> module块
    a = item
    #print('a begin:\n', a)
    top_name = find_topname(re.match('module.*', a).group())
    #print('top name:', top_name)
    top_port[top_name] = []
    top_ports(a, top_port[top_name])
    #print('top_name:', top_name)
    if re.search('assign.*', a) is not None:
        count += 1
        locals()['node' + str(count)] = Node(driven=[], driving=[])
        for item0 in re.findall('assign.*', a):  # item0 -> assign
            item0 = re.split('assign ', item0)[1]
            #item0 = form(item0)
            #print('item0:', item0)
            analysis(locals()['node' + str(count)], item0)
            #print('signal is:', signal[count])
        print('assign,count is %d' % count)
        #break
    for item1 in re.findall('always[\s\S]*end\s', a):  # item1 -> 所有的always块的集合
        string = item1.split('\n')
        for item2 in string:
            item2 = item2.strip()
            #print('item2:\n', item2)
            if item2 == '':
                continue
            elif re.match('if', item2) is not None:
                count += 1
                locals()['node' + str(count)] = Node(driven=[], driving=[])
                if_lay = 1
                locals()['node' + str(count)].ifc += 1
                print('if,count is', count)
                #print('item2:\n', item2)
            elif re.match('else if', item2) is not None:
                count += 1
                locals()['node' + str(count)] = Node(driven=[], driving=[])
                if_lay = 1
                locals()['node' + str(count)].ifc += 1
                print('if,count is', count)
                #print('item2:\n', item2)
            elif re.match('else begin', item2) is not None:
                count += 1
                locals()['node' + str(count)] = Node(driven=[], driving=[])
                if_lay = 1
                locals()['node' + str(count)].ifc += 1
                print('if,count is', count)
                #print('item2:\n', item2)
            else:
                if re.match('always', item2):
                    continue
                elif re.match('end', item2):
                    if parallel_lay == 1:
                        parallel_lay = 0
                    elif if_lay > case_lay:
                        if_lay = 0
                    else:
                        case_lay = 0
                elif re.match('begin', item2):
                    continue
                else:
                    #print('line is:', item2)
                    if if_lay == 1 or case_lay == 1:
                        analysis(locals()['node' + str(count)], item2)
                        #print(locals()['node' + str(count)].num)
                        #print(locals()['node' + str(count)].max_op)
                        #print(re.split(r'\=|\,|\+|\-|\^|\|', item2))
                    else:
                        if parallel_lay == 0:
                            parallel_lay = 1
                            count += 1
                            locals()['node' + str(count)] = Node(driven=[], driving=[])
                            analysis(locals()['node' + str(count)], item2)
                            print('parallel,count is', count)
                            #print(locals()['node' + str(count)].max_op)
                            #print(re.split(r'\=|\,|\+|\-|\^|\|', item2))
                        else:
                            analysis(locals()['node' + str(count)], item2)
                            #print(locals()['node' + str(count)].max_op)
                            #print(re.split(r'\=|\,|\+|\-|\^|\|', item2))
    #break  # 第一个module

base_count = count

print('\nbegin to analyse inst')

#分析每个模块里的例化模块, 得到inst_list，inst_port
for item6 in module_list:  # 按module分析 item -> module块
    a = item6
    #print('a\n', a)
    top_name = find_topname(re.match('module.*', a).group())
    print('top name:', top_name)
    inst_list[top_name] = []
    inst_port[top_name] = []
    item3 = a.split('\n')
    for item4 in item3:
        #print('item4:', item4)
        for exam in re.findall('.*\s.*\([\s\S]*\)', item4):
            exam = exam.strip()
            #print('exam:', exam)
            if (re.search('always', exam) is None) and (re.search('if', exam) is None) and (re.search('module', exam) is None): #例化语句
                print('exam:', exam)
                exam_name = re.split(' ', exam)[0]  #例化的模块名
                inst_list[top_name].append(exam_name)
                print('exam_name:', exam_name)
                find_inst_port(exam, inst_port[top_name])
            else:
                continue

print('\nanalyse inst analysis is finished')
print('inst_list:', inst_list)
print('inst_port:', inst_port)
print('top_port:', top_port)

#正式创建节点，并添加例化模块的节点
#top = module_list[0]

for num_ in range(base_count):#添加top层的节点
    num_ += 1
    if locals()['node' + str(num_)].top == 'TOP':
        count1 += 1
        locals()['node1_' + str(count1)] = Node1(driven=[], driving=[])
        copy_attribute(locals()['node1_' + str(count1)], locals()['node' + str(num_)])

add_node_of_inst('TOP', {})
print('count1:', count1)

fp.close()

'''
ab = 'kin'
cd = 'kin[0'
ef = 'key'
index = re.compile(ab+'\[\d+')
print(re.match(index, cd))
index = re.sub(ab, ef, cd)
print(index)

for n in range(count1):
    n += 1
    print('\n', n)
    print('node.top:%s' % locals()['node1_' + str(n)].top)
    print('node.name:%d' % locals()['node1_' + str(n)].name)
    print('node.shift:%d' % locals()['node1_' + str(n)].shift)
    print('node.add_minus:%d' % locals()['node1_' + str(n)].add_minus)
    print('node.or_and:%d' % locals()['node1_' + str(n)].or_and)
    print('node.xor:%d' % locals()['node1_' + str(n)].xor)
    print('node.cat:%d' % locals()['node1_' + str(n)].cat)
    print('node.num:%d' % locals()['node1_' + str(n)].num)
    print('node.if:%d' % locals()['node1_' + str(n)].ifc)
    print('node.case:%d' % locals()['node1_' + str(n)].cac)
    print('node.max_op:%d' % locals()['node1_' + str(n)].max_op)
    print('node.driving:', locals()['node1_' + str(n)].driving)
    print('node.driven:', locals()['node1_' + str(n)].driven)
'''


for s1 in module_list:  # 分析每个模块里每个信号的驱动关系
    name1 = find_topname(re.match('module.*', s1).group())
    locals()[name1 + '_signals'] = signal_analysis(s1)
    print('%s_signals:%s:' % (name1, locals()[name1 + '_signals']))

分析例化模块里的

