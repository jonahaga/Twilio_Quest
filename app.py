import os

from flask import Flask
from flask import Response
from flask import request
from flask import render_template
from twilio import twiml
from twilio.rest import TwilioRestClient

# Pull in configuration from system environment variables
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')

# create an authenticated client that can make requests to Twilio for your
# account.
client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Create a Flask web app
app = Flask(__name__)

# Render the home page
@app.route('/')
def index():
    return render_template('index.html')

# Handle a POST request to send a text message. This is called via ajax
# on our web page
@app.route('/message', methods=['POST'])
def message():
    # Send a text message to the number provided
    message = client.sms.messages.create(to=request.form['to'],
                                         from_=TWILIO_NUMBER,
                                         body='Good luck on your Twilio quest!')

    # Return a message indicating the text message is enroute
    return 'Message on the way!'

# Handle a POST request to make an outbound call. This is called via ajax
# on our web page
@app.route('/call', methods=['POST'])
def call():
    # Make an outbound call to the provided number from your Twilio number
    call = client.calls.create(to=request.form['to'], from_=TWILIO_NUMBER, 
                               url='http://twimlets.com/message?Message%5B0%5D=http://demo.kevinwhinnery.com/audio/zelda.mp3')

    # Return a message indicating the call is coming
    return 'Call inbound!'

@app.route('/sms', methods=['GET', 'POST'])
def sms():
    response = twiml.Response();
    response.message('hi! thanks for texting in!')
    return Response(str(response))

@app.route('/call', methods=['GET', 'POST'])
def inbound_call():
    response = twiml.Response();
    response.say('I just responded to a phone call. Huzzah!', voice='woman')
    # Gather digits.
    with response.gather(numDigits=1, action="/handle-key", method="POST") as g:
        g.say('Press 1 for more options, or press 0 to speak to Jona.')
 
    return str(response)

@app.route("/handle-key", methods=['GET', 'POST'])
def handle_key():
    # Handle key press from a user. 
    digit_pressed = request.values.get('Digits', None)
    if digit_pressed == "1":
        response = twiml.Response()
        response.say("Good job you pressed one. You are smart and beautiful.", voice='man')
 
        return str(response)
    
    # If the caller presses 0, it calls Jona
    elif digit_pressed == "0":
        response = twiml.Response()
        response.dial("+12102500227")
        # If call fails
        response.say("Sorry, Jona is not available. Goodbye.")

        return str(response)

    # If the caller pressed anything but 1 or 0, redirect them to the main menu.
    else:
        return redirect("/call")

# Generate TwiML instructions for an outbound call
@app.route('/hello')
def hello():
    response = twiml.Response()
    response.say('Hello there! You have successfully configured a web hook.')
    response.say('Good luck on your Twilio quest!', voice='woman')
    return Response(str(response), mimetype='text/xml')

if __name__ == '__main__':
    # Note that in production, you would want to disable debugging
    app.run(debug=True)