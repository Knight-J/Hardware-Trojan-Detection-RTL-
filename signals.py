import re

count = 0
count1 = 0
count2 = 0  # inst_port里面
inst_start = 0
base_count = 0
final_count = 0
if_lay = 0
if_nest = 0  # if嵌套
parallel_lay = 0
case_lay = 0
case_con = {}  # case语句的判断条件
case_key = ''
rst = 0
input_name = []
output_name = []
#fp = open("top_simple.txt", "r")
#fp = open("trojanonly\\8.txt", "r")
#fp = open("trojan\\8.txt", "r")
fp = open("others\\rs232.txt", "r")
content = fp.read()
exam_name = ''  #例化的模块名
instname = ''  #例化的名字
top_name = ''  #模块名
top_port = {}  #模块的顶层端口
inst_list = {}  #每个模块的例化模块
inst_port = {}
inst_name = {}
inst_name1 = {}
top_input = []  #原始输入
top_output = [] #原始输出
top_original = [] #顶层模块由原始输入驱动的信号
#port_replace = {} #例化模块里需要替换的信号，key为原始信号 value为例化模块信号
block = {}
#block1 = {}
signal_width = {}  #每个基本节点的信号位宽
signal_directed = [] #各模块中与原始输入有关的信号
data_out = []  #输出的样本数据
#sig_name = []
#sig_wid = 0
node_ctrl = {}
always_ctrl = {}
probability = {}
driving = {}

class Node(object):
    count_class = 0

    def __init__(self, top='', name=0, add_minus=0, or_and=0, xor=0, shift=0, cat=0, num=0, ifc=0, cac=0, max_op=0, active=0, sig={}, direct=[], ctrl={}):
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
        self.active = active
        self.sig = sig
        self.direct = direct
        self.ctrl = ctrl
        Node.count_class += 1


class Node1(object):
    count_class1 = 0

    def __init__(self, top='', name=0, name_o=0, add_minus=0, or_and=0, xor=0, shift=0, cat=0, num=0, ifc=0, cac=0, max_op=0, active=0, sig={}, direct=[], ctrl={}):
        self.top = top
        self.name = name
        self.name_o = name_o
        self.add_minus = add_minus
        self.or_and = or_and
        self.xor = xor
        self.shift = shift
        self.cat = cat
        self.num = num
        self.ifc = ifc
        self.cac = cac
        self.max_op = max_op
        self.active = active
        self.sig = sig
        self.direct = direct
        self.ctrl = ctrl
        Node1.count_class1 += 1


def form(arg1):
    arg = arg1.strip()
    if arg[-1] == ';':
        arg = arg[:-1]
    return arg


def analysis(arg1, arg2):
    #print('arg2:', arg2)
    arg1.top = top_name
    arg1.name = count
    arg1.add_minus += arg2.count('+') + arg2.count('-')
    arg1.or_and += arg2.count('&') + arg2.count('|')
    arg1.xor += arg2.count('^')
    arg1.cat += len(re.findall('{.*?}', arg2))
    arg1.num += 1
    b = re.split('=', arg2)
    #print('b:', b)
    if re.search(' ', b[0]) is not None:
        origin = re.split(' ', b[0])[1]  # assign等号左侧的信号
    else:
        origin = b[0]
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
                    if re.search(' |\t', item): #一行里的第一个信号
                        if re.split(' |\t', item)[-1] not in agr2:
                            agr2.append(re.split(' |\t', item)[-1])
                    else:
                        if item not in agr2:
                            #print('item:', item)
                            agr2.append(item)
            else:  # print("一行一个端口")
                if re.split(' |\t', item6)[-1] not in agr2:
                    agr2.append(re.split(' |\t', item6)[-1])


def find_module(data):
    iter = re.findall('module[\s\S]*?endmodule', data)
    return iter


def find_topname(data):
    #print('data:', data)
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


def find_inst_port_1(arg1, arg2):  # 712
    port_list = re.search('\([\s\S]*\)', arg1).group()
    #print(port_list)
    port_list = re.sub('\(|\)', '', port_list)  # 得到例化模块的端口
    #print(port_list)
    arg2.append(port_list)


def func_port_replace(arg1, arg2):  #arg1为inst_port, arg2为top_port, arg3为port_replace
    arg3 = {}
    if len(arg2) != len(arg1):
        print('error input')
        #print(len(arg1))
        #print(len(arg2))
    for item in range(len(arg2)):
        if arg1[item] != arg2[item]:
            arg3[arg2[item]] = arg1[item]
    return arg3


