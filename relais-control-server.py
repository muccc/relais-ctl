import RPi.GPIO as GPIO
from time import sleep
import json

from flask_api import FlaskAPI
app = FlaskAPI(__name__)


# bcm pin numbers from http://pinout.xyz/pinout/pin11_gpio17
p = {
     'decke1' : {'out': 18, 'in': 22},
     'decke2' : {'out': 23, 'in': 10},
     'kueche' : {'out': 24, 'in': 11},
     'reserve': {'out': 25, 'in': 9}  # Pin 9 ist vermutlich defekt... Hab deswegen als Workaround 9 und 11 vertauscht --Andi
}


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup( [ i['out'] for i in p.values() ], GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup( [ i['in'] for i in p.values() ],  GPIO.IN,  pull_up_down=GPIO.PUD_UP)


@app.route("/toggle/<string:name>", methods = ['GET', 'POST'] )
def toggle(name):
  GPIO.output(p[name]['out'], GPIO.LOW)
  sleep(0.1)
  GPIO.output(p[name]['out'], GPIO.HIGH)
  return '%s (BCM pin %d) was toggled' % (name, p[name]['out'])

# returns True when state in ON and False when state is OFF
def is_on(name):
    return not GPIO.input(p[name]['in'])


@app.route("/relais/", methods = ['GET'] )
def index():
	return  { i: return_state(i) for i in p.keys() }

@app.route("/relais/<string:name>", methods = ['GET'] )
def return_state(name):
  return 'ON' if is_on(name) else 'OFF'

@app.route("/relais/<string:name>", methods = ['POST'] )
def switch_on(name):
  if not is_on(name):
     toggle(name)
  return return_state(name) 

@app.route("/relais/<string:name>", methods = ['DELETE'] )
def switch_off(name):
  if is_on(name):
     toggle(name)
  return return_state(name) 

def note_repr(key):
  print(key)
  return {
    'url': request.host_url.rstrip('/') + "relais/" + key, # url_for('switch_on', name=key),
    'text': key
  }

@app.route("/", methods=['GET'])
def notes_list():
	return [ {'text': k, 'url': '/'} for k in p.keys() ]
#  return [note_repr(i) for i in p.keys()]


@app.route("/sitemap")
def site_map():
    links = []
    out = ""
    for rule in app.url_map.iter_rules():
        try:
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
            out += '<li><a href="{0}">{1}</a> {2}</li>'.format(url, rule.endpoint, rule)
        #except BuildError:
        except:
            pass
    # links is now a list of url, endpoint tuples
    return "<h1>Relais Ctl</h1><ul>" + out + "</ul>"



if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)



