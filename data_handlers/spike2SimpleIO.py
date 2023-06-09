import neo
import pandas as pd
import numpy as np
import quantities as pq
class spike2SimpleReader():
    """
    This class loads simple smr files of the Cambridge Electronics Software
    Spike2. It wraps the neo library 1). The resulting data-structure is a list. Each entry 
    in the list represents a Spike2 Segment consisting only of Analog and Event channels. The 
    list entry is a tuple with two dictionaries. The first for analog singals the second for 
    events. Each dictionary uses the channel name as a key and the  data is stored in the value.

    Events only save in the data-value the times the event occured. Annalog data consists of the 
    time vector and the magnitude of the different analog channels. All data will be saved in 
    self.outPutData.

    1) Garcia S., Guarino D., Jaillet F., Jennings T.R., Pröpper R., Rautenberg P.L., Rodgers C., 
       Sobolev A.,Wachtler T., Yger P. and Davison A.P. (2014) Neo: an object model for handling 
       electrophysiology data in multiple formats. Frontiers in Neuroinformatics 8:10: doi:10.3389/fninf.2014.00010
       https://neo.readthedocs.io/en/stable/index.html

    """    
    def __init__(self,fileName):
        """This function initializes the class and awaits the position of the smr file. It 
        also  initialises all relevant variables for the object

        :param fileName: position of the smr-file to read
        :type fileName: string or path-string
        """        
        self.fileName      = fileName
        self.eventList     = list()
        self.analogSigList = list()
        self.neoReader     = False
        self.dataBlock     = False
        self.outPutData    = list()


    def readByNeo(self):
        """ This initialises the spike2-reader object of the neo class. The readers
        is working in lazy mode. Hence it can use up large amounts of memory.
        """        
        self.neoReader = neo.io.Spike2IO(filename=self.fileName)
        self.dataBlock = self.neoReader.read(lazy=False)[0]

    def readSegments(self):
        """ This function splits the data into segments. Sometimes smr files include
        multiple recordings at different times, such su divisions are called segments.
        The function than runs the single segment read function. and returns the data 
        to self.outPutData.
        """
        self.outPutData = list()
        for seg in self.dataBlock.segments:
            self.outPutData.append(self.readSingleSeg(seg))
        

    def readSingleSeg(self,seg):
        """ This function calls the event and analog signal readers and returns the
        data in form of a tuple, with [0] = analog singals and [1] = events.

        :param seg: segment object of the neo - reader class
        :type seg: segment object
        :return: segmentData 
        :rtype: tuple
        """        
        events     = self.readEvents(seg)
        analogSigs = self.readAnalogSignals(seg)
        return (analogSigs,events)
    
    def readEvents(self,seg):
        """ This reads all the event channels of a segment and returns their occurences as a dictionary.

        :param seg: segment object of the neo - reader class
        :type seg: segment object
        :return:  a dictionary in which the keys are the names of the event channels and the values the indices of their occurence
        :rtype:  dictionary
        """        
        eventData = dict()
        for event in seg.events:
            eventData[event.name] = event.times
        return eventData
  

    def readAnalogSignals(self,seg):
        """This function reads all analog signals and returns a dictionary. The first entry of the
        dictionary is the time signal. Than all channels are listed. The key is the name of the channel.
        The value is the magnitude of the channel.

        :param seg: segment object of the neo - reader class
        :type seg: segment object
        :return:  a dictionary in which the keys are the names of the analog signal channels and the values are their magnitudes
        :rtype:  dictionary
        """        
        analogData = dict()
        analogData['time_s']  = seg.analogsignals[0].times
        for aSignal in seg.analogsignals:
            analogData[aSignal.name] = aSignal.magnitude
        return analogData
    
    def main(self):
        """This is the main program. It initializes the reader and than
        reads the data.
        """        
        self.readByNeo()
        self.readSegments()

class segmentSaver():
    """ This class writes the CED data read by the spike2SimpleReader to a pandas object.
        The event channels are therefore changed into boolean arrays. NOTE! The event channel
        is not subject to the sample frequency of the analog signals. This is changed here and 
        the nearest sample point to the event is used for this event
    """    
    def __init__(self,spike2SimplerReaderobject,savePos):
        """ This function initializes the segment save class. It needs the reader object and the
        position to which it should save the data, e.g. /destinationFolder/fileName.ext . It will
        augment the save position so that the segments can be read, e.g. 

        /destinationFolder/fileName_1_3.ext 
        /destinationFolder/fileName_2_3.ext 
        /destinationFolder/fileName_3_3.ext 

        :param spike2SimplerReaderobject: the reader object
        :type spike2SimplerReaderobject: python object
        :param savePos: file position where to save the files
        :type savePos: str
        """        
        self.s2sr     = spike2SimplerReaderobject
        self.savePos  = savePos
    
    def main(self, save_mode = False):
        """This is the main function that will split the reader object
        into dataframes which hold the data of each segment. Optionally
        all segment-dataframes are returned in a list.

        :return: a list of dataframes for each segment
        :rtype: list of pandas dataframes
        """        
        segNum = len(self.s2sr.outPutData)
        dataframeList = list()
        c = 0
        for segment in self.s2sr.outPutData:
            #create data frame on the basis of the analogData
            df = self.analogSignalDict2Pandas(segment)
            # add events
            df = self.eventDict2Pandas(segment,df)
            #save to savePos
            if save_mode:
                df.to_csv(self.savePos[:-4]+f'_{c}_{segNum}'+self.savePos[-4::])
            c+=1
            dataframeList.append(df)
        return dataframeList


    def analogSignalDict2Pandas(self,segment):
        """ This function transforms the analog signals into one pandas dataframe. The time in seconds is
        the index of the dataframe. The analogsignals are different columns in it.

        :param segment: a tuple with the dictionaries for the analog signals and the event data
        :type segment: tuple
        :return: a pandas dataframe described as above
        :rtype: dataframe
        """        
        # get Dict
        aSigDict = segment[0]
        # rescale time to seconds
        aSigDict['time_s'] = aSigDict['time_s'].rescale(pq.s) 

        for channel in  list(aSigDict.keys()):
            aSigDict[channel] = np.array(aSigDict[channel]).flatten()
        
        df = pd.DataFrame(aSigDict)
        df.set_index('time_s', inplace=True)
        return df
    
    def eventDict2Pandas(self,segment,df):
        """This function adds the event data as boolean arrays to the dataframe

        :param segment: a tuple with the dictionaries for the analog signals and the event data
        :type segment: tuple
        :return: a pandas dataframe described in analogSignalDict2Pandas
        :rtype: dataframe
        :return: same dataframe with additional event channels
        :rtype: data frame
        """        
        # get Dict
        eventDict = segment[1]

        for channel in  list(eventDict.keys()):
            # rescale time to seconds
            times = eventDict[channel].rescale(pq.s) 
            times = np.array(times.flatten())
            df[channel] = self.events2boolSignal(df.index.to_numpy(),times)
        
        return df
    
    def events2boolSignal(self,indArray,events):
        """ This function maps the time stamp of the event channel on to the time samples
        of the analog channels and returns this information  as a boolean array.

        :param indArray: time index as numpy array
        :type indArray: numpy array
        :param events: times in seconds when the event occured 
        :type events: numpy array
        :return: a boolean array where the occurences are mapped to the closest time index.
        :rtype: numpy array dtype booleans
        """        
        boolArray = np.full(indArray.shape,False)
        for occurence in events:
            absDiff = np.abs(indArray-occurence)
            pos = absDiff.argmin()
            boolArray[pos] = True

        return boolArray