def copy_attribute_update(arg1, arg2, arg3, arg4, arg5, arg6):  #arg1为新实例 arg2为老实例 arg3为端口替换表 arg4为例化的名字 arg5为被例化的模块名字 arg6为原始节点的count号
    temp = {}
    arg1.top = arg2.top
    arg1.name = count1
    arg1.name_o = arg6
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
    arg1.ctrl = arg2.ctrl.copy()

    #print('old sig:', arg1.sig)
    #print('replace:', arg3)

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

    #print('new sig:', arg1.sig)

    # 626 ctrl 直接复制的上面，有冗余逻辑未删除
    temp = {}
    #print('@@@@@@@@@@@@@@@@@@@@@@@%d, old ctrl:%s' % (count1, arg1.ctrl))
    for k in arg1.ctrl.keys():
        #print('k:', k)
        if k not in top_port[arg5]:
            temp[arg4 + '#' + k] = arg1.ctrl[k][:]
        else:
            temp[k] = arg1.ctrl[k][:]

    arg1.ctrl = temp.copy()
    #print('@@@@@@@@@@@@@@@@@@@@@@@@@@ctrl:', arg1.ctrl)


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
    arg1.ctrl = arg2.ctrl.copy()


def add_node_of_inst(module_name, replace, inst): #当前模块的顶层名字;当前模块的port_replace
    global count1
    port_replace = {}
    for item9 in range(len(inst_list[module_name])):  # 该顶层有几个例化模块
        exam_name = inst_list[module_name][item9]
        name_of_inst = str(inst + '#' + inst_name[module_name][item9])
        update_port = inst_port[module_name][item9][:]  #更新例化模块的端口
        #print('test exam_name:', exam_name)
        #print('old update_port:', update_port)
        #print('input replace:', replace)
        for item11 in replace.keys():
            comp = re.compile(item11 + '\[\d+')
            for item12 in range(len(update_port)):
                if update_port[item12] == item11:
                    update_port[item12] = replace[item11]
                elif re.match(comp, update_port[item12]) is not None:
                    update_port[item12] = re.sub(item11, replace[item11], update_port[item12])
                else:
                    continue
        #print('update_port replace:', update_port)

        for item13 in range(len(update_port)):
            if update_port[item13] != 'clk' and re.search('#', update_port[item13]) is None and update_port[item13] not in top_port['TOP']:
            #if update_port[item13] != 'clk' and re.search('#', update_port[item13]) is None:
                update_port[item13] = str(inst + '#' + update_port[item13])
            else:
                update_port[item13] = update_port[item13]
        #print('update_port add name:', update_port)

        #print('name_of_inst:', name_of_inst)

        port_replace = func_port_replace(update_port, top_port[exam_name])  # 找到需要替换的端口名字

        for n in range(base_count):  # 在基本模块里找例化模块的节点
            n += 1
            #print('module:', globals()['node' + str(n)].top)
            if globals()['node' + str(n)].top == exam_name:
                print('success')
                count1 += 1
                #print('^^^^^^^^^^^^^count1:', count1)
                globals()['node1_' + str(count1)] = Node1(sig={}, direct=[], ctrl={})
                #func_port_replace(inst_port[module_name][item9], top_port[exam_name], port_replace)  # 找到需要替换的端口名字
                port_replace = func_port_replace(update_port, top_port[exam_name])  # 找到需要替换的端口名字
                #print('port_replace:', port_replace)
                copy_attribute_update(globals()['node1_' + str(count1)], globals()['node' + str(n)], port_replace, name_of_inst, exam_name, n)  # 更新新节点的属性
            else:
                print('error')
        if inst_list[exam_name]:  # 例化的模块里还有例化
            #print(exam_name, 'inst has inst')
            #print('output port_replace:', port_replace)
            #print('\n')
            add_node_of_inst(exam_name, port_replace, name_of_inst)
        else:
            print('empty')


