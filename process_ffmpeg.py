#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer, SetLogLevel
import sys
import os
import json
import subprocess

SAMPLE_RATE = 16000

class VOSK_Extractor:
    def __init__(self, file, sampleRate=None, model=None):
        self.dataFile = file

        if sampleRate is None:
            self.sampleRate = SAMPLE_RATE
        else:
            self.sampleRate = sampleRate

        if model is None:
            self.model = Model("data/model")
        else:
            self.model = Model(model)

        # VOSK Model Setup
        SetLogLevel(0)
        self.check_for_model()
        self.rec = KaldiRecognizer(self.model, self.sampleRate)

    def check_for_model(self):
        if not os.path.exists("data/model"):
            print(
                "Please download the model from https://alphacephei.com/vosk/models and unpack as 'test_name' in your working directory."
                "This is the training model needed to work with the VOSK API.")
            exit(1)

    def process_ffmpeg(self):
        process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i', self.dataFile, '-ar',
                                    str(self.sampleRate) , '-ac', '1', '-f', 's16le', '-'],
                                    stdout=subprocess.PIPE)
        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            if self.rec.AcceptWaveform(data):
                self.rec.Result()
                # print(self.rec.Result())
            # else:
            #     print(self.rec.PartialResult())

    def prepare_result(self):
        # Load string into JSON format and extract resulting text
        result = json.loads(self.rec.FinalResult())
        print("Result from [" + self.dataFile + "]: " + result["text"])



if __name__ == "__main__":
    extractor = VOSK_Extractor(sys.argv[1])
    extractor.process_ffmpeg()
    extractor.prepare_result()

# Executable Command: python3 process_ffmpeg.py data/test.mp4
