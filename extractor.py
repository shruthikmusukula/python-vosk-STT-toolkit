#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer, SetLogLevel

import datetime
import json
import os
import srt
import subprocess

MODEL_PATH = "data/model"
SAMPLE_RATE = 16000
WORDS_PER_LINE = 7

class VOSK_Extractor:
    def __init__(self, file, sampleRate=None, model=None):
        self.check_for_model()

        self.dataFile = file

        if sampleRate is None:
            self.sampleRate = SAMPLE_RATE
        else:
            self.sampleRate = sampleRate

        if model is None:
            self.model = Model(MODEL_PATH)
        else:
            self.model = Model(model)

        self.output = ""

        # VOSK General Model Setup
        SetLogLevel(0)
        self.rec = KaldiRecognizer(self.model, self.sampleRate)
        self.rec.SetWords(True)

        # Initialize SRT Variables
        self.results = []
        self.subs = []

    def check_for_model(self):
        if not os.path.exists("data/model"):
            print(
                "Please download a valid model from https://alphacephei.com/vosk/models and "
                "unpack as 'any_name' in your working directory. This is the training model "
                "needed to work with the VOSK API.")
            exit(1)

    def initialize_process(self):
        self.process = subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-i', self.dataFile, '-ar',
                                    str(self.sampleRate) , '-ac', '1', '-f', 's16le', '-'],
                                    stdout=subprocess.PIPE)

    def prepare_result(self):
        # Load string into JSON format and extract resulting text
        output = json.loads(self.output)
        print("Result from [" + self.dataFile + "]: " + output["text"] + "\n")

    def process_input_file(self):
        # Call to initialize subprocess with VOSK API
        self.initialize_process()

        # Preprocessing of detected speech
        while True:
            data = self.process.stdout.read(4000)
            if len(data) == 0:
                break
            if self.rec.AcceptWaveform(data):
                self.results.append(self.rec.Result())

        # Save extracted output
        self.output = self.rec.FinalResult()

        # Add extracted text to results
        self.results.append(self.output)

        # Call to prepare result
        self.prepare_result()

    def built_srt(self):
        # Build SRT File content
        for i, res in enumerate(self.results):
            jres = json.loads(res)
            if not 'result' in jres:
                continue
            words = jres['result']
            for j in range(0, len(words), WORDS_PER_LINE):
                line = words[j: j + WORDS_PER_LINE]
                s = srt.Subtitle(index=len(self.subs),
                                 content=" ".join([l['word'] for l in line]),
                                 start=datetime.timedelta(seconds=line[0]['start']),
                                 end=datetime.timedelta(seconds=line[-1]['end']))
                self.subs.append(s)
        print(srt.compose(self.subs))

# Lone Executable Command (If Main Was In Here): python3 extractor.py data/test.mp4