def signal_analysis(arg1):  # arg1为待分析的语句块
    arg2 = {}
    #print('arg1:\n', arg1)
    arg3 = re.split('\n', arg1)
    for arg4 in arg3:
        #print('arg4:', arg4)
        arg4 = arg4.strip(' |\t')
        if re.search('<=', arg4) is not None:  # 时序逻辑
            #print('arg4:', arg4)
            items = re.split(r'<=', arg4)
            #print('items:', items)
            for i in re.split(r',|\+|\-|\^|\||\&|>>', items[0]):
                i = i.strip(' |\t')
                #print('i:', i)
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
                for i1 in re.split(r',|\+|\-|\^|\||\&|>>', items[1]):
                    i1 = i1.strip(' |\t')
                    #print('i1:', i1)
                    #print('items[1]:', items[1])
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
        elif re.search('=', arg4) is not None and re.search(' if', arg4) is None and re.match('if', arg4) is None:  # 组合逻辑
            if re.search('assign', arg4) is not None:
                arg4 = re.split('assign ', arg4)[1]
            #print('arg4:', arg4)
            items = re.split(r'=', arg4)
            for i in re.split(r',|\+|\-|\^|\||\&|>>', items[0]):
                i = i.strip(' |\t')
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
                for i1 in re.split(r',|\+|\-|\^|\||\&|>>', items[1]):
                    i1 = i1.strip(' |\t')
                    #print('items[1]:', items[1])
                    #print('i1:', i1)
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
        for i in re.split(r',|\+|\-|\^|\||\&|>>', items[0]):
            i = i.strip(' |\t')
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
            for i1 in re.split(r',|\+|\-|\^|\||\&|>>', items[1]):
                i1 = i1.strip(' |\t')
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
    elif re.search('=', arg1) is not None and re.search(' if', arg1) is None and re.match('if', arg1) is None:  # 组合逻辑
        if re.search('assign', arg1) is not None:
            arg1 = re.split('assign ', arg1)[1]
            #print('arg1:', arg1)
        #print('arg1:', arg1)
        items = re.split(r'=', arg1)
        #print('items:', items)
        for i in re.split(r',|\+|\-|\^|\||\&|>>', items[0]):
            i = i.strip(' |\t')
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
            for i1 in re.split(r',|\+|\-|\^|\||\&|>>', items[1]):
                i1 = i1.strip(' |\t')
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


def control_analysis(arg1):  # arg1为1行代码 分析IF的判断条件
    arg2 = {}
    #print('%%%%%%%%%%%%%%%%%%%%%%%%分析控制信号')
    #print('block%d' % count)
    node_ctrl = {}
    ctrl = arg1.strip()
    #print(ctrl)
    ctrl = re.search('\(.*\)', ctrl).group()
    ctrl = ctrl[1:-1]  # 去掉最外面的括号
    ctrl = ctrl.strip()
    #print('ctrl:', ctrl)
    if len(re.findall('\(', ctrl)) >= 1:  # 大于一个判断条件
        if re.search('\|\|', ctrl) is None:  # 没有||
            for item9 in re.split('&&', ctrl):
                item9 = item9.strip()
                #print('item9:', item9)
                #if item9[0] == '(' or item9[-1] == ')':
                item9 = item9.lstrip('(')
                item9 = item9.rstrip(')')
                l_signal = re.split('==|>|<', item9)[0].strip()
                # r_signal = re.split('==|>|<', item9)[1].strip()
                r_signal = re.search('[=><].*', item9).group().strip()
                r_signal = r_signal.lstrip('(')
                r_signal = r_signal.rstrip(')')
                #print('l_signal:', l_signal)
                #print('r_signal:', r_signal)
                if l_signal not in node_ctrl.keys():
                    arg2[l_signal] = []
                    arg2[l_signal].append(r_signal)
                else:
                    if r_signal not in arg2[l_signal]:
                        arg2[l_signal].append(r_signal)
            # 添加always的控制信息
            for a_k in always_ctrl.keys():
                if a_k not in arg2.keys():
                    arg2[a_k] = []
                    arg2[a_k].append(always_ctrl[a_k][0])

        else:  # 有||
            print('mul')
    else:  # 只有一个括号
        if re.search('negedge', ctrl) is None and re.search('posedge', ctrl) is None and re.search(',', ctrl) is None and re.search('==|>|<', ctrl) is not None:
            l_signal = re.split('==|>|<', ctrl)[0].strip()
            #r_signal = re.split('==|>|<', ctrl)[1].strip()
            r_signal = re.search('[=><].*', ctrl).group().strip()
            #print('split:', re.split('==|>|<', ctrl))
            #print('l_signal:', l_signal)
            #print('r_signal:', r_signal)
            if l_signal not in arg2.keys():
                arg2[l_signal] = []
                arg2[l_signal].append(r_signal)
            else:
                if r_signal not in arg2[l_signal]:
                    arg2[l_signal].append(r_signal)
            # 添加always的控制信息
            print('$$$$$$$$$$#######always_ctrl:%s' % always_ctrl)
            for a_k in always_ctrl.keys():
                if a_k not in arg2.keys():
                    arg2[a_k] = []
                    arg2[a_k].append(always_ctrl[a_k][0])

        else:  # always语句
            print('always判断')
            if re.search(',', ctrl) is not None:  # 多个条件
                for item10 in re.split(',', ctrl):
                    item10 = item10.strip()
                    #print('always ,:', item10)
                    if re.search('negedge', item10) is None and re.search('posedge', item10) is None:  # 非边沿
                        if item10 not in arg2.keys():
                            arg2[item10] = []
                            arg2[item10].append('signal')
                    else:  # 边沿
                        if re.split(' ', item10)[1].strip() not in arg2.keys():
                            arg2[re.split(' ', item10)[1].strip()] = []
                            arg2[re.split(' ', item10)[1].strip()].append('edge')
            elif re.search('or', ctrl) is not None:
                for item11 in re.split('or', ctrl):
                    item11 = item11.strip()
                    #print('always or:', item11)
                    if re.search('negedge', item11) is None and re.search('posedge', item11) is None:
                        if item11 not in arg2.keys():
                            arg2[item11] = []
                            arg2[item11].append('signal')
                    else:
                        if re.split(' ', item11)[1].strip() not in arg2.keys():
                            arg2[re.split(' ', item11)[1].strip()] = []
                            arg2[re.split(' ', item11)[1].strip()].append('edge')
            else:  # 一个判断条件
                if re.search('negedge', ctrl) is None and re.search('posedge', ctrl) is None:
                    if ctrl[0] == '!' or ctrl[0] == '~':
                        ctrl = ctrl[1:]
                    if ctrl not in arg2.keys():
                        arg2[ctrl] = []
                        arg2[ctrl].append('signal')
                else:
                    if re.split(' ', ctrl)[1].strip() not in arg2.keys():
                        arg2[re.split(' ', ctrl)[1].strip()] = []
                        arg2[re.split(' ', ctrl)[1].strip()].append('edge')
    #print('...............................node_ctrl:', arg2)
    return arg2


