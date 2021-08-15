import csv
import numpy as np
import pandas as pd


class Report:

    def __init__(self, employeeIdentity, licensePlateNumber, date, odometerRead, parkingLocation):
        self.employeeIdentity = employeeIdentity
        self.licensePlateNumber = licensePlateNumber
        self.date = date  # done
        self.odometerRead = odometerRead
        self.parkingLocation = parkingLocation  # done

    def parseReportToCSV(self):
        pass
