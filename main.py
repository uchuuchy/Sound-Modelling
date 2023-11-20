from CleanUp import CleanUp
from WaveManip import WaveManip


def get_input():
    file = input("Path to file: ")
    if str(file.split(".",1)[1].upper()) == "MP3":
        return file
    elif str(file.split(".",1)[1].upper()) == "WAV":
        return file
    else:
        print("File format not supported.")
        quit()


def main():
    stream = get_input()
    print(stream)
    stream = CleanUp(stream).convert()
    WaveManip(stream).wavePlot()


if __name__ == '__main__':
    main()
