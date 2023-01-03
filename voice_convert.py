import speech_recognition as sr
from os import path
from pydub import AudioSegment
from paho.mqtt import client as mqtt_client
import base64
import pyogg

broker = "8.219.195.118"
port = 1883
topic = "broker1/voice"
topci2 = "broker1"


def ogg2wav(ofn):
    wfn = ofn.replace(".ogg", ".wav")
    x = AudioSegment.from_file(ofn)
    x.export(wfn, format="wav")


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


# suscribe to topic
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        json = msg.payload.decode()
        # convert json to dict
        dict = eval(json)
        # get the value of the key 'mediaData'
        mediaData = dict["mediaData"]
        # print(mediaData["data"])

        # decode the base64 to ogg
        ogg = base64.b64decode(mediaData["data"])
        # write the ogg to file with pyogg
        with open("convert.ogg", "wb") as f:
            f.write(ogg)
        # convert the ogg to wav
        ogg2wav("convert.ogg")
        # use the speech_recognition to recognize the wav
        AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "convert.wav")
        r = sr.Recognizer()
        with sr.AudioFile(AUDIO_FILE) as source:
            audio = r.record(source)
        theText = r.recognize_google(audio, language="id-ID")
        # print(theText)

        # change msg to dict
        msg = eval(msg.payload.decode())
        # delete mediaData
        del msg["msg"]
        # add theText to msg
        msg["msg"] = theText
        # convert dict to json_string
        print(msg)
        json_string = str(msg)
        json_string = json_string.replace("'", '"')
        # publish the json_string to topic2
        client.publish(topci2, json_string)

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == "__main__":
    run()
