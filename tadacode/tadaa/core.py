from functools import partial
import numpy as np
import pandas as pd
import traceback

import easysparql
import data_extraction
import learning

from models import MLModel, PredictionRun


def explore_and_train(endpoint=None, model_id=None):
    if endpoint is None:
        print "explore_and_train> endpoint is None"
        return
    if model_id is None:
        print "explore_and_train> model_id should not be None"
        return
    try:
        update_progress_func = partial(update_model_progress_for_partial, model_id)
        update_model_state(model_id=model_id, new_state=MLModel.RUNNING, new_progress=0,
                           new_notes="Extracting numerical class/property combinations")
        # Safe function
        classes_properties_uris = easysparql.get_all_classes_properties_numerical(endpoint=endpoint)
        update_model_state(model_id=model_id, new_progress=0,
                           new_notes="extracting values from gathered class/property")
        data, meta_data = data_extraction.data_and_meta_from_class_property_uris(
            class_property_uris=classes_properties_uris, update_func=update_progress_func)
        update_model_state(model_id=model_id, new_progress=0, new_notes="training the model")
        if np.any(np.isnan(data)):
            print "explore_and_train> there is a nan in the data"
            print "**************************"
        else:
            print "explore_and_train> no nans in the data"
        model = learning.train_with_data_and_meta(data=data, meta_data=meta_data, update_func=update_progress_func)
        update_model_state(model_id=model_id, new_progress=0, new_notes="organizing the clusters")
        meta_with_clusters = learning.get_cluster_for_meta(training_meta=meta_data, testing_meta=meta_data,
                                                           update_func=update_progress_func)
        # Now I'm not using the computed data here
        # update_model_state(model_id=model_id, new_progress=0, new_notes="computing the score of the trained model")
        # learning.test_with_data_and_meta(model=model, data=data, meta_data=meta_with_clusters,
        #                                  update_func=update_progress_func)
        update_model_state(model_id=model_id, new_progress=0, new_notes="Saving the model data")
        model_file_name = data_extraction.save_model(model=model, meta_data=meta_data, file_name=str(model_id) + " - ")
        if model_file_name is not None:
            m = MLModel.objects.filter(id=model_id)
            if len(m) == 1:
                m = m[0]
                m.file_name = model_file_name
                m.save()
                update_model_state(model_id=model_id, new_progress=100, new_state=MLModel.COMPLETE, new_notes="Completed")
            else:
                update_model_state(model_id=model_id, new_progress=0, new_state=MLModel.STOPPED, new_notes="model is deleted")
        else:
            update_model_state(model_id=model_id, new_progress=0, new_state=MLModel.STOPPED, new_notes="Error Saving the model")
    except Exception as e:
        print "explore_and_train> Exception %s" % str(e)
        traceback.print_exc()
        update_model_state(model_id=model_id, new_state=MLModel.STOPPED, new_notes="Not captured error: " + str(e))


def predict_files(predictionrun_id=None, files=[]):
    update_progress_func = partial(update_predictionrun_progress_for_partial, predictionrun_id)
    update_predictionrun_state(predictionrun_id=predictionrun_id, new_progress=0, new_state=PredictionRun.RUNNING)
    num_of_files = len(files)
    for idx, fname in enumerate(files):
        update_predictionrun_state(predictionrun_id=predictionrun_id, new_progress= int(idx*1.0/num_of_files * 100),
                                   new_notes='predicting columns in file: '+fname.split('/').strip()[:-4])
        data, meta_data = data_extraction.data_and_meta_from_a_mixed_file(file_name=fname)

        predictionrun = PredictionRun.objects.filter(id=predictionrun_id)
        if len(predictionrun) == 1:
            predictionrun = predictionrun[0]
            predictionrun.add_memberships()
    update_predictionrun_state(predictionrun_id=predictionrun_id, new_progress=100, new_state=PredictionRun.COMPLETE)


####################################################################
#                State update functions                            #
####################################################################


def update_model_progress_for_partial(model_id, new_progress):
    return update_model_state(model_id=model_id, new_progress=new_progress)


def update_model_state(model_id=None, new_state=None, new_notes=None, new_progress=None):
    m = MLModel.objects.filter(id=model_id)
    if len(m) == 1:
        m = m[0]
        if new_state is not None:
            m.state = new_state
        if new_notes is not None:
            m.notes = new_notes
        if new_progress is not None:
            m.progress = new_progress
        m.save()
        return m
    return None


def update_predictionrun_progress_for_partial(predictionrun_id, new_progress):
    return update_predictionrun_state(predictionrun_id=predictionrun_id, new_progress=new_progress)


def update_predictionrun_state(predictionrun_id=None, new_state=None, new_notes=None, new_progress=None):
    m = PredictionRun.objects.filter(id=predictionrun_id)
    if len(m) == 1:
        m = m[0]
        if new_state is not None:
            m.state = new_state
        if new_notes is not None:
            m.notes = new_notes
        if new_progress is not None:
            m.progress = new_progress
        m.save()
        return m
    return None
