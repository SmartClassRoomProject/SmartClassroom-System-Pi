from flask import request, jsonify


def get_id(request):
      try :
            return int(request.form['ID'])
      except :
            return None

def param_needed():
      res = {
            'description' : 'param needed'
      }
      return jsonify(res) , 400

def param_check(request,param_list):
      for r in param_list :
            if r not in request.form :
                  return True

      return False # mean not not match