def signal_control_analysis(arg1):  #分析IF条件控制的语句块 arg1 单条语句
    #print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!分析语句的控制:', arg1)
    arg1 = arg1.strip()
    l_signal = re.split('=', arg1)[0].strip()
    r_signal = re.split('=', arg1)[1].strip()
    if l_signal[-1] == '<':
        l_signal = l_signal[:-1]
    if r_signal[-1] == ';':
        r_signal = r_signal[:-1]
    if re.search('\[', l_signal) is not None:
        l_signal = re.split('\[', l_signal)[0]
    if re.search('\d$', r_signal) is None:
        r_signal = 'complex'
    #print('!l_signal:', l_signal)
    #print('!r_signal:', r_signal)



def width(arg1, arg2):
    temp1 = arg1.strip()
    if temp1[-1] == ',' or temp1[-1] == ';':
        temp1 = temp1[:-1]
    #print('temp1:', temp1)
    if re.search('\[', temp1) is None:  # 位宽为1
        wi = 1
        #print('wi:', wi)
    else:
        wi = re.search('\d*:\d*', temp1).group()
        #print('wi:', wi)
        wi = int(re.split(':', wi)[0]) - int(re.split(':', wi)[1]) + 1
        #print('wi:', wi)
    if re.search(',', temp1):  # print("一行多个端口")
        for si1 in re.split(',', temp1):  # item 为一行里的一个信号
            if re.search('\s', si1):  # 一行里的第一个信号
                if re.split('\s', si1)[-1] not in arg2.keys():
                    arg2[re.split('\s', si1)[-1]] = wi
            else:
                if si1 not in arg2.keys():
                    arg2[si1] = wi
    else:  # print("一行一个端口")
        if re.split('\s', temp1)[-1] not in arg2.keys():
            arg2[re.split('\s', temp1)[-1]] = wi


fp.close()

