import csv
from typing import Iterable

from .unpackUtils import newMotorsList, listDirectory
from os import stat

class Loader:
    
    modelCsv = None
    def __init__(self, motor, speed):
        self.motor = motor
        self.speed = str(speed)
        self.modelCsv = self.getModelCsv()
        pass

    @staticmethod
    def mapToNominal(freq):
        nomFreq = [50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000]
        distance = [(freq - i)**2 for i in nomFreq]
        index_min = distance.index(min(distance))

        return nomFreq[index_min]

    @staticmethod
    def allMotors(speed, inLineSpeed=False, inLineAG=False):
        iterableLoaderInstance = iterableLoader(speed)
        motorsRowsArray = []
        for model in newMotorsList():
            iterableLoaderInstance.motor = model
            iterableLoaderInstance.modelCsv = iterableLoaderInstance.getModelCsv()
            motorsRowsArray += iterableLoaderInstance.modelRowsArray(inLineSpeed=inLineSpeed, inLineAG=inLineAG)
            
        return motorsRowsArray

    def getModelCsv(self):
        csvFile = open(f'HeidmannDataHandler/models/{self.motor}/{self.motor}-{str(self.speed)}sp.csv').readlines()
        modelCsv = csv.reader(csvFile)
        return modelCsv 

    def modelRowsArray(self, inLineSpeed=False, inLineAG=False):
        
        rowsArray = list()
        for row in self.modelCsv:
            if row[0] == '':
                continue
            if row[0].startswith('Ang'):
                " TODO: Implement regex logic to now if a name is a str but with wrong typo"
                " TODO: Implement logic on the caller function, to jump this model in case of exception."
                
                angle = row[0]
                if not inLineAG:
                    rowsArray.append(row)
                continue

            tmp = list()
            if inLineSpeed:
                tmp.append(int(self.speed))
            if inLineAG:
                tmp.append(int(angle[3:]))
            aux = [float(i) for i in row]
            aux[0] = self.mapToNominal(aux[0])
            tmp += aux
            rowsArray.append(tmp)

        return rowsArray

    def buildMatrix(self):
        
        rowsArray = self.modelRowsArray()
        # Initialize the lists 
        frequencies = list()
        angles = list()
        matrix = list()

        first = True # Its the first time that the program pass by a angle set
        for i in range(len(rowsArray) - 1):

            if type(rowsArray[i][0]) is str: # If the pointer is on a "Angle XX"

                first2 = False # Tells the program that he's not in the first angle set
                if first: # If it is the first time that it pass by a angle set
                    first2 = True # Says that actually it is the first angle set
                    first = False # From now on, it will be not the first time it passes by a angle set
                j = 0 # index for iterating by the matrix, reset on each pass by a "Angle XX"
                angles.append(int(rowsArray[i][0][3:])) # Add the angle to the angle list

            else: # If the ponter is on a Frequencie:Data pair
                # If it is the first angle set, initialize the rows of the matrix 
                if first2: 
                    matrix.append([])
                # Add the frequencies to the frequencies list and the data to the new column on the matrix 
                frequencies.append(rowsArray[i][0])
                matrix[j].append(rowsArray[i][1]) 

                j += 1

        return matrix, frequencies, angles


class MotorsParameters:
    paramsDict = dict()
    Fanid = list()
    # Transform the paramsDict in a params.json file or a class (easy to change)
    paramsDict = {
        "TotalPressure": [1.5, 1.5, 1.6, 1.5, 1.4, 1.6, 1.2, 1.2],
        "MassFlow":      [430, 430, 415, 396, 396, 385, 396, 403],
        "MT":            [1.04, 1.04, 1.39, 0.99, 0.99, 0.89, 0.67, 0.63],
        "MTd":           [1.2, 1.2, 1.52, 1.12, 1.12, 1.14, 0.88, 0.87],
        "V":             [90, 60, 60, 112, 112, 88, 50, 11],
        "B":             [40, 26, 26, 53,  53, 36, 42, 15],
        "BPF":           [2420, 1570, 2250, 3120, 3120, 2180, 1670, 556],
        "Cutoff":        [0.83, 0.8, 0, 0.89, 0.89, 0.68, 3.53, 2.38],
        "RSS":           [200, 200, 200, 367, 367, 227, 400, 200]
        }

    Fanid =['FanA','FanB','FanC','FanQF-1','FanQF-3','FanQF-5','FanQF-6','FanQF-9']

    def __init__(self, motor = None):
        if motor:
            return self.singleMotor(motor)
        pass

    @staticmethod
    def motorsParametersdict():
        MotorsParameters.motorsParameters = dict()
        for motor in MotorsParameters.Fanid:
            MotorsParameters.motorsParameters[motor] = MotorsParameters.singleMotor(motor)
        return MotorsParameters.motorsParameters

    @staticmethod
    def singleMotor(motor):
        motorParam = dict()
        for param, values in MotorsParameters.paramsDict.items():
            motorParam[param] = values[MotorsParameters.Fanid.index(motor)]
        return motorParam


class iterableLoader(Loader):
    def __init__(self, speed):
        if speed: 
            self.speed = str(speed)
        else:
            raise Exception("speed parameter not informed")
