import serial 
from tkinter import * 
import threading 
import math
import csv


"""
HC - 06 연결
RXD - D12 연결
TXD - D11 연결

BT이름 : MECHA
"""
class User: 
    
    def __init__(self,name, gender, bodyStat, age): 
        self.entityList = list()
        self.age = age;
        
        self.userName = str(name)
        
        self.exerciseStat = bodyStat
        self.gender = gender
        self.bodyStat = bodyStat
        
        self.HBMax = 220 - self.age
        self.HBavailable = None
        self.HBRest = self.getHBRest()
        self.HBavailable = self.HBMax - self.HBRest

        self.trials  = 0

    def getHBRest(self): 
        self.maleHBList = [53, 59, 65, 69,73, 76, 88]
        self.femaleHBList = [58, 63, 67, 71, 75, 80, 85] 
        self.genderHBdict = [self.maleHBList, self.femaleHBList]
        
        
        return int(self.genderHBdict[self.gender][self.bodyStat])
                   
         
    
    def getFILENAME(self):
        return str(self.userName) + '.csv'

    
    def BPM_Algorithsm(self, other):
        self.ProcessingIQR(other)
        self.BPMthresold = [self.getThresold(0), self.getThresold(1),self.getThresold(2)]
        self.status = None 
        try: 
            
            if self.averageBPM < self.BPMthresold[0]:
                self.status =  "REST"
            elif self.averageBPM < self.BPMthresold[1]:
                self.status = 'FAT BURNING'
            elif self.averageBPM < self.BPMthresold[2]: 
                self.status = "CARIAC REINFORCE"
            elif self.averageBPM > self.BPMthresold[2]:
                self.status = 'MAX BEAT RATE'
  
        except: 
            return "입력값 오류"
        self.SavetheData()
        self.entityList.clear()
        return self.status 
        

    def ProcessingIQR(self,trial): 
        self.entityList.sort()

        self.Third_QuaterData = self.entityList[int(3/4*trial -1)] 
        self.A_QuaterData = self.entityList[int(1/4*trial-1)]

        self.IQR = abs(self.A_QuaterData - self.Third_QuaterData) 
        print(self.entityList)
        self.popTargetList = list()
        for i in range(len(self.entityList)): 
            print(i)
            if self.A_QuaterData - 1.5 * self.IQR < self.entityList[i] < self.Third_QuaterData + 1.5*self.IQR: 
                pass 
            else: 
                self.popTargetList.append(i)
        for i in self.popTargetList[::-1]: 
            self.entityList.pop(i)
        self.averageBPM = sum(self.entityList)/len(self.entityList)

        
        

    def getThresold(self, index): 
        self.percentageHB = [0.4, 0.65, 0.8]
        return (self.percentageHB[index]*self.HBavailable) + self.HBRest 
        
    def SavetheData(self): 
        if self.trials == 0: 
            self.FILE = open(self.getFILENAME(), 'w', encoding = 'utf-8') 
            self.writerOBJ = csv.writer(self.FILE)
            self.initialLine = ["trial " + str(x)  for x in range(len(self.entityList))]
            print(self.initialLine)
            self.initialLine.append("status")
            self.initialLine.append("average BPM")
            self.initialLine.append("age")
            self.initialLine.append("name")
            self.initialLine.append("sex")
            self.initialLine.append("MAX BPM")
            self.initialLine.append("REST BPM")
            self.initialLine.append("AVAILABLE BPM")
            self.writerOBJ.writerow(self.initialLine)
        else : 
            self.FILE = open(self.getFILENAME(), 'a', encoding = "utf-8") 
            self.writerOBJ = csv.writer(self.FILE)
        self.saveDATAList = [x for x in self.entityList]
        self.saveDATAList.append(self.status)
        self.saveDATAList.append(self.averageBPM) 
        self.saveDATAList.append(self.age)
        self.saveDATAList.append(self.userName) 
        self.saveDATAList.append(self.gender) 
        self.saveDATAList.append(self.HBMax)
        self.saveDATAList.append(self.HBRest) 
        self.saveDATAList.append(self.HBavailable)
      
        self.writerOBJ.writerow(self.saveDATAList)
        self.FILE.close()


class DemoPlay(User): 
    def __init__(self, name, gender, ex, age): 
        super().__init__(name, gender, ex, age)



