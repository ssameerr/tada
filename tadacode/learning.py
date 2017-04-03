
import numpy as np

from clustering.fuzzy_clustering import FCM


def train_with_data_and_meta(data=None, meta_data=None):
    """
    :param data: data points
    :param meta_data: a list of meta_data, each meta_data is a dict
    :return: FCM model
    """
    if meta_data is None:
        print "train_with_data_and_meta> meta data can't be None"
        return None
    if data is None:
        print "train_with_data_and_meta> data can't be None"
        return None
    model = FCM(n_clusters=len(meta_data), max_iter=1)
    u = np.zeros((data.shape[0], len(meta_data)))
    for clus, md in enumerate(meta_data):
        print "%d from index %d to index %d" % (clus, md["from_index"], md["to_index"])
        for i in range(md["from_index"], md["to_index"]):
            u[i][clus] = 1.0
    model.u = u
    model.compute_cluster_centers(data)
    return model


def test_with_data_and_meta(model=None, data=None, meta_data=None):
    """
    :param model: FCM model
    :param data: test data
    :param meta_data: a list of test meta data each with the cluster they belong to
    :return: a list of dict, each has the following info:
        score_vector: np.array of membership
        cluster: integer
        type: class/property string
    """
    print "\n****************************"
    print "*  test_with_data_and_meta *"
    print "****************************\n"
    if model is None:
        print "test_with_data_and_meta> model should not be None"
    if data is None:
        print "test_with_data_and_meta> data should not be None"
    if meta_data is None:
        print "test_with_data_and_meta> meta_data should not be None"
    meta_u = []
    num_of_correct = 0
    for clus, md in enumerate(meta_data):
        u = model.predict(data[md["from_index"]:md["to_index"]])
        uu = {}
        uu["score_vector"] = np.average(u, axis=0)
        uu["cluster"] = md["cluster"]
        uu["num_of_row"] = u.shape[0]
        uu["type"] = md["type"]
        meta_u.append(uu)
        print "\n---------------"
        #print "data: "
        #print data[md["from_index"]:md["to_index"]]
        print "from-to: %d - %d" % (md["from_index"], md["to_index"])
        print "type:          %s" % uu["type"]
        print "score: %f " % uu["score_vector"][uu["cluster"]]
        print "classified as: %s" % meta_data[uu["score_vector"].argmax()]["type"]
        print "classification score: %f " % uu["score_vector"].max()
        if np.any(np.isnan(uu["score_vector"])):
            print "clus %d has nan" % clus
            print uu["score_vector"]
            print "and u:"
            print u
            kkk = 1/0
        #print "classified as: %s" % meta_data[md["cluster"]]["type"]

        if meta_data[uu["score_vector"].argmax()]["type"] == md["type"]: #md["type"] == meta_data[md["cluster"]]["type"]:
            num_of_correct += 1

        meta_u.append(uu)
    print "number of correctly classified is: %d out of %d" % (num_of_correct, len(meta_data))
        #print "score vector: %s" % str(uu["score_vector"])
    print "\n=============\n"
    return meta_u


def get_cluster_for_meta(training_meta=None, testing_meta=None):
    print "\n*************************"
    print "*  get_cluster_for_meta *"
    print "*************************\n"
    if training_meta is None:
        print "get_cluster_for_meta> training meta should not be None"
        return []
    if testing_meta is None:
        print "get_cluster_for_meta> testing meta should not be None"
        return []
    new_meta = testing_meta
    for clus, tr_meta in enumerate(training_meta):
        for idx, te_meta in enumerate(testing_meta):
            if tr_meta["type"] == te_meta["type"]:
                new_meta[idx]["cluster"] = clus
                break
    for nm in new_meta:
        print "\n------------"
        print "type: %s" % nm["type"]
        print "cluster: %d" % nm["cluster"]
        print "from-to: %d - %d" % (nm["from_index"], nm["to_index"])
    print "\n==================\n"
    return new_meta


def predict(model=None, data=None, meta_data=None):
    """
    :param model: FCM model
    :param data: data to be predicted
    :param meta_data: meta data of the provided data
    :return:
    """
    if model is None:
        print "predict> model should not be None"
        return None
    if data is None:
        print "predict> data should not be None"
        return None
    if meta_data is None:
        print "predict> meta data should not be None"

    uu = []
    for idx, md in enumerate(meta_data):
        u = model.predict(data[md["from_index"]:md["to_index"]])
        u_avg = np.average(u, axis=0)
        print "\n----------"
        print "type: %s" % md["type"]
        print "is close to cluster %d with membership %f" % (u_avg.argmax(), u_avg.max())
        print "score vector: %s" % str(u_avg)
        uu.append(u_avg)
    print "\n============"
    uu = np.array(uu)
    return uu












