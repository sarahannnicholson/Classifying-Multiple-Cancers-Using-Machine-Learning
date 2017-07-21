import csv
import logging
import re
import numpy as np
from collections import Counter
from sklearn import svm, preprocessing
from sklearn.svm import LinearSVC
from sklearn.neural_network import MLPClassifier
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_moons, make_circles, make_classification
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

names = ["Nearest Neighbors", "Linear SVM", "RBF SVM", "Gaussian Process", "Decision Tree", "Random Forest", "Neural Net", "AdaBoost","Naive Bayes", "QDA"]

classifiers = [
	KNeighborsClassifier(3),
	SVC(kernel="linear", C=0.025),
	SVC(gamma=2, C=1),
	GaussianProcessClassifier(1.0 * RBF(1.0), warm_start=True),
	DecisionTreeClassifier(max_depth=5),
	RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
	MLPClassifier(alpha=1),
	AdaBoostClassifier(),
	GaussianNB(),
	QuadraticDiscriminantAnalysis()]

class FeatureData(object):
	"""Class responsible for interfacing with our data, eg) getting the data, stats, etc.."""

	def __init__(self, res_path, cls_path):
		self._get_classes(cls_path)
		self._get_tumor_samples(res_path)


	def _get_classes(self, path):
		with open(path, 'r') as f:
			reader = [l.strip() for l in f.readlines()]
			self.number_of_samples = reader[0].split(' ')[0]
			self.number_of_classes = reader[0].split(' ')[1]
			self.classes = reader[1].split(' ')[0:]
			self.Y = reader[2].split(' ')

	def _get_tumor_samples(self, path):
		with open(path, 'r') as inputFile:
			lines = [l.strip().split('	') for l in inputFile.readlines()]
			data = np.matrix(lines[3:]).T
			self.feature_names = data[1]
			data = data[2:]
			data = np.delete(data, list(range(1, data.shape[1], 2)), axis=0)

		self.X = data.astype(float)

	def _get_binary(self, name):
		try:
			index = self.classes.index(name) - 1
			return  [c == str(index) for c in self.Y]
		except ValueError:
			return False


	def _describe(self):
		print "\n------ data description -----"
		print "X len = ", len(self.X)
		print "Y len = ", len(self.Y)
		print "# samples = ", self.number_of_samples
		print "# classes = ", self.number_of_classes
		print "-----------------------------\n"

def plot_coefficients(classifier, feature_names, class_name, top_features=20):
	 coef = classifier.coef_[0]

	 top_positive_coefficients = np.argsort(coef)[-top_features:]
	 top_negative_coefficients = np.argsort(coef)[:top_features]
	 top_coefficients = np.hstack([top_negative_coefficients, top_positive_coefficients])

	 # create plot
	 plt.figure(figsize=(30, 15))
	 colors = ['#cccccc' if c < 0 else 'teal' for c in coef[top_coefficients]]
	 plt.bar(np.arange(2 * top_features), coef[top_coefficients], color=colors)
	 feature_names = np.array(feature_names)[top_coefficients]
	 plt.xticks(np.arange(1, 1 + 2 * top_features), feature_names, rotation='vertical', ha='right')
	 plt.savefig("graphs/plot" + class_name + ".png")


def run_test(train, test):
	train._describe()
	test._describe()

	for c in test.classes[1:]:
		print c
		trainY = train._get_binary(c)
		testY = test._get_binary(c)

		if not trainY or not testY:
			print "Not enough data"
			continue

		for name, model in zip(names, classifiers):
			model.fit(train.X, trainY)
			#plot_coefficients(model, train.feature_names.tolist()[0], c)
			results = model.predict(test.X)
			res = zip(results, testY)
			truePos = np.count_nonzero([y[0] for y in res if y[1]])
			falsePos = np.count_nonzero([y[0] for y in res if not y[1]])
			falseNeg = np.count_nonzero([not y[0] for y in res if y[1]])
			print c, name
			print float(truePos) / (truePos + falseNeg)
			# print truePos
			# print "T+" + str(truePos)
			# print "F+" + str(falsePos)
			# print "F-" + str(falseNeg)


if __name__ == '__main__':
	train = FeatureData('data/Training_res.txt', 'data/Training_cls.txt')
	test = FeatureData('data/Test_res.txt', 'data/Test_cls.txt')

	run_test(train, test)
