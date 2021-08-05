import sys

from extractor import VOSK_Extractor
from wer import WER_Engine

def runExtractor(input_file):
    # Initialize Extractor Object
    extractor = VOSK_Extractor(input_file)

    # Call on VOSK STT API and print resulting text to console
    extractor.process_input_file()

    # Construct and write to an outputted srt file
    extractor.built_srt()

    # Embed subtitles into video and save output file
    extractor.embed_subtitles()

def runWER_Engine():
    # Compare reference and hypothesis text inputs
    reference = "data/input.txt"
    hypothesis = "output/output.txt"
    with open(reference, 'r', encoding="utf8") as ref:
        r = ref.read().split()
    with open(hypothesis, 'r', encoding="utf8") as hyp:
        h = hyp.read().split()
    WER = WER_Engine()
    WER.wer(r, h)

if __name__ == "__main__":
    runExtractor(sys.argv[1])
    runWER_Engine()

# Lone Executable Command: python3 extractor.py data/input.mp4
