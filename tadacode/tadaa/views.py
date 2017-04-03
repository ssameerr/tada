
import os


from django.shortcuts import render
import models
import core


def home(request):
    import time
    pid = os.fork()
    if pid == 0:
        print "child will sleep"
        time.sleep(5)
        print "child is walking up"
        os._exit(0)
    else:
        return render(request, 'home.html')
    #return render(request, 'home.html')


def add_model(request):
    if request.method == 'GET':
        return render(request, 'add_model.html')
    elif request.method =='POST':
        error_msg = ''
        if 'url' not in request.POST:
            error_msg = 'url is not passed'
        if 'name' not in request.POST:
            error_msg = 'name is not passed'
        if error_msg != '':
            return render(request, 'add_model.html', {'error_msg': error_msg})
        pid = os.fork()
        if pid == 0:
           return render(request, 'add_model.html', {'message': 'model is under processing'})
        else:
            mlmodel = models.MLModel()
            mlmodel.name = request.POST['name']
            mlmodel.url = request.POST['url']
            mlmodel.save()
            core.explore(endpoint=mlmodel.url, model_id=mlmodel.id)
            os._exit(0) # to close the thread after finishing