class mainApp(): 
    ##초기화면 구성
    def __init__(self): 
        self.userList = []
        self.nowUserIndex = 0
        self.nowUserMax = 0
        self.arduino = None

        self.window = Tk()
        self.window.geometry('1000x410')
        self.window.resizable(False, False)
        self.semiWindow = 0

        self.img = PhotoImage(file = "heartRed.png")
        self.img2 = PhotoImage(file = "heartGreen.png")
        self.canvas = Canvas(self.window, width =300, height=300)
        self.realImg = self.canvas.create_image(150, 150, image = self.img)
        self.canvas.place(x = 50, y=30)

        
        self.NOWUSER = Label(text="등록 필요", font=("Arial", 40))
        self.BPM = Label(text="BPM : "+"NULL", font=("Helvetica", 40))
        self.STATUS = Label(text="STAT : NULL", font=("Helvetica", 40))
        self.NOWUSER.place(x=400,y=50)
        self.BPM.place(x =400,y=150)
        self.STATUS.place(x = 400, y=250)
        
        self.DEMOBTT = Button(self.window, text = "DEMOPLAY",  command = self.DemoPlay)
        self.DEMOBTT.place(x = 525 , y = 375)

        self.CNUBTT = Button(self.window, text = "새로운 유저 추가", command = self.CreateNewUser1) 
        self.CNUBTT.place(x = 400, y =350)
        self.SBCBTT = Button(self.window, text = "시리얼 통신 연결", command = self.SetSerialPortConnection)
        self.SBCBTT.place(x = 525, y= 350)
        self.CNGUSERBTT = Button(self.window, text = "유저 변경", command= self.ChangeUser1)
        self.CNGUSERBTT.place(x = 400, y = 375)

         #블루투스 자동 연결, 시도 후 연결 실패시 오프라인 모드-데모 버전 
        ##아두이노 통신 파트, 스레딩 부분이므로 건들지 말 것
        self.setThreading = Button(self.window, text = "스레딩 시작", command = self.setThreadingFNC) 
        self.setThreading.place(x = 650, y = 350)

        self.STPLSDBTT = Button(self.window, text = "스레딩 정지", command = self.setIsWorking)
        self.STPLSDBTT.place(x = 650, y = 375) 

        self.arduinoStatus = Label(self.window, text = "Arduino : connection required",font=("Arial", 10))
        self.arduinoStatus.place(x = 120, y=310)

        
        self.frame = LabelFrame(self.window , text ="Console", width= 370, height=50) 
        self.consoleLabel = Label(self.window, text = "PPT 주의사항 확인 바랍니다.", font=("Helvetica", 15))
        self.frame.place(x = 30,y = 340)

        self.consoleLabel.place(x=50, y =355)

        self.window.mainloop() 

##################################################################################################################

    def setThreadingFNC(self):
        tread =threading.Thread(target = self.ListenSerialData )
        tread.start()

    def ListenSerialData(self): 
        self.isWorking = True 
        self.tempSerialData = None
        self.trial = 0
        while self.isWorking:
            try: 
                self.arduino.write(b's')
                print(1)
                print(self.arduino.readable())
                
                #표시 부분
                self.tempSerialData = self.arduino.readline().decode()[:len(self.arduino.readline().decode())-2]
                     
                self.BPM.configure(text = "BPM : " + self.tempSerialData) 
            except serial.serialutil.SerialException: 
                self.printonTKconsole('오류가 발생했습니다.')
                self.setIsWorking()

            except AttributeError: 
                self.printonTKconsole("아두이노 연결을 먼저 하십시오")
                self.setIsWorking()
                break
            
            
            self.canvas.create_image(150, 150, image = self.img2)
            self.canvas.place(x = 50, y=30)
            try:
                self.userList[self.nowUserIndex].entityList.append(int(self.tempSerialData))
                self.trial += 1
                self.printonTKconsole('시행 : ' + str(self.trial))
            except: 
                self.printonTKconsole("심박센서 시작")
            
            
            if self.trial == 12 :
                             
               self.result = self.userList[self.nowUserIndex].BPM_Algorithsm(self.trial)
               self.STATUS.configure(text = self.result)
               self.trial = 0
            self.canvas.create_image(150, 150, image = self.img)
            self.canvas.place(x = 50, y=30)   
                
        ###여기까지 건들지 말것 