module_list = find_module(content)
# 分析基本模块，不考虑例化
for item in module_list:  # 按module分析 item -> module块
    a = item
    #print('a begin:\n', a)
    top_name = find_topname(re.match('module.*\(', a).group())  # 711
    #print('top name:', top_name)
    top_port[top_name] = []
    top_ports(a, top_port[top_name])
    #print('top_name:', top_name)
    # 信号位宽分析 621
    signal_width[top_name] = {}
    for input in re.findall('input.*', a):
        width(input, signal_width[top_name])
    for output in re.findall('output.*', a):
        width(output, signal_width[top_name])
    for reg in re.findall('reg.*', a):
        width(reg, signal_width[top_name])
    for wire in re.findall('wire.*', a):
        width(wire, signal_width[top_name])
    print('##########################################module_name', top_name)
    print('#########################################signal_width', signal_width)
    #
    if re.search('assign.*', a) is not None:
        count += 1
        # 节点的控制信号
        node_ctrl[count] = {}
        #
        locals()['node' + str(count)] = Node(sig={}, direct=[], ctrl={})
        # 626
        locals()['node' + str(count)].ctrl = node_ctrl[count].copy()
        #
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
            elif re.match('if', item2) is not None:  # if语句块
                parallel_lay = 0  # 716
                if if_lay == 0:  # 716 if无嵌套
                    count += 1
                    locals()['node' + str(count)] = Node(sig={}, direct=[], ctrl={})
                    block[count] = []  # 611
                    if_lay = 1
                    locals()['node' + str(count)].ifc += 1
                    print('if,count is', count)
                    # print('item2:\n', item2)
                    # 节点的控制信号621
                    node_ctrl[count] = control_analysis(item2)
                    # 626
                    locals()['node' + str(count)].ctrl = node_ctrl[count].copy()
                    #
                else:  # 716 if有嵌套
                    node_ctrl[count] = control_analysis(item2)
                if re.search('rst', item2) is None:
                    rst = 0
                else:
                    rst = 1
            elif re.match('else if', item2) is not None:  # if语句块
                count += 1
                locals()['node' + str(count)] = Node(sig={}, direct=[], ctrl={})
                block[count] = []  # 611
                if_lay = 1
                locals()['node' + str(count)].ifc += 1
                print('if,count is', count)
                #print('item2:\n', item2)
                # 节点的控制信号
                node_ctrl[count] = control_analysis(item2)
                # 626
                locals()['node' + str(count)].ctrl = node_ctrl[count].copy()
                #
            elif re.match('else begin', item2) is not None:  # if语句块
                count += 1
                locals()['node' + str(count)] = Node(sig={}, direct=[], ctrl={})
                block[count] = []  # 611
                if_lay = 1
                locals()['node' + str(count)].ifc += 1
                print('if,count is', count)
                #print('item2:\n', item2)
                # 节点的控制信号
                # node_ctrl[count] = control_analysis(item2)
                node_ctrl[count] = node_ctrl[count-1].copy()  # 701
                # 626
                locals()['node' + str(count)].ctrl = node_ctrl[count].copy()
                #
            elif re.match('else', item2) is not None:  # 618  # if语句块
                count += 1
                locals()['node' + str(count)] = Node(sig={}, direct=[], ctrl={})
                block[count] = []  # 611
                if_lay = 1
                locals()['node' + str(count)].ifc += 1
                print('if,count is', count)
                #print('item2:\n', item2)
                # 节点的控制信号
                # node_ctrl[count] = control_analysis(item2)
                node_ctrl[count] = node_ctrl[count-1].copy()  # 701
                # 626
                locals()['node' + str(count)].ctrl = node_ctrl[count].copy()
                #
            elif re.match('case \(', item2):  # 620  # case语句块
                print('case分支%s' % item2)
                case_con.clear()  # 715
                case_con[re.search('\(.*\)', item2).group().strip().lstrip('\(').rstrip('\)'.strip())] = []  # 715
                #print('case_con%s' % case_con)
                case_key = re.search('\(.*\)', item2).group().strip().lstrip('\(').rstrip('\)'.strip())  # 715
                case_lay = 1
                if parallel_lay == 1:
                    parallel_lay = 0
                #print('case_con:', case_con)
                '''
                count += 1
                locals()['node' + str(count)] = Node(sig={}, direct=[], ctrl={})
                block[count] = []  # 611
                locals()['node' + str(count)].cac += 1
                print('case,count is', count)
                '''
            else:
                if re.match('always', item2):
                    always_ctrl = control_analysis(item2)
                    #print('$$$$$$$$$$$$$$$$$always_ctrl:', always_ctrl)
                elif re.match('end', item2):
                    if rst == 1:  # 715 复位
                        rst = 0
                    elif parallel_lay == 1:
                        parallel_lay = 0
                    #elif if_lay > case_lay:
                    elif if_lay == 1:
                        if_lay = 0
                    else:
                        if re.match('endcase', item2) is not None:
                            case_lay = 0
                elif re.match('begin', item2):
                    continue
                else:  # 语句分析
                    #print('line is:', item2)
                    if re.search(':$', item2) is not None and case_lay == 1:  # case的一个判断分支
                        case_con[case_key] = item2[:-1]
                        print('case_con:', case_con)
                    #elif rst == 1:  # 715 复位
                        #continue
                    #elif if_lay == 1 or case_lay == 1:
                    elif if_lay == 1 and case_lay == 0:  # 单纯的if
                        #print('item2:', item2)
                        analysis(locals()['node' + str(count)], item2)
                        block[count].append(item2[:-1])  # 611
                        signal_control_analysis(item2)
                        # print(locals()['node' + str(count)].num)
                        # print(locals()['node' + str(count)].max_op)
                        # print(re.split(r'\=|\,|\+|\-|\^|\|', item2))
                    elif if_lay == 0 and case_lay == 1:
                        if parallel_lay == 0:
                            parallel_lay = 1
                            count += 1
                            locals()['node' + str(count)] = Node(sig={}, direct=[], ctrl={})
                            block[count] = []
                            locals()['node' + str(count)].cac += 1
                            print('parallel,count is', count)

                            #print('item2:', item2)
                            analysis(locals()['node' + str(count)], item2)
                            block[count].append(item2[:-1])  # 611
                            signal_control_analysis(item2)
                            #print(locals()['node' + str(count)].num)
                            #print(locals()['node' + str(count)].max_op)
                            #print(re.split(r'\=|\,|\+|\-|\^|\|', item2))
                            node_ctrl[count] = case_con.copy()
                            locals()['node' + str(count)].ctrl = case_con.copy()
                        else:
                            #print('item2:', item2)
                            analysis(locals()['node' + str(count)], item2)
                            block[count].append(item2[:-1])  # 611
                            signal_control_analysis(item2)
                            # print(locals()['node' + str(count)].num)
                            # print(locals()['node' + str(count)].max_op)
                            # print(re.split(r'\=|\,|\+|\-|\^|\|', item2))
                    elif if_lay == 1 and case_lay == 1:
                        #print('item2:', item2)
                        analysis(locals()['node' + str(count)], item2)
                        block[count].append(item2[:-1])  # 611
                        signal_control_analysis(item2)
                        # print(locals()['node' + str(count)].num)
                        # print(locals()['node' + str(count)].max_op)
                        # print(re.split(r'\=|\,|\+|\-|\^|\|', item2))
                    else:  # if_lay == 0 and case_lay == 0
                        if parallel_lay == 0:
                            parallel_lay = 1
                            count += 1
                            locals()['node' + str(count)] = Node(sig={}, direct=[], ctrl={})
                            block[count] = []  # 611
                            analysis(locals()['node' + str(count)], item2)
                            block[count].append(item2[:-1])  # 611
                            print('parallel,count is', count)
                            signal_control_analysis(item2)
                            # 节点的控制信号621
                            node_ctrl[count] = always_ctrl
                            # 626
                            locals()['node' + str(count)].ctrl = node_ctrl[count].copy()
                            #
                            #print(locals()['node' + str(count)].max_op)
                            #print(re.split(r'\=|\,|\+|\-|\^|\|', item2))
                        else:
                            analysis(locals()['node' + str(count)], item2)
                            block[count].append(item2[:-1])  # 611
                            signal_control_analysis(item2)
                            #print(locals()['node' + str(count)].max_op)
                            #print(re.split(r'\=|\,|\+|\-|\^|\|', item2))
    #break  # 第一个module

