# pytransfer


该模块可以对vw以及libsvm的数据格式进行转换
原始数据 -> vw，libsvm的数据格式

---------------

说明：
	采用python处理原始raw数据（一般为sql得到的数据格式）
	处理格式类型：
				1. libsvm
				2. ranksvm
				3. vw

文件：
1. featureMap.py:  格式转换
2. modelfeat.yaml  配置文件（模型的特征）
3. inputformat.py  utils函数，将libsvm转换成vw,vw2csv等
4. getmodelweights 获取模型权重的函数
