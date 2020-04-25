from flask import Flask,request,render_template
import os
import string as st
import requests
import json
import datetime
import random

app = Flask(__name__)
secret = ""  #your google recaptcha secret key

def generateInstallID(stringLength):
   letters = st.ascii_letters + st.digits
   return ''.join(random.choice(letters) for i in range(stringLength))

def refer(referrer):
   install_id = generateInstallID(11)
   body = {"key": "{}=".format(generateInstallID(42)),
           "install_id": install_id,
           "fcm_token": "{}:APA91b{}".format(install_id, generateInstallID(134)),
           "referrer": referrer,
           "warp_enabled": True,
           "tos": datetime.datetime.now().isoformat()[:-3] + "+07:00",
           "type": "Android",
           "locale": "en-IN"}

   bodyString = json.dumps(body)

   headers = {'Content-Type': 'application/json; charset=UTF-8',
              'Host': 'api.cloudflareclient.com',
              'Connection': 'Keep-Alive',
              'Accept-Encoding': 'gzip',
              'User-Agent': 'okhttp/3.12.1'
              }

   r = requests.post('https://api.cloudflareclient.com/v0a745/reg', data=bodyString, headers=headers)
   return r

def startRefer(ref):
   retryTimes = 3
   for i in range(int(3)):
      result = refer(ref)
      if result.status_code == 200:
         ''' OK '''
         print('Crediting Data ...')
      else:
         print(i + 1, "Error")
         for r in range(retryTimes):
            retry = refer(ref)
            if retry.status_code == 200:
               print(i + 1, "Retry #" + str(r + 1), "OK")
               break
            else:
               print(i + 1, "Retry #" + str(r + 1), "Error")
               if r == retryTimes - 1:
                  break

def validaterecaptcha(token):
   data = {"secret" : secret,"response":token}
   r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
   return r


@app.route('/')
def hello_name():
   return render_template('index.html')


@app.route('/send-warp-data',methods=['POST'])
def getwrap():

    try:
        ref = request.form['config']
        token = request.form['token']

        if ref is not None and token is not None:
          ret = validaterecaptcha(token)
          # print(ret.json())
          if ret.status_code==200:#and ret.json()['hostname']=='127.0.0.1'
             if ret.json()['success']==True :
                startRefer(ref)
                data = {'status':200,'msg':'Success! Credited your account with 2GB.'}
                return json.dumps(data)
             elif ret.json()['success']==False and 'error-codes' in ret.json() and "timeout-or-duplicate" in str(ret.json()['error-codes']):
                data = {'status':204,'msg':'Hold on, the captcha has expired,refresh the page and try again.'}
                return json.dumps(data)
             else:
                data = {'status':206,'msg':'Internal error.Try Again!'}
                return json.dumps(data) 
          else:
             data = {'status': 208, 'msg': 'Captcha service unavailable.Check your internet connection.'}
             return json.dumps(data)
        else:
          data = {'status':404,'msg':'Invalid access.'}
          return json.dumps(data)
    except Exception as ex:
        print("Exception : ",str(ex))
        data = {'status':400,'msg':'Internal Exception thrown!'}
        return json.dumps(data)


if __name__ == '__main__':
   #app.run(host='0.0.0.0', port=os.getenv('PORT'),debug=True)
   app.run(debug=False)