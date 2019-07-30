import numpy as np
import dataset as trojan_data
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler


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

    scaler = StandardScaler()
    train_std = scaler.fit_transform(data_train)  # 标准化
    test_std = scaler.transform(data_test)
    '''
    train_std = data_train.copy()
    test_std = data_test.copy()
    '''

    rfc = RandomForestClassifier(n_estimators=10)
    # 训练模型
    rfc.fit(train_std, target_train)
    # 计算测试集精度
    score = rfc.score(test_std, target_test)
    predict = rfc.predict(test_std)
    print('\n木马%d 精度为%s' % (test_node, score))
    print('木马%d 预测:%s' % (test_node, predict))
    print('木马%d 理想:%s' % (test_node, target_test))
    TP = 0
    FP = 0
    TN = 0
    FN = 0
    for item in range(len(test_std)):
        if rfc.predict(test_std)[item] == 1 and target_test[item] == 1:
            TP += 1
        elif rfc.predict(test_std)[item] == 1 and target_test[item] == 0:
            FP += 1
        elif rfc.predict(test_std)[item] == 0 and target_test[item] == 0:
            TN += 1
        else:
            FN += 1
    TPR = TP / (TP + FN)
    TNR = TN / (TN + FP)
    print('TPR:%f' % TPR)
    print('TNR:%f' % TNR)
