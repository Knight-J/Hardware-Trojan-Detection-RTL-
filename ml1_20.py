import numpy as np
# import dataset1_20 as trojan_data
# import dataset_auto as trojan_data
import dataset as trojan_data
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV, train_test_split


for test_node in range(21):
    test_node += 1
    pos_train = []
    pos_test = []
    neg_train = []
    neg_test = []
    for items in trojan_data.data_neg.keys():
        if items == test_node:
            for item in trojan_data.data_neg[items]:
                neg_test.append(item)
        else:
            for item in trojan_data.data_neg[items]:
                neg_train.append(item)
    for items in trojan_data.data_pos.keys():
        if items == test_node:
            for item in trojan_data.data_pos[items]:
                pos_test.append(item)
        else:
            for item in trojan_data.data_pos[items]:
                pos_train.append(item)

    data_train = np.empty(shape=[0, 10], dtype=float)
    target_train = np.empty(shape=[0, ], dtype=int)

    data_test = np.empty(shape=[0, 10], dtype=float)
    target_test = np.empty(shape=[0, ], dtype=int)

    for item in pos_train:
        n = np.asarray(item)
        data_train = np.append(data_train, [n], axis=0)
        target_train = np.append(target_train, [0], axis=0)

    for item in neg_train:
        n = np.asarray(item)
        data_train = np.append(data_train, [n], axis=0)
        target_train = np.append(target_train, [1], axis=0)

    for item in pos_test:
        n = np.asarray(item)
        data_test = np.append(data_test, [n], axis=0)
        target_test = np.append(target_test, [0], axis=0)

    for item in neg_test:
        n = np.asarray(item)
        data_test = np.append(data_test, [n], axis=0)
        target_test = np.append(target_test, [1], axis=0)

    #print(data.shape)
    #print(target.shape)

    scaler = StandardScaler()

    train_std = scaler.fit_transform(data_train)  # 标准化
    test_std = scaler.transform(data_test)
    '''
    train_std = data_train.copy()
    test_std = data_test.copy()
    '''
    #print('train_std', train_std)
    #print('test_std', test_std)
    #x_train, x_test, y_train, y_test = train_test_split(train_std, target_train, test_size=.3)

    svc = SVC(kernel='rbf', class_weight='balanced',)
    c_range = np.logspace(-4, 3, 10, base=2)
    gamma_range = np.logspace(-1, 1, 13, base=2)
    # 网格搜索交叉验证的参数范围，cv=3,3折交叉
    param_grid = [{'kernel': ['rbf'], 'C': c_range, 'gamma': gamma_range}]
    grid = GridSearchCV(svc, param_grid, cv=3, n_jobs=-1, iid=True)
    # 训练模型
    clf = grid.fit(train_std, target_train)
    # 计算测试集精度
    score = grid.score(test_std, target_test)
    print('木马%d 精度为%s' % (test_node, score))
    print('木马%d 预测:%s' % (test_node, grid.predict(test_std)))
    print('木马%d 理想:%s' % (test_node, target_test))
    print('木马%d best_params:%s' % (test_node, grid.best_params_))
    '''
    print(grid.best_score_)
    print(grid.best_params_)
    '''

    TP = 0
    FP = 0
    TN = 0
    FN = 0
    for item in range(len(test_std)):
        if grid.predict(test_std)[item] == 1 and target_test[item] == 1:
            TP += 1
        elif grid.predict(test_std)[item] == 1 and target_test[item] == 0:
            FP += 1
        elif grid.predict(test_std)[item] == 0 and target_test[item] == 0:
            TN += 1
        else:
            FN += 1
    TPR = TP/(TP + FN)
    TNR = TN/(TN + FP)
    print('TPR:%f' % TPR)
    print('TNR:%f' % TNR)

    # print('data_test:%s' % data_test)
    # print('test_std:%s' % test_std)



'''
fp = open('confirm.txt', 'w+')
fp.write('train\n')
for item in data_train:
    fp.write(str(item))
    fp.write('\n')
fp.write('test')
for item in data_test:
    fp.write(str(item))
    fp.write('\n')
'''