###################################################################################
    
        

    def printonTKconsole(self, string):
        #print(string)
        self.consoleLabel.configure(text = string)
           

    #스레딩 반복 중지. 
    def setIsWorking(self): 
        if self.isWorking == True: 
            self.isWorking = False
        elif self.isWorking == False: 
            self.printonTKconsole('이미 스레딩이 정지되었습니다.')
    

    def SetSerialPortConnection(self):
        try: 
            self.port ="COM6"
            self.baudrate = 115200
            self.arduino = serial.Serial(self.port, self.baudrate)
            self.printonTKconsole("set " + str(self.port) +" : ( baudrate : " + str(self.baudrate) + ")") 
            self.arduinoStatus.configure(text = "Arduino : CONNECTED")
        except serial.serialutil.SerialException: 
            self.printonTKconsole("연결 확인 혹은 접속됨")
        except FileNotFoundError: 
            self.printonTKconsole("포트 설정이 잘못됨")
    
        ###뒤에 시리즈로 번호가 붙은 경우 절대로 건들지 말 것 

     

    def DemoPlay(self): 
        
        self.DEMOUSER = DemoPlay("DEMOPLAY.csv", 0, 5, 20)
        self.DEMOFILE = open("DEMO.csv" , 'r', encoding = "utf-8")
        self.DEMOReader = list(csv.reader(self.DEMOFILE))
        
        self.k = self.DEMOReader[0][0:12]
        for i in self.k:
            self.DEMOUSER.entityList.append(int(i))
        self.DEMOUSER.userName = self.DEMOReader[0][15] 
        self.DEMOUSER.age = self.DEMOReader[0][14]      
    
        self.NOWUSER.configure(text = "DEMO PLAYER")
        
        self.STATUS.configure(text = self.DEMOUSER.BPM_Algorithsm(12))
        self.BPM.configure(text = "BPM : " + str(int(self.DEMOUSER.averageBPM)))

    def CreateNewUser1(self) :
        self.writeName = Toplevel()

        Label(self.writeName, text = "사용자 이름 입력").grid(row = 0, column = 0)
        Label(self.writeName, text = "사용자 나이 입력").grid(row = 1, column = 0)

        self.nameInput = Entry(self.writeName)
        self.ageInput = Entry(self.writeName) 

        self.nameInput.grid(row = 0, column = 1)
        self.ageInput.grid(row = 1, column = 1)
        
        self.genderVar = IntVar()
        self.maleRadioBTT = Radiobutton(self.writeName, text = 'male', value = 0, variable=self.genderVar)
        self.maleRadioBTT.grid(row = 3, column = 0)
        self.femaleRadioBTT = Radiobutton(self.writeName, text = 'female', value = 1, variable=self.genderVar)
        self.femaleRadioBTT.grid(row = 3, column = 1)
        

        self.excerIntValue = IntVar() 

        self.athlete = Radiobutton(self.writeName, text = '운동선수', value = 0, variable=self.excerIntValue)
        self.athlete.grid(row = 2, column = 0)

        self.highSuperb = Radiobutton(self.writeName, text = '뛰어남', value = 1, variable=self.excerIntValue)
        self.highSuperb.grid(row = 2, column = 1)

        self.lowSuperb = Radiobutton(self.writeName, text = '좋음', value = 2, variable=self.excerIntValue)
        self.lowSuperb.grid(row = 2, column = 2)

        self.overAverage = Radiobutton(self.writeName, text = '평균 이상', value = 3, variable=self.excerIntValue)
        self.overAverage.grid(row = 2, column = 3)

        self.average = Radiobutton(self.writeName, text = '평균', value = 4, variable=self.excerIntValue)
        self.average.grid(row = 2, column = 4)

        self.lessAverage = Radiobutton(self.writeName, text = '평균 이하', value = 5, variable=self.excerIntValue)
        self.lessAverage.grid(row = 2, column = 5)

        self.bad = Radiobutton(self.writeName, text = '나쁨', value = 6, variable=self.excerIntValue)
        self.bad.grid(row = 2, column = 6)
        

        self.writeButton = Button(self.writeName, text = "입력", command = self.CreateNewUser2)   
        self.writeButton.grid(row = 4, column = 0)
        

        self.writeName.mainloop() 
        

    def CreateNewUser2(self):
        if int(self.ageInput.get()) > 100: 
            self.printonTKconsole("100세 이하를 대상 프로그램입니다.")
            return 
        elif int(self.ageInput.get()) < 0: 
            self.printonTKconsole("나이는 음수가 될 수 없습니다.")
            return
        try: 
            self.userList.append(User(self.nameInput.get(), self.genderVar.get(), self.excerIntValue.get(), int(self.ageInput.get())))
            self.nowUserMax = len(self.userList) - 1
            self.nowUserIndex = self.nowUserMax
            self.printonTKconsole(self.userList[self.nowUserIndex].userName + " : 유저 번호 ["+str(self.nowUserIndex)+'] : 나이 :' + str(self.userList[self.nowUserIndex].age))
            self.NOWUSER.configure(text = "USER : " + str(self.nameInput.get()))
        except ValueError: 
            self.printonTKconsole("나이에는 숫자만 입력해야 합니다.")
         
    def ChangeUser1(self): 
        self.writeTargetUserNumber = Tk() 
        Label(self.writeTargetUserNumber, text = "변경할 사용자 이름 입력 : ").grid(row = 0 , column = 0)
        self.targetIndexInput = Entry(self.writeTargetUserNumber) 
        self.targetIndexInput.bind("<Return>", self.ChangeUser2)
        self.targetIndexInput.grid(row = 0, column = 1)
        
        self.writeTargetUserNumber.mainloop()

    def ChangeUser2(self,event): 

            self.tempInput = str(self.targetIndexInput.get())
            k = 0
            for i in self.userList:  
                print(i.userName == self.tempInput)
                if i.userName == self.tempInput : 
                    self.nowUserIndex = k
                else : 
                    k+=1
            print(self.userList[self.nowUserIndex].userName)
            self.NOWUSER.configure(text = "USER : " + str(self.userList[self.nowUserIndex].userName))
            self.printonTKconsole(self.userList[self.nowUserIndex].userName +"으로 변경되었습니다.")
        
            
        

k =mainApp()