base_count = count


#更新node的sig属性
for i4 in range(base_count):
    i4 += 1
    for i2 in block[i4]:
        #print('i2:', i2)
        for i3 in signal_analysis_single(i2).keys():
            #print('i3:')
            if i3 not in locals()['node' + str(i4)].sig.keys():
                locals()['node' + str(i4)].sig[i3] = signal_analysis_single(i2)[i3]
    print('sig:', locals()['node' + str(i4)].sig)

print('block:', block)

print('\nbegin to analyse inst********************************************')

#分析每个模块里的例化模块, 得到inst_list，inst_port, inst_name, inst_name1
for item6 in module_list:  # 按module分析 item -> module块
    count2 = 0
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
        ''' # 712
        for exam in re.findall('.*\s.*\([\s\S]*\)', item4):
            exam = exam.strip()
            print('exam:', exam)
            if (re.search('always', exam) is None) and (re.search('if', exam) is None) and (re.search('module', exam) is None) and (re.search('=', exam) is None) and (re.search('case', exam) is None) and (re.search('\.', exam) is None): #例化语句
                print('exam true:', exam)
                exam_name = re.split(' ', exam)[0]  #例化的模块名
                inst_list[top_name].append(exam_name)
                inst_name[top_name].append(re.split(' ', exam)[1])
                inst_name1[re.split(' ', exam)[1]] = re.split(' ', exam)[0] #628
                #print('exam_name:', exam_name)
                find_inst_port(exam, inst_port[top_name])
            else:
                continue
        '''
        if re.search('\(', item4) is not None:  # 712
            exam = item4.strip()
            #print('exam:', exam)
            if (re.search('always', exam) is None) and (re.search('if', exam) is None) and (
                    re.search('module', exam) is None) and (re.search('=', exam) is None) and (
                    re.search('case', exam) is None) and (re.search('\.', exam) is None):  # 例化语句
                #print('exam true:', exam)
                exam_name = re.split(' ', exam)[0]  # 例化的模块名
                instname = re.split(' ', exam)[1]  # 例化的名字
                inst_list[top_name].append(exam_name)
                inst_name[top_name].append(re.split(' ', exam)[1])
                inst_name1[re.split(' ', exam)[1]] = re.split(' ', exam)[0]  # 628
                inst_start = 1
                if re.search('\)', exam) is not None:  # xx xx ();例化
                    #print('xx xx ();例化')
                    #print('exam_name:', exam_name)
                    find_inst_port(exam, inst_port[top_name])
            elif re.search('\.', exam) is not None:  # xx xx (.a(a),例化
                exam = item4.strip()
                #print('exam_name:', exam_name)
                #print('exam 。:', exam)
                #print('exam_name:', exam_name)
                if inst_start == 1:
                    inst_start = 0
                    inst_port[top_name].append([])
                find_inst_port_1(exam, inst_port[top_name][count2])
                if re.search(',', item4) is None and inst_start == 0:
                    count2 += 1
                    print('count2:', count2)

