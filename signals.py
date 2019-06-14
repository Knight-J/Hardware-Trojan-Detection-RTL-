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
inst_name = {}
top_input = []  #原始输入
top_output = [] #原始输出
top_original = [] #顶层模块由原始输入驱动的信号
#port_replace = {} #例化模块里需要替换的信号，key为原始信号 value为例化模块信号
block = {}
block1= {}
signal_directed = [] #各模块中与原始输入有关的信号

class Node(object):
    count_class = 0

    def __init__(self, top='', name=0, add_minus=0, or_and=0, xor=0, shift=0, cat=0, num=0, ifc=0, cac=0, max_op=0, sig={}, direct=[]):
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
        self.sig = sig
        self.direct = direct
        Node.count_class += 1


class Node1(object):
    count_class1 = 0

    def __init__(self, top='', name=0, add_minus=0, or_and=0, xor=0, shift=0, cat=0, num=0, ifc=0, cac=0, max_op=0, sig={}, direct=[]):
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
        self.sig = sig
        self.direct = direct
        Node1.count_class1 += 1


def form(arg1):
    arg1 = arg1.strip()
    arg1 = arg1[:-1]
    return arg1


def analysis(arg1, arg2):
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


def copy_attribute_update(arg1, arg2, arg3, arg4, arg5):  #arg1为新实例 arg2为老实例 arg3为端口替换表 arg4为例化的名字 arg5为被例化的模块名字
    temp = {}
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
    arg1.sig = arg2.sig.copy()

    print('old sig:', arg1.sig)
    print('replace:', arg3)

    for k in arg1.sig.keys():
        if k not in top_port[arg5]:
            temp[arg4 + '#' + k] = []
            for v in arg1.sig[k]:
                if v not in top_port[arg5]:
                    temp[arg4 + '#' + k].append(str(arg4 + '#' + v))
                else:
                    temp[arg4 + '#' + k].append(v)
        else:
            temp[k] = []
            for v in arg1.sig[k]:
                if v not in top_port[arg5]:
                    temp[k].append(str(arg4 + '#' + v))
                else:
                    temp[k].append(v)

    arg1.sig = temp.copy()

    #print('mid sig:', arg1.sig)

    for k in arg1.sig.keys():
        for v in range(len(arg1.sig[k])):
            if arg1.sig[k][v] in arg3.keys():
                arg1.sig[k][v] = arg3[arg1.sig[k][v]]
    for k in list(arg1.sig.keys()):
        if k in arg3.keys():
            arg1.sig[arg3[k]] = arg1.sig.pop(k)

    print('new sig:', arg1.sig)

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
    '''


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
    arg1.sig = arg2.sig.copy()


'''
def add_node_of_inst(module_name, replace): #当前模块的顶层名字;当前模块的port_replace
    global count1
    port_replace = {}
    for item9 in range(len(inst_list[module_name])):  # 该顶层有几个例化模块
        exam_name = inst_list[module_name][item9]
        name_of_inst = inst_name[module_name][item9]
        update_port = inst_port[module_name][item9][:]  #更新例化模块的端口
        print('old update_port:', update_port)
        print('replace:', replace)
        for item11 in replace.keys():
            comp = re.compile(item11 + '\[\d+')
            for item12 in range(len(update_port)):
                if update_port[item12] == item11:
                    update_port[item12] = replace[item11]
                elif re.match(comp, update_port[item12]) is not None:
                    update_port[item12] = re.sub(item11, replace[item11], update_port[item12])
                else:
                    continue
        print('new update_port:', update_port)
        print('\ntest exam_name:', exam_name)
        print('name_of_inst:', name_of_inst)
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
''' #612m


def add_node_of_inst(module_name, replace, inst): #当前模块的顶层名字;当前模块的port_replace
    global count1
    port_replace = {}
    for item9 in range(len(inst_list[module_name])):  # 该顶层有几个例化模块
        exam_name = inst_list[module_name][item9]
        name_of_inst = str(inst + '#' + inst_name[module_name][item9])
        update_port = inst_port[module_name][item9][:]  #更新例化模块的端口
        print('test exam_name:', exam_name)
        print('old update_port:', update_port)
        print('input replace:', replace)
        for item11 in replace.keys():
            comp = re.compile(item11 + '\[\d+')
            for item12 in range(len(update_port)):
                if update_port[item12] == item11:
                    update_port[item12] = replace[item11]
                elif re.match(comp, update_port[item12]) is not None:
                    update_port[item12] = re.sub(item11, replace[item11], update_port[item12])
                else:
                    continue
        print('update_port replace:', update_port)

        for item13 in range(len(update_port)):
            if update_port[item13] != 'clk' and re.search('#', update_port[item13]) is None:
                update_port[item13] = str(inst + '#' + update_port[item13])
            else:
                update_port[item13] = update_port[item13]
        print('update_port add name:', update_port)

        print('name_of_inst:', name_of_inst)

        port_replace = func_port_replace(update_port, top_port[exam_name])  # 找到需要替换的端口名字
        '''
        #更新信号名(例化模块)
        update_signals = {}
        for k0 in globals()[exam_name + '_signals'].keys():
            if k0 in top_port[exam_name]:  # key为顶层信号
                update_signals[k0] = []
                for v0 in globals()[exam_name + '_signals'][k0]:
                    if v0 in top_port[exam_name]:
                        update_signals[k0].append(v0)
                    else:
                        update_signals[k0].append(v0 + '_' + name_of_inst)
            else:  # key为内部信号
                update_signals[k0 + '_' + name_of_inst] = []
                for v0 in globals()[exam_name + '_signals'][k0]:
                    if v0 in top_port[exam_name]:
                        update_signals[k0 + '_' + name_of_inst].append(v0)
                    else:
                        update_signals[k0 + '_' + name_of_inst].append(v0 + '_' + name_of_inst)

        print('old update_signals:', update_signals)
        print('port_replace:', port_replace)
        for k in update_signals.keys():
            for v in range(len(update_signals[k])):
                if update_signals[k][v] in port_replace.keys():
                    update_signals[k][v] = port_replace[update_signals[k][v]]
        for k in list(update_signals.keys()):
            if k in port_replace.keys():
                update_signals[port_replace[k]] = update_signals.pop(k)
        print('    update_signals:', update_signals)
        #
        '''
        for n in range(base_count):  # 在基本模块里找例化模块的节点
            n += 1
            print('module:', globals()['node' + str(n)].top)
            if globals()['node' + str(n)].top == exam_name:
                print('success')
                count1 += 1
                globals()['node1_' + str(count1)] = Node1(sig={}, direct=[])
                #func_port_replace(inst_port[module_name][item9], top_port[exam_name], port_replace)  # 找到需要替换的端口名字
                port_replace = func_port_replace(update_port, top_port[exam_name])  # 找到需要替换的端口名字
                #print('port_replace:', port_replace)
                copy_attribute_update(globals()['node1_' + str(count1)], globals()['node' + str(n)], port_replace, name_of_inst, exam_name)  # 更新新节点的属性
            else:
                print('error')
        if inst_list[exam_name]:  # 例化的模块里还有例化
            print(exam_name, 'inst has inst')
            print('output port_replace:', port_replace)
            print('\n')
            add_node_of_inst(exam_name, port_replace, name_of_inst)
        else:
            print('empty')


def signal_analysis(arg1):  # arg1为待分析的语句块
    arg2 = {}
    arg3 = re.split('\n', arg1)
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


def signal_analysis_single(arg1):  # arg1为待分析的单个语句
    arg2 = {}
    if re.search('<=', arg1) is not None:  # 时序逻辑
        items = re.split(r'<=', arg1)
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
    elif re.search('=', arg1) is not None:  # 组合逻辑
        if re.search('assign', arg1) is not None:
            arg1 = re.split('assign ', arg1)[1]
            #print('arg1:', arg1)
        items = re.split(r'=', arg1)
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
        #print('pass:', arg1)
        pass
    return arg2


fp.close()

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
        locals()['node' + str(count)] = Node(sig={}, direct=[])
        block[count] = []  #611
        for item0 in re.findall('assign.*', a):  # item0 -> assign
            item0 = item0.strip()
            item0 = re.split('assign ', item0)[1]
            #item0 = form(item0)
            #print('item0:', item0)
            analysis(locals()['node' + str(count)], item0)
            block[count].append(item0[:-1])  #611
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
                locals()['node' + str(count)] = Node(sig={}, direct=[])
                block[count] = []  # 611
                if_lay = 1
                locals()['node' + str(count)].ifc += 1
                print('if,count is', count)
                #print('item2:\n', item2)
            elif re.match('else if', item2) is not None:
                count += 1
                locals()['node' + str(count)] = Node(sig={}, direct=[])
                block[count] = []  # 611
                if_lay = 1
                locals()['node' + str(count)].ifc += 1
                print('if,count is', count)
                #print('item2:\n', item2)
            elif re.match('else begin', item2) is not None:
                count += 1
                locals()['node' + str(count)] = Node(sig={}, direct=[])
                block[count] = []  # 611
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
                        block[count].append(item2[:-1])  # 611
                        #print(locals()['node' + str(count)].num)
                        #print(locals()['node' + str(count)].max_op)
                        #print(re.split(r'\=|\,|\+|\-|\^|\|', item2))
                    else:
                        if parallel_lay == 0:
                            parallel_lay = 1
                            count += 1
                            locals()['node' + str(count)] = Node(sig={}, direct=[])
                            block[count] = []  # 611
                            analysis(locals()['node' + str(count)], item2)
                            block[count].append(item2[:-1])  # 611
                            print('parallel,count is', count)
                            #print(locals()['node' + str(count)].max_op)
                            #print(re.split(r'\=|\,|\+|\-|\^|\|', item2))
                        else:
                            analysis(locals()['node' + str(count)], item2)
                            block[count].append(item2[:-1])  # 611
                            #print(locals()['node' + str(count)].max_op)
                            #print(re.split(r'\=|\,|\+|\-|\^|\|', item2))
    #break  # 第一个module

base_count = count


#更新node的sig属性
for i1 in range(base_count):
    i1 += 1
    for i2 in block[i1]:
        for i3 in signal_analysis_single(i2).keys():
            if i3 not in locals()['node' + str(i1)].sig.keys():
                locals()['node' + str(i1)].sig[i3] = signal_analysis_single(i2)[i3]
    print('sig:', locals()['node' + str(i1)].sig)

print('block:', block)

print('\nbegin to analyse inst********************************************')

#分析每个模块里的例化模块, 得到inst_list，inst_port, inst_name
for item6 in module_list:  # 按module分析 item -> module块
    a = item6
    #print('a\n', a)
    top_name = find_topname(re.match('module.*', a).group())
    #print('top name:', top_name)
    inst_list[top_name] = []
    inst_port[top_name] = []
    inst_name[top_name] = []
    item3 = a.split('\n')
    for item4 in item3:
        #print('item4:', item4)
        for exam in re.findall('.*\s.*\([\s\S]*\)', item4):
            exam = exam.strip()
            #print('exam:', exam)
            if (re.search('always', exam) is None) and (re.search('if', exam) is None) and (re.search('module', exam) is None): #例化语句
                #print('exam:', exam)
                exam_name = re.split(' ', exam)[0]  #例化的模块名
                inst_list[top_name].append(exam_name)
                inst_name[top_name].append(re.split(' ', exam)[1])
                #print('exam_name:', exam_name)
                find_inst_port(exam, inst_port[top_name])
            else:
                continue

print('\nanalyse inst analysis is finished')
print('inst_list:', inst_list)
print('inst_name:', inst_name)
print('inst_port:', inst_port)
print('top_port:', top_port)
print('\n')


# 获取原始输入
for s2 in re.split('\n', module_list[0]):
    s2 = s2.strip()
    if re.search('input', s2) is not None:
        if s2[-1] == ',' or s2[-1] == ';':
            s2 = s2[:-1]
        if re.search(',', s2):  # print("一行多个端口")
            for item in re.split(',', s2):  #item 为一行里的一个信号
                if re.search(' ', item):  # 一行里的第一个信号
                    if re.split(' ', item)[-1] not in top_input and re.split(' ', item)[-1] != 'clk' and re.search('rst', re.split(' ', item)[-1]) is None:
                        top_input.append(re.split(' ', item)[-1])
                else:
                    if item not in top_input and item != 'clk' and re.search('rst', item) is None:
                        print('item:', item)
                        top_input.append(item)
        else:  # print("一行一个端口")
            if re.split(' ', s2)[-1] not in top_input and re.split(' ', s2)[-1] != 'clk' and re.search('rst', re.split(' ', s2)[-1]) is None:
                top_input.append(re.split(' ', s2)[-1])
#print(top_input)


# 获得各个模块的信号驱动列表
for module in module_list:
    name1 = top_name = find_topname(re.match('module.*', module).group())
    print('module name:', name1)
    locals()[name1 + '_signals'] = signal_analysis(module)
    print(name1, locals()[name1 + '_signals'])


#获取顶层模块由原始输入驱动的信号
for item7 in TOP_signals.keys():
    for item8 in TOP_signals[item7]:
        if item8 in top_input and item7 not in top_original:
            top_original.append(item7)
print('top_original:', top_original)


#正式创建节点，并添加例化模块的节点

for num_ in range(base_count):#添加top层的节点
    num_ += 1
    if locals()['node' + str(num_)].top == 'TOP':
        count1 += 1
        locals()['node1_' + str(count1)] = Node1(sig={}, direct=[])
        copy_attribute(locals()['node1_' + str(count1)], locals()['node' + str(num_)])
        temp_top = {}
        for k in locals()['node1_' + str(count1)].sig.keys():
            if k not in top_port['TOP']:
                temp_top['top' + '#' + k] = []
                for v in locals()['node1_' + str(count1)].sig[k]:
                    if v not in top_port['TOP']:
                        temp_top['top' + '#' + k].append(str('top' + '#' + v))
                    else:
                        temp_top['top' + '#' + k].append(v)
            else:
                temp_top[k] = []
                for v in locals()['node1_' + str(count1)].sig[k]:
                    if v not in top_port['TOP']:
                        temp_top[k].append(str('top' + '#' + v))
                    else:
                        temp_top[k].append(v)
        locals()['node1_' + str(count1)].sig = temp_top.copy()


#添加例化模块的节点
print('\nbegin to add_node_of_inst***************************************************\n')
add_node_of_inst('TOP', {}, 'top')
print('count1:', count1)


#找到所有与原始输入有关的信号,更新节点的direct属性
print('find_undirected_signals begins')
num = 1
temp = top_input[:]
while num != 0:
    num = 0
    for c1 in range(count1):
        c1 += 1
        for c2 in locals()['node1_' + str(c1)].sig.keys():
            for c3 in locals()['node1_' + str(c1)].sig[c2]:
                if c3 in temp and c2 not in temp:
                    print('add:', c2)
                    temp.append(c2)
                    signal_directed.append(c2)
                    num += 1

for c3 in range(count1):
    c3 += 1
    for c4 in locals()['node1_' + str(c3)].sig.keys():
        if c4 in signal_directed:
            locals()['node1_' + str(c3)].direct.append(c4)
        else:
            for c5 in locals()['node1_' + str(c3)].sig[c4]:
                if c5 in signal_directed and c4 not in locals()['node1_' + str(c3)].direct:
                    locals()['node1_' + str(c3)].direct.append(c4)
    print('%d: %s' % (c3, locals()['node1_' + str(c3)].sig.keys()))
    print('%d:           %s' % (c3, locals()['node1_' + str(c3)].direct))

'''
for j in range(18):
    j += 1
    print('node.sig:', locals()['node1_' + str(j)].sig)
'''

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
    print('node.sig:', locals()['node1_' + str(n)].sig)
    print('node.direct:', locals()['node1_' + str(n)].direct)


