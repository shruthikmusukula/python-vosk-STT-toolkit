import sys

from extractor import VOSK_Extractor

if __name__ == "__main__":
    # Initialize Extractor Object
    extractor = VOSK_Extractor(sys.argv[1])

    # Call on VOSK STT API and print resulting text to console
    extractor.process_input_file()

    extractor.built_srt()