print('\nanalyse inst analysis is finished')
print('inst_list:', inst_list)
print('inst_name:', inst_name)
print('inst_name1:', inst_name1)
print('inst_port:', inst_port)
print('top_port:', top_port)
print('\n')


# 获取原始输入
for s2 in re.split('\n', module_list[0]):
    s2 = s2.strip()
    if re.search('input', s2) is not None:
        if s2[-1] == ',' or s2[-1] == ';':
            s2 = s2[:-1]
        #print('@@@@@@@@@@@@@@@@@@@input:%s' % s2)
        if re.search(',', s2):  # print("一行多个端口")
            for item in re.split(',', s2):  #item 为一行里的一个信号
                if re.search(' |\t', item):  # 一行里的第一个信号
                    if re.split(' |\t', item)[-1] not in top_input and re.split(' |\t', item)[-1] != 'clk':
                        top_input.append(re.split(' |\t', item)[-1])
                else:
                    if item not in top_input and item != 'clk' and re.search('rst', item) is None:
                        #print('item:', item)
                        top_input.append(item)
        else:  # print("一行一个端口")
            if re.split(' |\t', s2)[-1] not in top_input and re.split(' |\t', s2)[-1] != 'clk':
                #print(re.split(' |\t', s2)[-1])
                top_input.append(re.split(' |\t', s2)[-1])
#print(top_input)


# 获得各个模块的信号驱动列表
for module in module_list:
    name1 = find_topname(re.match('module.*', module).group())
    #print('module name:', name1)
    '''
    locals()[name1 + '_signals'] = signal_analysis(module)
    print(name1, locals()[name1 + '_signals'])
    '''
    driving[name1] = signal_analysis(module)
    #print(name1, driving[name1])


'''
#获取顶层模块由原始输入驱动的信号
for item7 in TOP_signals.keys():
    for item8 in TOP_signals[item7]:
        if item8 in top_input and item7 not in top_original:
            top_original.append(item7)
print('top_original:', top_original)
'''

#正式创建节点，并添加例化模块的节点

for num_ in range(base_count):#添加top层的节点
    num_ += 1
    if locals()['node' + str(num_)].top == 'TOP':
        count1 += 1
        locals()['node1_' + str(count1)] = Node1(sig={}, direct=[], ctrl={})
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

# 713 for test
for n in range(count1):
    out = []
    n += 1
    print('\n', n)
    print('\n'.join(['%s:%s' % item for item in locals()['node1_' + str(n)].__dict__.items()]))
    print('node.top:%s' % locals()['node1_' + str(n)].top)


#找到所有与原始输入有关的信号,更新节点的direct属性
print('##############################find_undirected_signals begins')
num = 1
temp = top_input[:]
print('temp:%s' % temp)
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

print('signal_directed:%s' % signal_directed)

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




# for test 716
for item7 in range(len(block)):
    item7 += 1
    print('block%d:%s' % (item7, block[item7]))
for item8 in signal_width.keys():
    print('signal_width[%s]:%s' % (item8, signal_width[item8]))
print('top_input:%s' % top_input)
for item9 in driving.keys():
    print('module %s' % item9)
    for item10 in driving[item9].keys():
        print('driving[%s]:%s' % (item10, driving[item9][item10]))
for item9 in node_ctrl.keys():
    print('node%s ctrl:%s' % (item9, node_ctrl[item9]))



print('signal_width:', signal_width)
print('inst_name:', inst_name)
# 更新节点的发生概率
reg_width = 0
module_name = ''
signal_name = ''
active = 1
print('\n开始分析节点的发生概率')
for p1 in range(count1):
    p1 += 1
    print('number', p1)
    if locals()['node1_' + str(p1)].ctrl != {}:
        for p2 in locals()['node1_' + str(p1)].ctrl.keys():
            if re.search('#', p2) is None:
                print('p2', p2)
                module_name = locals()['node1_' + str(p1)].top
                if re.search('\[', p2) is None:
                    if p2 in top_port[module_name]:
                        reg_width = signal_width[module_name][p2]
                    else:
                        if re.search('!|~', p2) is not None:
                            p2 = p2.lstrip('!|~')
                        reg_width = signal_width['TOP'][p2]
                elif re.search(':', p2) is None:
                    reg_width = 1
                else:
                    w = re.search('\d*:\d*', p2).group()
                    print('w:', w)
                    reg_width = int(re.split(':', w)[0]) - int(re.split(':', w)[1]) + 1
                print(reg_width)
                if p2 != 'clk' and p2 != 'rst':
                    active *= (1/(2**reg_width))
                locals()['node1_' + str(p1)].active = active
                print('active:', active)
            else:
                signal_name = re.split('#', p2)[-1]
                print('p2', p2)
                print(signal_name)
                module_name = re.split('#', p2)[-2]
                module_name = inst_name1[module_name]
                #print('module_name:', module_name)
                if re.search('\[', signal_name) is None:
                    reg_width = signal_width[module_name][signal_name]
                elif re.search(':', p2) is None:
                    reg_width = 1
                else:
                    w = re.search('\d*:\d*', p2).group()
                    reg_width = int(re.split(':', w)[0]) - int(re.split(':', w)[1]) + 1
                print(reg_width)
                if signal_name != 'clk' and p2 != 'rst':
                    active *= (1 / (2**reg_width))
                locals()['node1_' + str(p1)].active = active
                print('active:', active)
    else:
        locals()['node1_' + str(p1)].active = 1
    active = 1

'''
# 输出节点的属性
for n in range(count1):
    n += 1
    print(n)
    print('\n'.join(['%s:%s' % item for item in locals()['node1_' + str(n)].__dict__.items()]))
'''

'''
for j in range(18):
    j += 1
    print('node.sig:', locals()['node1_' + str(j)].sig)
'''

'''
for XX in range(count):
    XX += 1
    print('%d :' % XX)
    print('控制', node_ctrl[XX])
    # print('代码', block[XX])
'''

'''
#输出结果
f = open('testdata.txt', 'w+')
for n in range(count1):
    out = []
    n += 1
    print('\n', n)
    print('\n'.join(['%s:%s' % item for item in locals()['node1_' + str(n)].__dict__.items()]))
    print('node.top:%s' % locals()['node1_' + str(n)].top)
    for item in locals()['node1_' + str(n)].__dict__.items():
        if item[0] == 'num' or item[0] == 'active':
            continue
        elif item[0] == 'sig':
            out.append(len(item[1]) / locals()['node1_' + str(n)].num)
        elif item[0] == 'direct':
            out.append(len(item[1]) / locals()['node1_' + str(n)].num)
        elif item[0] != 'top' and item[0] != 'name' and item[0] != 'name_o':
            out.append(item[1]/locals()['node1_' + str(n)].num)

    f.write(str(out))
    f.write('\n')
f.close()
'''


#输出结果
print('begin to write files')
#pos = open('database\\pos.txt', 'a+')
#neg = open('database\\neg.txt', 'a+')
pos = open('database\\pos.txt', 'w+')
neg = open('database\\neg.txt', 'w+')
for n in range(count1):
    out = []
    n += 1
    print('\n', n)
    print('\n'.join(['%s:%s' % item for item in locals()['node1_' + str(n)].__dict__.items()]))
    print('node.top:%s' % locals()['node1_' + str(n)].top)
    for item in locals()['node1_' + str(n)].__dict__.items():
        #print('item:', item)
        if item[0] == 'top' or item[0] == 'name' or item[0] == 'name_o' or item[0] == 'num' or item[0] == 'sig' or item[0] == 'ctrl':
            continue
        elif item[0] == 'active':
            out.append(locals()['node1_' + str(n)].active)
        elif item[0] == 'max_op':
            out.append(locals()['node1_' + str(n)].max_op)
        elif item[0] == 'ifc':
            out.append(locals()['node1_' + str(n)].ifc)
        elif item[0] == 'cac':
            out.append(locals()['node1_' + str(n)].cac)
        elif item[0] == 'direct':
            if len(locals()['node1_' + str(n)].direct) < len(locals()['node1_' + str(n)].sig):
                out.append(1)
                print('direct:1')
            else:  # direct == sig
                out.append(0)
                print('direct:0')
        else:  # add_minus, or_and, xor, shift, cat
            print(item)
            #out.append(item[1]/locals()['node1_' + str(n)].num)
            out.append(item[1])
    #if n <= 18:
    if locals()['node1_' + str(n)].top in ['TOP', 'expand_key_128', 'S', 'one_round', 'table_lookup', 'T', 'xS', 'final_round', 'S4']:
        pos.write(str(out))
        pos.write('\n')
    else:
        neg.write(str(out))
        neg.write('\n')
    print(out)
pos.close()
neg.close()

print('控制', node_ctrl)
print('top_input:%s' % top_input)
